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

async function renderModifiedDesign(original: FrameNode, modifiedJson: any): Promise<FrameNode> {
    // Create frame with proper dimensions
    const modifiedFrame = figma.createFrame();
    modifiedFrame.name = `Modified ${original.name}`;
    modifiedFrame.resize(original.width, original.height);
    modifiedFrame.fills = []; // Transparent background
    
    // Create all elements
    const nodesMap = new Map<string, SceneNode>();
    for (const element of modifiedJson.elements) {
        let node: SceneNode | null = null;
        
        try {
            switch (element.type) {
                case 'RECTANGLE':
                    node = figma.createRectangle();
                    if (element.cornerRadius && 'cornerRadius' in node) {
                        (node as RectangleNode).cornerRadius = element.cornerRadius;
                    }
                    break;
                    
                case 'TEXT':
                    node = figma.createText();
                    await figma.loadFontAsync({ family: "Inter", style: "Regular" });
                    (node as TextNode).characters = element.text || "";
                    break;
                    
                case 'FRAME':
                    node = figma.createFrame();
                    break;
                    
                case 'ELLIPSE':
                    node = figma.createEllipse();
                    break;
                    
                case 'LINE':
                    node = figma.createLine();
                    break;
                    
                case 'VECTOR':
                    node = figma.createVector();
                    break;
                    
                case 'INSTANCE':
                case 'COMPONENT':
                case 'symbolInstance':
                    // Try to find the main component by name if ID isn't available
                    let mainComponent: ComponentNode | null = null;
                    if (element.mainComponentId) {
                        const foundNode = figma.getNodeById(element.mainComponentId);
                        if (foundNode && foundNode.type === 'COMPONENT') {
                            mainComponent = foundNode;
                        }
                    }
                    
                    if (!mainComponent && element.name) {
                        // Search all components in the document
                        const allComponents = figma.root.findAll(node => 
                            node.type === 'COMPONENT' && node.name === element.name
                        ) as ComponentNode[];
                        if (allComponents.length > 0) {
                            mainComponent = allComponents[0];
                        }
                    }
                    
                    if (mainComponent) {
                        node = mainComponent.createInstance();
                    } else {
                        // Fallback to frame if component not found
                        node = figma.createFrame();
                        node.name = `${element.type}: ${element.text || element.name || 'Untitled'}`;
                    }
                    break;
                    
                case 'GROUP':
                    node = figma.group([], modifiedFrame);
                    break;

                case 'POLYGON':
                    node = figma.createPolygon();
                    if (element.pointCount && 'pointCount' in node) {
                        (node as PolygonNode).pointCount = element.pointCount;
                    }
                    break;

                case 'STAR':
                    node = figma.createStar();
                    if (element.pointCount && 'pointCount' in node) {
                        (node as StarNode).pointCount = element.pointCount;
                    }
                    break;

                case 'SLICE':
                    node = figma.createSlice();
                    break;

                case 'STICKY':
                    node = figma.createSticky();
                    break;

                case 'CONNECTOR':
                    node = figma.createConnector();
                    break;

                case 'SHAPE_WITH_TEXT':
                    node = figma.createShapeWithText();
                    break;

                default:
                    // Fallback for unsupported types
                    node = figma.createFrame();
                    node.name = `${element.type}: ${element.text || element.name || 'Untitled'}`;
            }

            if (node) {
                // Set common properties
                node.name = element.text || element.name || "Unnamed";
                node.x = element['position.x'] || 0;
                node.y = element['position.y'] || 0;
                
                // Set size if specified - only for resizable nodes
                if (element.width && element.height) {
                    if ('resize' in node) {
                        (node as BaseFrameMixin).resize(element.width, element.height);
                    }
                }

                // Set color if specified
                if (element.color && 'fills' in node) {
                    const rgb = hexToRgb(element.color);
                    (node as MinimalFillsMixin).fills = [{
                        type: 'SOLID',
                        color: rgb,
                        opacity: element.opacity || 1
                    }];
                }

                // Set text properties for text nodes
                if (node.type === 'TEXT') {
                    const textNode = node as TextNode;
                    if (element.fontSize) textNode.fontSize = element.fontSize;
                    if (element.textAlign) textNode.textAlignHorizontal = element.textAlign;
                    if (element.fontName) {
                        try {
                            await figma.loadFontAsync(element.fontName);
                            textNode.fontName = element.fontName;
                        } catch (e) {
                            console.warn(`Couldn't load font ${element.fontName?.family}`);
                        }
                    }
                }

                // Set stroke if specified
                if (element.stroke && 'strokes' in node) {
                    const strokeRgb = hexToRgb(element.stroke.color);
                    (node as MinimalStrokesMixin).strokes = [{
                        type: 'SOLID',
                        color: strokeRgb,
                        opacity: element.stroke.opacity || 1
                    }];
                    if (element.stroke.weight && 'strokeWeight' in node) {
                        (node as MinimalStrokesMixin).strokeWeight = element.stroke.weight;
                    }
                }

                nodesMap.set(element.id, node);
            }
        } catch (e) {
            console.error(`Error creating ${element.type}:`, e);
        }
    }

    // Second pass: Build hierarchy and handle connections
    for (const element of modifiedJson.elements) {
        const node = nodesMap.get(element.id);
        if (!node) continue;

        // Ensure proper positioning
        node.x = element['position.x'] || 0;
        node.y = element['position.y'] || 0;
        
        // Add to frame
        modifiedFrame.appendChild(node);
    }

    return modifiedFrame;
}

