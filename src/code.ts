import { FeatureExtractor } from "./services/FeatureExtractor";
import { ApiService } from "./services/ApiService";
import { UiService } from "./services/UiService";
import { FeedbackResult } from "./types";

// Show UI when the plugin starts
UiService.showUI();

figma.ui.onmessage = async (msg) => {
  
    try {
        console.log('Plugin received message:', msg.type);
        
        if (msg.type === 'start-detection') {
            // Your existing detection logic
            const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];
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
    }      

    if (allFeedback.length > 0) {
        UiService.sendFeedbackToUI(allFeedback);
    }
}
else if (msg.type === 'request-modifications') {
    try {
        console.log('Requesting modifications for frame:', msg.frameName);
        
        // Find frame by name (more reliable than ID)
        const frames = figma.currentPage.children.filter(node => 
            node.type === "FRAME" && node.name === msg.frameName
        ) as FrameNode[];
        
        if (frames.length === 0) {
            figma.notify(`Frame "${msg.frameName}" not found`);
            figma.ui.postMessage({
                type: 'error',
                message: `Frame "${msg.frameName}" not found`
            });
            return;
        }
        
        const frame = frames[0];
        
        // Get frame screenshot
        const originalImage = await frame.exportAsync({ format: "PNG" });
        const originalImageBase64 = figma.base64Encode(originalImage);
        
        // Extract design data
        const designData = await FeatureExtractor.extractForAI(frame);
        
        // Show loading in UI
        figma.ui.postMessage({
            type: 'progress-update',
            progress: 10,
            message: 'Preparing design data...'
        });
        
        // Call API service
        const result = await ApiService.sendModificationRequest(frame.id, {
            ...designData,
        });
        
        if (result.status === "error") {
            throw new Error(result.error);
        }
        
        // Send modifications to UI
        figma.ui.postMessage({
            type: 'design-modifications',
            frameId: frame.id,
            frameName: frame.name,
            
            modifications: result.modifications || [],
            summary: result.summary || "",
            modifiedDesign: result.modified_design || null
        });
        
    } catch (error) {
        console.error('Modification error:', error);
        figma.ui.postMessage({
            type: 'error',
            message: error instanceof Error ? error.message : 'Modification failed'
        });
    }
}
} catch (error) {
console.error('Plugin error:', error);
figma.notify('An error occurred. See console for details.');

}
};