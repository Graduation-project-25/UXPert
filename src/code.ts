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
else if (msg.type === 'create-frame-from-json') {
    // Show a minimal UI to trigger file picker
    const filePickerUI = `
        <input type="file" id="jsonFile" accept=".json" style="display: none;">
        <script>
            const fileInput = document.getElementById('jsonFile');
            fileInput.click();
            fileInput.onchange = () => {
                if (fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const json = JSON.parse(e.target.result);
                            parent.postMessage({ pluginMessage: { type: 'json-loaded', json } }, '*');
                        } catch (error) {
                            parent.postMessage({ pluginMessage: { type: 'error', message: 'Invalid JSON file' } }, '*');
                        }
                    };
                    reader.readAsText(file);
                }
            };
        </script>
    `;
    figma.showUI(filePickerUI, { visible: false });

    // Handle file picker response
    figma.ui.onmessage = async (fileMsg) => {
        try {
            if (fileMsg.type === 'json-loaded') {
                const json = fileMsg.json;
                if (!json || !json.elements) {
                    throw new Error("Invalid JSON: Missing elements");
                }

                // Load font for text nodes (with fallback)
                try {
                    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
                } catch (error) {
                    console.warn("Font 'Inter' not found, falling back to 'Roboto'");
                    await figma.loadFontAsync({ family: "Roboto", style: "Regular" });
                }

                // Create a new frame
                const newFrame = figma.createFrame();
                newFrame.name = "Modified Design";
                newFrame.resize(json.metadata?.screenWidth || 1440, json.metadata?.screenHeight || 717);
                newFrame.x = 1500; // Offset to avoid overlapping
                newFrame.y = 0;

                let yOffset = 20; // Start position for stacking nodes

                // Parse and create nodes
                json.elements.forEach((element: any) => {
                    let node: SceneNode | null = null;

                    // Parse color (supports rgb(r,g,b) or defaults to black)
                    let color = { r: 0, g: 0, b: 0, a: 1 };
                    if (element.color) {
                        const rgbMatch = element.color.match(/rgb\((\d+),(\d+),(\d+)\)/);
                        if (rgbMatch) {
                            color = {
                                r: parseInt(rgbMatch[1]) / 255,
                                g: parseInt(rgbMatch[2]) / 255,
                                b: parseInt(rgbMatch[3]) / 255,
                                a: 1
                            };
                        }
                    }

                    // Parse optional position and size
                    const x = element.x || 20;
                    const y = element.y || yOffset;
                    const width = element.width || (element.type === "FRAME" ? 200 : 120);
                    const height = element.height || (element.type === "FRAME" ? 100 : 40);

                    switch (element.type?.toUpperCase()) {
                        case "FRAME":
                            node = figma.createFrame();
                            node.name = element.text || "Unnamed Frame";
                            node.resize(width, height);
                            node.fills = [{ type: "SOLID", color }];
                            break;
                        case "RECTANGLE":
                            node = figma.createRectangle();
                            node.name = element.text || "Unnamed Rectangle";
                            node.resize(width, height);
                            node.fills = [{ type: "SOLID", color }];
                            break;
                        case "TEXT":
                            node = figma.createText();
                            (node as TextNode).characters = element.text || "";
                            (node as TextNode).fontSize = element.fontSize || 16;
                            (node as TextNode).fontName = element.fontName || { family: "Inter", style: "Regular" };
                            (node as TextNode).fills = [{ type: "SOLID", color }];
                            break;
                        case "LINE":
                            node = figma.createLine();
                            node.name = element.text || "Unnamed Line";
                            (node as LineNode).strokeWeight = element.strokeWeight || 2;
                            (node as LineNode).strokes = [{ type: "SOLID", color }];
                            (node as LineNode).resize(element.length || 100, 0);
                            break;
                        case "GROUP":
                            // Skip groups unless children are provided
                            if (!element.children) {
                                console.warn(`Skipping GROUP: ${element.text || "Unnamed"} (no children)`);
                                return;
                            }
                            node = figma.createFrame(); // Use frame as placeholder for group
                            node.name = element.text || "Unnamed Group";
                            node.resize(width, height);
                            break;
                        case "INSTANCE":
                        case "SYMBOLINSTANCE":
                            // Create placeholder for instances
                            node = figma.createRectangle();
                            node.name = `INSTANCE: ${element.text || "Unnamed"}`;
                            node.resize(width, height);
                            node.fills = [{ type: "SOLID", color }];
                            console.warn(`INSTANCE ${element.text || "Unnamed"} created as placeholder`);
                            break;
                        default:
                            console.warn(`Unsupported node type: ${element.type}`);
                            return;
                    }

                    if (node) {
                        // Apply position
                        node.x = x;
                        node.y = y;
                        yOffset += height + 20; // Update yOffset for next node

                        // Add to frame
                        newFrame.appendChild(node);
                    }
                });

                // Add frame to page
                figma.currentPage.appendChild(newFrame);

                // Select and zoom to new frame
                figma.currentPage.selection = [newFrame];
                figma.viewport.scrollAndZoomIntoView([newFrame]);

                figma.notify("New frame created with JSON changes!");
            } else if (fileMsg.type === 'error') {
                throw new Error(fileMsg.message);
            }
        } catch (error) {
            console.error("Error creating frame from JSON:", error);
            figma.notify(error instanceof Error ? error.message : "Failed to create frame");
        } finally {
            // Close the file picker UI
            figma.closePlugin();
        }
    };
}
} catch (error) {
console.error('Plugin error:', error);
figma.notify('An error occurred. See console for details.');

}
};