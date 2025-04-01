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



async function getModifiedDesign(frame: FrameNode, feedback: any, elements: any[]) {
    try {
        console.log("Exporting frame as image...");
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);
        const imageDataUrl = `data:image/png;base64,${imageBase64}`;

        console.log("Sending to modification endpoint...");
        const response = await fetch("http://localhost:3000/modify-design", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                screenshot: imageDataUrl,
                feedback: feedback,
                elements: elements
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("API Error:", errorData);
            throw new Error(errorData.error || "API request failed");
        }

        const result = await response.json();
        console.log("Received modification result:", result);
        
        if (result.status === "success") {
            figma.ui.postMessage({
                type: 'modified-design',
                original: imageDataUrl,
                modified: result.modified_screenshot,
                instructions: result.modification_instructions
            });
        } else {
            throw new Error(result.message || "Modification failed");
        }

    } catch (error) {
        console.error("Design modification error:", error);
        figma.notify('Failed to get design modifications. Check console for details.');
        
        // Send error details to UI
        figma.ui.postMessage({
            type: 'modification-error',
            error: error instanceof Error ? error.message : String(error)
        });
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

            if (result) {
                allFeedback.push({
                    frameName: frame.name,
                    errorPreventionFeedback: result.error_prevention_results.Feedback,
                    errorHandlingFeedback: result.error_handling_results.Feedback,
                    minimalistFeedback: result.minimalist_results.Feedback,
                    consistencyFeedback: result.consistency_results.Feedback,
                    recognitionFeedback : result.recognition_results.Feedback,
                    screenshot: imageDataUrl
                });
            }
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify(`Failed to send elements from ${frame.name} to backend.`);
        }
    }

    // if (allFeedback.length > 0) {
    //     UiService.sendFeedbackToUI(allFeedback);
    // }

    if (allFeedback.length > 0) {
        UiService.sendFeedbackToUI(allFeedback);
        // Get modified design for the first frame
        const firstFrame = frames[0];
        const firstFeedback = allFeedback[0];
        await getModifiedDesign(firstFrame, firstFeedback, await FeatureExtractor.extractElements(firstFrame));
    }
};
