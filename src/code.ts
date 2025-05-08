import { FeatureExtractor } from "./services/FeatureExtractor";
import { ApiService } from "./services/ApiService";
import { UiService } from "./services/UiService";
import { FeedbackResult } from "./types";

// Interface for recognition result to fix TypeScript error
interface RecognitionResult {
    element_id?: string;
    element_name?: string;
    Feedback?: string[];
}

// Rendering functions
async function applyJsonToFigma(json: any): Promise<FrameNode> {
    if (typeof figma === "undefined") {
        throw new Error("figma is not defined in applyJsonToFigma");
    }

    const frame = figma.createFrame();
    const width = json.metadata?.screenWidth || 1440;
    const height = json.metadata?.screenHeight || 2491;
    frame.resize(width, height);

    const frameElement = json.elements.find((el: any) => el.type === "FRAME" || el.type === "GROUP");
    if (frameElement && frameElement.color) {
        frame.fills = [{ type: 'SOLID', color: rgbStringToFigmaColor(frameElement.color) }];
    } else {
        frame.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
    }

    let x = 20, y = 20;
    const maxWidth = width - 40;
    const renderedGroups: string[] = frameElement ? [frameElement.id] : [];

    for (const element of json.elements.filter((el: any) => !renderedGroups.includes(el.id))) {
        let node;
        if (element.type === "GROUP") {
            node = figma.createFrame();
            node.resize(element.width || 100, element.height || 100);
            node.fills = [{ type: 'SOLID', color: rgbStringToFigmaColor(element.color || 'rgb(200,200,200)') }];
            node.name = element.text || 'Group';
            node.x = element.x || x;
            node.y = element.y || y;

            const label = figma.createText();
            try {
                await figma.loadFontAsync({ family: "Inter", style: "Regular" });
            } catch {
                try {
                    await figma.loadFontAsync({ family: "Roboto", style: "Regular" });
                } catch {
                    await figma.loadFontAsync({ family: "Arial", style: "Regular" });
                }
            }
            label.characters = element.text || 'Group';
            label.fontSize = 12;
            label.fills = [{ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }];
            label.x = (element.x || x) + 5;
            label.y = (element.y || y) - 15;
            frame.appendChild(label);
        } else if (element.type === "RECTANGLE") {
            node = figma.createRectangle();
            node.resize(element.width || 100, element.height || 100);
            node.fills = [{ type: 'SOLID', color: rgbStringToFigmaColor(element.color) }];
            node.x = element.x || x;
            node.y = element.y || y;
        } else if (element.type === "TEXT") {
            node = figma.createText();
            try {
                await figma.loadFontAsync({ family: element.fontFamily || "Inter", style: "Regular" });
            } catch {
                try {
                    await figma.loadFontAsync({ family: "Roboto", style: "Regular" });
                } catch {
                    await figma.loadFontAsync({ family: "Arial", style: "Regular" });
                }
            }
            node.characters = element.text || "";
            node.fontSize = element.fontSize || 12;
            node.fills = [{ type: 'SOLID', color: rgbStringToFigmaColor(element.color) }];
            node.x = element.x || x;
            node.y = element.y || y;
        }

        if (node) {
            frame.appendChild(node);
            x += (element.width || 100) + 20;
            if (x + 100 > maxWidth) {
                x = 20;
                y += (element.height || 100) + 20;
            }
        }
    }

    return frame;
}

function rgbStringToFigmaColor(rgbString: string): { r: number, g: number, b: number } {
    const match = rgbString.match(/rgb\((\d+),(\d+),(\d+)\)/);
    if (!match) {
        console.warn(`Invalid RGB string: ${rgbString}, using default white`);
        return { r: 1, g: 1, b: 1 };
    }
    const [, r, g, b] = match.map(Number);
    return { r: r / 255, g: g / 255, b: b / 255 };
}

async function exportFrameAsImage(frame: FrameNode): Promise<Uint8Array> {
    const imageBytes = await frame.exportAsync({
        format: 'PNG',
        constraint: { type: 'SCALE', value: 0.5 }
    });
    return imageBytes;
}

function bytesToBase64(bytes: Uint8Array): string {
    // Use figma.base64Encode instead of btoa
    const base64String = figma.base64Encode(bytes);
    return `data:image/png;base64,${base64String}`;
}

function save_image(imageDataUrl: any) {
    // Implementation remains the same
}

// Main plugin logic
UiService.showUI();