async function getModifiedDesign(frame: FrameNode): Promise<void> {
    try {
        figma.ui.postMessage({ type: 'processing-started' });

        // 1. Prepare and send data
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

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const result = await response.json();
        
        if (result.status === "error") {
            throw new Error(result.error || "Unknown backend error");
        }

        // 2. Render the modified design
        const modifiedFrame = await renderModifiedDesign(frame, result.modified_design);
        
        // CRITICAL: Add to current page and force render
        figma.currentPage.appendChild(modifiedFrame);
        await new Promise(resolve => { 
            modifiedFrame.exportAsync({ format: 'PNG' }).then(resolve); 
        });
        
        // Export with proper settings
        const modifiedBytes = await modifiedFrame.exportAsync({
            format: "PNG",
            constraint: { type: 'SCALE', value: 1 },
            contentsOnly: true // This is key to avoid black squares
        });
        
        // Convert to displayable image
        const modifiedBase64 = figma.base64Encode(modifiedBytes);
        
        // Verify we got actual image data
        if (modifiedBase64.length < 1000) {
            throw new Error("Image export failed - insufficient data");
        }

        // Send to UI
        figma.ui.postMessage({
            type: 'design-modified',
            frameId: frame.id,
            original: `data:image/png;base64,${imageBase64}`,
            modified: `data:image/png;base64,${modifiedBase64}`,
            modifications: result.modifications || []
        });

        // Cleanup
        modifiedFrame.remove();
        
    } catch (error) {
        console.error("Modification Error:", error);
        
        // Export original as fallback
        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);

        figma.ui.postMessage({
            type: 'modification-error',
            error: error instanceof Error ? error.message : String(error),
            original: `data:image/png;base64,${imageBase64}`
        });
    } finally {
        figma.ui.postMessage({ type: 'processing-finished' });
    }
}

// Type guard for valid connector endpoint nodes
function isConnectorEndpoint(node: SceneNode): node is 
    VectorNode | BooleanOperationNode | ComponentNode | InstanceNode | TextNode {
    return (
        node.type === 'VECTOR' ||
        node.type === 'BOOLEAN_OPERATION' ||
        node.type === 'COMPONENT' ||
        node.type === 'INSTANCE' ||
        node.type === 'TEXT'
    );
}

function hexToRgb(hex: string): RGB {
    // Remove # if present
    hex = hex.replace('#', '');
    
    // Parse r, g, b values
    let r, g, b;
    if (hex.length === 3) {
        r = parseInt(hex[0] + hex[0], 16) / 255;
        g = parseInt(hex[1] + hex[1], 16) / 255;
        b = parseInt(hex[2] + hex[2], 16) / 255;
    } else if (hex.length === 6) {
        r = parseInt(hex.substring(0, 2), 16) / 255;
        g = parseInt(hex.substring(2, 4), 16) / 255;
        b = parseInt(hex.substring(4, 6), 16) / 255;
    } else {
        // Default to black if invalid
        return { r: 0, g: 0, b: 0 };
    }
    
    return { r, g, b };
}
async function safeLoadFont(fontName: FontName): Promise<boolean> {
    try {
        await figma.loadFontAsync(fontName);
        return true;
    } catch (e) {
        console.warn(`Failed to load font ${fontName.family} ${fontName.style}:`, e);
        return false;
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
