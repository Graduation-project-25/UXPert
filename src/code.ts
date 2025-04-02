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



async function getModifiedDesign(frame: FrameNode) {
    try {
        const elements = await FeatureExtractor.extractForAI(frame);
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);
        
        const response = await fetch("http://localhost:3000/modify-design", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenshot: `data:image/png;base64,${imageBase64}`,
                elements
            }),
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }

        // Show modified image
        figma.ui.postMessage({
            type: 'design-modified',
            original: `data:image/png;base64,${imageBase64}`,
            modified: result.modified_image,
            instructions: result.instructions || ["No specific instructions provided"]
        });
        
    } catch (error) {
        console.error("Design modification failed:", error);
        figma.notify(`AI modification failed: ${error instanceof Error ? error.message : String(error)}`);
    }
}

function hexToRgb(hex: string): { r: number, g: number, b: number } {
    // Remove # if present
    hex = hex.replace('#', '');
    
    // Parse r, g, b values
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    
    return { r, g, b };
}
async function applyJsonChanges(changes: any[]) {
    for (const change of changes) {
        try {
            // Use async version with error handling
            const node = await figma.getNodeByIdAsync(change.id);
            
            if (!node) {
                console.warn(`Node ${change.id} not found`);
                continue;
            }

            // Handle color changes
            if (change.color && 'fills' in node) {
                const rgb = hexToRgb(change.color);
                (node as RectangleNode).fills = [{
                    type: 'SOLID',
                    color: rgb
                }];
            }

            // Handle text changes
            if (change.text && 'characters' in node) {
                (node as TextNode).characters = change.text;
            }

        } catch (error) {
            console.error(`Failed to modify node ${change.id}:`, error);
        }
    }
}
trackInstanceTextChanges();

figma.ui.onmessage = async (msg) => {
    if (msg.type !== 'start-detection') return;

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
        
            console.log("API Response:", result); 
        
            if (result && result.error_prevention_results) {
                allFeedback.push({
                    frameName: frame.name,
                    errorPreventionFeedback: result.error_prevention_results.Feedback ?? "No feedback",
                    errorHandlingFeedback: result.error_handling_results?.Feedback ?? "No feedback",
                    minimalistFeedback: result.minimalist_results?.Feedback ?? "No feedback",
                    consistencyFeedback: result.consistency_results?.Feedback ?? "No feedback",
                    recognitionFeedback: result.recognition_results?.Feedback ?? "No feedback",
                    screenshot: imageDataUrl
                });
            } else {
                console.warn("Missing expected fields in API response.");
            }
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify(`Failed to send elements from ${frame.name} to backend.`);
        }
        
    // if (allFeedback.length > 0) {
    //     UiService.sendFeedbackToUI(allFeedback);
    // }
    if (msg.type === 'design-modified') {
        // This will be handled by the UI's JavaScript
    }
    if (msg.type === 'apply-changes') {
        // Handle applying changes if needed
        figma.notify('Changes applied successfully');
    }
    if (allFeedback.length > 0) {
        UiService.sendFeedbackToUI(allFeedback);
        // Get modified design for the first frame
        const firstFrame = frames[0];
        const firstFeedback = allFeedback[0];
        // Process all frames, not just the first one
        const modifiedDesigns = [];
        for (const frame of frames) {
            if (!frame.visible) continue;
            
            try {
                await getModifiedDesign(frame);
            } catch (e) {
                console.error(`Failed to modify frame ${frame.name}:`, e);
            }
        }
    
    }
}};
