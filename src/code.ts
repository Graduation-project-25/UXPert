import { FeatureExtractor } from "./services/FeatureExtractor";
import { ApiService } from "./services/ApiService";
import { UiService } from "./services/UiService";
import { FeedbackResult } from "./types";

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

// Main plugin logic
UiService.showUI();

figma.ui.onmessage = async (msg) => {
    try {
        console.log('Plugin received message:', msg.type);

        if (msg.type === 'start-detection') {
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

            if (allFeedback.length > 0) {
                UiService.sendFeedbackToUI(allFeedback);
            }
        } else if (msg.type === 'request-modifications') {
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
                const originalImage = await frame.exportAsync({ format: "PNG" });
                const originalImageBase64 = figma.base64Encode(originalImage);
                const designData = await FeatureExtractor.extractForAI(frame);

                if (!designData.elements || designData.elements.length === 0) {
                    console.error('No elements extracted for frame:', frame.name);
                    figma.ui.postMessage({
                        type: 'error',
                        message: 'No elements found in the selected frame'
                    });
                    return;
                }

                const requestBody = {
                    design_json: {
                        metadata: { screenWidth: frame.width, screenHeight: frame.height },
                        elements: designData.elements
                    }
                };
                console.log('Sending request body:', JSON.stringify(requestBody, null, 2));

                figma.ui.postMessage({
                    type: 'progress-update',
                    progress: 10,
                    message: 'Preparing design data...'
                });

                const result = await ApiService.sendModificationRequest(frame.id, requestBody);

                if (result.status === "error") {
                    throw new Error(result.error);
                }

                // Merge original positions if missing
                let designJson = result.designJson || {};
                if (designJson.elements && designData.elements) {
                    designJson.elements = designJson.elements.map((modEl: any) => {
                        const origEl = designData.elements.find((o: any) => o.id === modEl.id);
                        if (origEl && (!modEl.x || !modEl.y || !modEl.width || !modEl.height)) {
                            return {
                                ...modEl,
                                x: origEl.x || 0,
                                y: origEl.y || 0,
                                width: origEl.width || 100,
                                height: origEl.height || 100,
                                fontSize: origEl.fontSize || 12,
                                fontFamily: origEl.fontFamily || "Inter"
                            };
                        }
                        return modEl;
                    });
                }

                // Render the designJson as an image
                let base64Image = '';
                if (designJson && designJson.elements && designJson.elements.length > 0) {
                    try {
                        const renderedFrame = await applyJsonToFigma(designJson);
                        const imageBytes = await exportFrameAsImage(renderedFrame);
                        base64Image = bytesToBase64(imageBytes);
                        renderedFrame.remove(); // Clean up
                    } catch (error) {
                        console.error('Failed to render design in backend:', error);
                        throw new Error(`Failed to render modified design: ${error}`);
                    }
                } else {
                    console.warn('No elements to render in designJson');
                }

                figma.ui.postMessage({
                    type: 'design-modifications',
                    frameId: frame.id,
                    frameName: frame.name,
                    modifications: result.modifications || [],
                    summary: result.summary || "",
                    designJson: designJson,
                    image: base64Image
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