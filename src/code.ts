import { FeatureExtractor } from "./services/FeatureExtractor";
import { ApiService } from "./services/ApiService";
import { UiService } from "./services/UiService";
import { FeedbackResult } from "./types";

// Show UI when the plugin starts
UiService.showUI();

// Function to track text changes in instances
async function trackInstanceTextChanges() {
    await figma.loadAllPagesAsync(); // Load all pages to avoid incremental mode errors

    figma.on('documentchange', (event) => {
        event.documentChanges.forEach(change => {
            if (change.type === 'PROPERTY_CHANGE' && change.node.type === 'TEXT') {
                const textNode = change.node as TextNode; // Explicitly cast to TextNode
                console.log(`Text changed in an instance: ${textNode.characters}`);
                figma.ui.postMessage({
                    type: 'INSTANCE_TEXT_UPDATE',
                    id: textNode.id,
                    text: textNode.characters
                });
            }
        });
    });
}


interface Modification {
    node_id: string;
    property: string;
    value: any;
    heuristic?: string;
    reason?: string;
}

interface ModifiedDesign {
    original: string;
    modified: string;
    modifications: Modification[];
}

// Track modified designs
const modifiedDesigns = new Map<string, ModifiedDesign>();

async function getModifiedDesign(frame: FrameNode): Promise<void> {
    try {
        const designData = await FeatureExtractor.extractForAI(frame);
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);

        const response = await fetch("http://localhost:3000/modify-design", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                design_json: designData,
                screenshot: `data:image/png;base64,${imageBase64}`
            }),
        });

        const result = await response.json();
        
        // Store both the modifications and full modified design
        modifiedDesigns.set(frame.id, {
            original: `data:image/png;base64,${imageBase64}`,
            modified: result.modified_design,  // Now contains full design JSON
            modifications: result.modifications
        });

        figma.ui.postMessage({
            type: 'design-modified',
            frameId: frame.id,
            original: `data:image/png;base64,${imageBase64}`,
            modifiedDesign: result.modified_design,  // Send full design to UI
            modifications: result.modifications,
            summary: result.summary
        });

    } catch (error) {
        console.error("Modification error:", error);
        figma.notify(`Failed to generate modified design: ${error instanceof Error ? error.message : String(error)}`);
    }
}

async function applyModifications(original: FrameNode, modifications: Modification[]): Promise<FrameNode> {
    const modified = original.clone();
    
    // Validate modifications before applying
    const validModifications = modifications.filter(mod => 
        mod.node_id && 
        mod.property && 
        mod.value !== undefined &&
        mod.value !== null
    );

    if (validModifications.length !== modifications.length) {
        console.warn(`Filtered out ${modifications.length - validModifications.length} invalid modifications`);
    }

    for (const mod of validModifications) {
        try {
            const node = modified.findOne(n => n.id === mod.node_id);
            if (!node) {
                console.warn(`Node ${mod.node_id} not found`);
                continue;
            }

            // Apply modification...
        } catch (e) {
            console.warn(`Failed to apply modification to ${mod.node_id}:`, e);
        }
    }
    
    return modified;
}
function hexToRgb(hex: string): { r: number, g: number, b: number } {
    hex = hex.replace('#', '');
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    return { r, g, b };
}
// Update the applyModifications function

trackInstanceTextChanges();
// const modifiedFrames = new Map<string, FrameNode>();
const modifiedFrames = new Map<string, {original: string, modified: string, modifications: any[]}>();
figma.ui.onmessage = async (msg) => {
    if (msg.type !== 'start-detection') return;
    
    const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];
    const frame = figma.currentPage.children.find(node => node.type === "FRAME") as FrameNode;
    await getModifiedDesign(frame);
    if (frames.length === 0) {
        figma.notify('No frames found on the current page.');
        return;
    }

    const allFeedback: any[] = [];

    for (const frame of frames) {
        if (!frame.visible) continue;

        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);
        const imageDataUrl = `data:image/png;base64,${imageBase64}`;

        const serializedNodes = FeatureExtractor.extractElements(frame);
        const user_name = figma.currentUser?.name ?? "Unknown User";
        const design_name = figma.root.name ?? "Untitled Design";
        

        try {
            const result = await ApiService.sendToBackend({
                user_name,
                design_name,
                frame: {
                    frameName: frame.name,
                    screen_width: frame.width,
                    screen_height: frame.height
                },
                elements: (await serializedNodes).map(node => {
                    const { imageBase64, ...rest } = node;
                    return imageBase64 ? { ...rest, imageBase64 } : rest;
                })
            }) as FeedbackResult;
        
            console.log("API Response:", result); 
            const recognitionFeedback = Array.isArray(result.recognition_results) 
            ? result.recognition_results.map(r => ({
                element_id: r?.element_id ?? "Unknown ID",
                element_name: r?.element_name ?? "Unknown Element",
                feedback: Array.isArray(r?.Feedback) ? r.Feedback.join(", ") : "No recognition feedback"
              }))
            : [];

            if (result && result.error_prevention_results) {
                allFeedback.push({
                    frameName: frame.name,
                    errorPreventionFeedback: result.error_prevention_results.Feedback ?? "No feedback",
                    errorHandlingFeedback: result.error_handling_results?.Feedback ?? "No feedback",
                    minimalistFeedback: result.minimalist_results?.Feedback ?? "No feedback",
                    consistencyFeedback: result.consistency_results?.Feedback ?? "No feedback",
                    recognitionFeedback,
                    screenshot: imageDataUrl
                });
                console.log("Sending to UI:", JSON.stringify(allFeedback, null, 2));

            } else {
                console.warn("Missing expected fields in API response.");
            }
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify(`Failed to send elements from ${frame.name} to backend.`);
        }
        

    if (allFeedback.length > 0) {
        UiService.sendFeedbackToUI(allFeedback);
    }

else if (msg.type === 'show-modified-design') {
    try {
        const frameId = msg.frameId;
        const frame = figma.getNodeById(frameId) as FrameNode;
        
        if (!frame || frame.type !== 'FRAME') {
            throw new Error("Original frame not found");
        }

        // Check if we already modified this frame
        if (modifiedFrames.has(frameId)) {
            const { original, modified, modifications } = modifiedFrames.get(frameId)!;
            figma.ui.postMessage({
                type: 'design-modified',
                frameId: frameId,
                original: original,
                modified: modified,
                modifications: modifications
            });
            return;
        }

        // Process new modification
        const designData = await FeatureExtractor.extractForAI(frame);
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);

        const response = await fetch("http://localhost:3000/modify-design", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                design_json: designData,
                screenshot: `data:image/png;base64,${imageBase64}`
            }),
        });

        if (!response.ok) throw new Error(await response.text());

        const result = await response.json();
        const modifiedFrame = await applyModifications(frame, result.modifications);
        
        const modifiedBytes = await modifiedFrame.exportAsync({ format: "PNG" });
        const modifiedBase64 = figma.base64Encode(modifiedBytes);

        // Store modified design
        modifiedFrames.set(frameId, {
            original: `data:image/png;base64,${imageBase64}`,
            modified: `data:image/png;base64,${modifiedBase64}`,
            modifications: result.modifications
        });

        figma.ui.postMessage({
            type: 'design-modified',
            frameId: frameId,
            original: `data:image/png;base64,${imageBase64}`,
            modifiedDesign: result.modified_design,
            modifications: result.modifications,
            status: result.status || "success"
        });

        // Cleanup
        modifiedFrame.remove();

    } catch (error) {
        console.error("Modification error:", error);
        figma.notify(`Failed to show modified design: ${error instanceof Error ? error.message : String(error)}`);
    }

}}}
