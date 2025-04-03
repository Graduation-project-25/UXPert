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



// async function getModifiedDesign(frame: FrameNode) {
//     try {
//         const elements = await FeatureExtractor.extractForAI(frame);
//         const imageBytes = await frame.exportAsync({ format: "PNG" });
//         const imageBase64 = figma.base64Encode(imageBytes);
        
//         const response = await fetch("http://localhost:3000/modify-design", {
//             method: "POST",
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 screenshot: `data:image/png;base64,${imageBase64}`,
//                 elements
//             }),
//         });
        
//         const result = await response.json();
        
//         if (result.error) {
//             throw new Error(result.error);
//         }

//         // Show modified image
//         figma.ui.postMessage({
//             type: 'design-modified',
//             original: `data:image/png;base64,${imageBase64}`,
//             modified: result.modified_image,
//             instructions: result.instructions || ["No specific instructions provided"]
//         });
        
//     } catch (error) {
//         console.error("Design modification failed:", error);
//         figma.notify(`AI modification failed: ${error instanceof Error ? error.message : String(error)}`);
//     }
// }
// In your code.ts
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
        console.log(`Generating modified design for frame ${frame.id}`);
        
        // 1. Extract design data
        const designData = await FeatureExtractor.extractForAI(frame);
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);

        // 2. Call modification endpoint
        const response = await fetch("http://localhost:3000/modify-design", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                design_json: designData,
                screenshot: `data:image/png;base64,${imageBase64}`
            }),
        });

        if (!response.ok) throw new Error(await response.text());

        // 3. Get modifications from backend
        const result = await response.json();
        if (!result.modifications) {
            throw new Error("No modifications received from server");
        }

        // 4. Apply modifications
        const modifiedFrame = await applyModifications(frame, result.modifications);
        
        // 5. Export modified design
        const modifiedBytes = await modifiedFrame.exportAsync({ format: "PNG" });
        const modifiedBase64 = figma.base64Encode(modifiedBytes);

        // 6. Store modified design
        modifiedDesigns.set(frame.id, {
            original: `data:image/png;base64,${imageBase64}`,
            modified: `data:image/png;base64,${modifiedBase64}`,
            modifications: result.modifications
        });

        // 7. Send to UI
        figma.ui.postMessage({
            type: 'design-modified',
            frameId: frame.id,
            original: `data:image/png;base64,${imageBase64}`,
            modified: `data:image/png;base64,${modifiedBase64}`,
            modifications: result.modifications
        });

        // 8. Cleanup
        modifiedFrame.remove();

    } catch (error) {
        console.error("Modification error:", error);
        figma.notify(`Failed to generate modified design: ${error instanceof Error ? error.message : String(error)}`);
        figma.ui.postMessage({
            type: 'modification-error',
            error: error instanceof Error ? error.message : String(error)
        });
    }
}

async function applyModifications(original: FrameNode, modifications: Modification[]): Promise<FrameNode> {
    const modified = original.clone();
    
    for (const mod of modifications) {
        try {
            const node = modified.findOne(n => n.id === mod.node_id);
            if (!node) {
                console.warn(`Node ${mod.node_id} not found`);
                continue;
            }

            switch (mod.property.toLowerCase()) {
                case 'color':
                    if ('fills' in node) {
                        const rgb = hexToRgb(mod.value);
                        (node as RectangleNode).fills = [{ 
                            type: 'SOLID', 
                            color: rgb 
                        }];
                    }
                    break;
                    
                case 'text':
                    if ('characters' in node) {
                        const textNode = node as TextNode;
                        if (textNode.fontName !== figma.mixed) {
                            await figma.loadFontAsync(textNode.fontName);
                        }
                        textNode.characters = mod.value;
                    }
                    break;
                    
                // Add other modification cases as needed
            }
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
// In code.ts, update the message handling
figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];
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
            
                if (result && result.error_prevention_results) {
                    allFeedback.push({
                        frameId: frame.id,  // Make sure to include frameId
                        frameName: frame.name,
                        errorPreventionFeedback: result.error_prevention_results.Feedback ?? "No feedback",
                        errorHandlingFeedback: result.error_handling_results?.Feedback ?? "No feedback",
                        minimalistFeedback: result.minimalist_results?.Feedback ?? "No feedback",
                        consistencyFeedback: result.consistency_results?.Feedback ?? "No feedback",
                        recognitionFeedback: result.recognition_results?.Feedback ?? "No feedback",
                        screenshot: imageDataUrl
                    });
                }
            } catch (error) {
                console.error("Error during fetch:", error);
                figma.notify(`Failed to send elements from ${frame.name} to backend.`);
            }
        }

        if (allFeedback.length > 0) {
            UiService.sendFeedbackToUI(allFeedback);
        }
    }
    else if (msg.type === 'request-modified-design') {
        try {
            const frameId = msg.frameId;
            
            // Use getNodeByIdAsync instead of getNodeById
            const frame = await figma.getNodeByIdAsync(frameId) as FrameNode;
            
            if (!frame || frame.type !== 'FRAME') {
                throw new Error("Original frame not found or not a frame");
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
                modified: `data:image/png;base64,${modifiedBase64}`,
                modifications: result.modifications
            });

            // Cleanup
            modifiedFrame.remove();

        } catch (error) {
            console.error("Modification error:", error);
            figma.notify(`Failed to show modified design: ${error instanceof Error ? error.message : String(error)}`);
            figma.ui.postMessage({
                type: 'modification-error',
                error: error instanceof Error ? error.message : String(error)
            });
        }
    }
};