figma.ui.onmessage = async (msg) => {
    try {
        console.log('Plugin received message:', msg.type);

        if (msg.type === 'start-detection') {
            const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];
            const allFeedback: any[] = [];
            const totalFrames = frames.length;
            let processedFrames = 0;

            for (const frame of frames) {
                if (!frame.visible) continue;

                // Update progress
                processedFrames++;
                const progress = Math.floor((processedFrames / totalFrames) * 90); // Scale to 90%
                figma.ui.postMessage({
                    type: 'progress-update',
                    progress: progress
                });

                const imageBytes = await frame.exportAsync({ format: "PNG" });
                const imageBase64 = figma.base64Encode(imageBytes);
                const imageDataUrl = `data:image/png;base64,${imageBase64}`;

                const serializedNodes = await FeatureExtractor.extractElements(frame);
                const user_name = figma.currentUser?.name ?? "Unknown User";
                const design_name = figma.root.name ?? "Untitled Design";
                const frame_id = frame.id;

                // Check if frame data exists in the database
                try {
                    const existingFeedback = await ApiService.checkExistingFrame({
                        design_name,
                        frame_name: frame.name,
                        elements: serializedNodes.map(node => {
                            const { imageBase64, ...rest } = node;
                            return rest;
                        })
                    });

                    if (existingFeedback && existingFeedback.feedback) {
                        // If feedback exists, use it and skip further processing
                        console.log(`Found existing feedback for frame: ${frame.name}`);
                        allFeedback.push({
                            frameName: frame.name,
                            frameId: frame.id,
                            errorPreventionFeedback: existingFeedback.feedback.error_prevention_results?.Feedback ?? "No feedback",
                            errorHandlingFeedback: existingFeedback.feedback.error_handling_results?.Feedback ?? "No feedback",
                            minimalistFeedback: existingFeedback.feedback.minimalist_results?.Feedback ?? "No feedback",
                            consistencyFeedback: existingFeedback.feedback.consistency_results?.Feedback ?? "No feedback",
                            recognitionFeedback: Array.isArray(existingFeedback.feedback.recognition_results)
                                ? existingFeedback.feedback.recognition_results.map((r: RecognitionResult) => ({
                                    element_id: r?.element_id ?? "Unknown ID",
                                    element_name: r?.element_name ?? "Unknown Element",
                                    feedback: Array.isArray(r?.Feedback) ? r.Feedback.join(", ") : "No recognition feedback"
                                }))
                                : [],
                            screenshot: imageDataUrl
                        });
                        continue;
                    }
                } catch (error) {
                    console.warn(`Error checking existing frame data for ${frame.name}:`, error);
                    // Proceed with full processing if check fails
                }

                // Proceed with full feature extraction and feedback generation
                try {
                    const result = await ApiService.sendToBackend({
                        user_name,
                        design_name,
                        imageDataUrl,
                        frame: {
                            frameName: frame.name,
                            frameId: frame_id,
                            screen_width: frame.width,
                            screen_height: frame.height
                        },
                        elements: serializedNodes.map(node => {
                            const { imageBase64, ...rest } = node;
                            return imageBase64 ? { ...rest, imageBase64 } : rest;
                        })
                    }) as FeedbackResult;

                    console.log("API Response:", result);
                    const recognitionFeedback = Array.isArray(result.recognition_results)
                        ? result.recognition_results.map((r: RecognitionResult) => ({
                            element_id: r?.element_id ?? "Unknown ID",
                            element_name: r?.element_name ?? "Unknown Element",
                            feedback: Array.isArray(r?.Feedback) ? r.Feedback.join(", ") : "No recognition feedback"
                        }))
                        : [];

                    if (result && result.error_prevention_results) {
                        allFeedback.push({
                            frameName: frame.name,
                            frameId: frame.id,
                            errorPreventionFeedback: result.error_prevention_results.Feedback ?? "No feedback",
                            errorHandlingFeedback: result.error_handling_results?.Feedback ?? "No feedback",
                            minimalistFeedback: result.minimalist_results?.Feedback ?? "No feedback",
                            consistencyFeedback: result.consistency_results?.Feedback ?? "No feedback",
                            recognitionFeedback,
                            screenshot: imageDataUrl
                        });
                    }
                } catch (error) {
                    console.error("Error during fetch:", error);
                    figma.notify(`Failed to send elements from ${frame.name} to backend.`);
                }
            }

            // Complete progress
            figma.ui.postMessage({
                type: 'progress-update',
                progress: 100
            });

            if (allFeedback.length > 0) {
                UiService.sendFeedbackToUI(allFeedback);
            }
        }
        
        else if (msg.type === 'request-modifications') {
            try {
                console.log('Requesting modifications for frame:', msg.frameName);
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
                const imageBytes = await frame.exportAsync({ format: "PNG" });
                const imageBase64 = figma.base64Encode(imageBytes);
                const imageDataUrl = `data:image/png;base64,${imageBase64}`;
        
                // Get the design name - use a default if not available
                const designName = figma.root.name || "Untitled Design";
                
                // First get text suggestions
                const suggestionsResponse = await ApiService.getSuggestions(frame.id, designName);
                
                if (suggestionsResponse.error) {
                    throw new Error(suggestionsResponse.error);
                }
        
                // Send suggestions to UI
                figma.ui.postMessage({
                    type: 'design-modifications',
                    frameId: frame.id,
                    frameName: frame.name,
                    suggestions: suggestionsResponse.suggestions,
                    original_image: imageDataUrl
                });
        
            } catch (error) {
                console.error('Modification error:', error);
                figma.ui.postMessage({
                    type: 'error',
                    message: error instanceof Error ? error.message : 'Modification failed'
                });
            }
        }
    }
    catch (error) {
        console.error('Plugin error:', error);
        figma.notify('An error occurred. See console for details.');
    }

};