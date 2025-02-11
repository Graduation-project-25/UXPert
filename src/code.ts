// Define the expected structure of the response
interface ConsistencyResult {
    status: number;
    consistency_results: {
        Feedback: Record<string, string>;
        // MinimalistFeedback: Record<string, string>;
    };
    error_prevention_results: {
        Feedback:Record<string, string>;
    };
    error_handling_results: {
        Feedback: Record<string, string>;
    };
}

// Show the initial UI with the start button
figma.showUI(__html__, { width: 1024, height: 3024 });

figma.ui.onmessage = async (msg) => {
    if (msg.type !== 'start-detection') return;

    const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];

    if (frames.length === 0) {
        figma.notify('No frames found on the current page.');
        return;
    }

    const allFeedback = [];

    for (const frame of frames) {
        if (!frame.visible) continue;

        const imageBytes = await frame.exportAsync({ format: "PNG" });
        const imageBase64 = figma.base64Encode(imageBytes);
        const imageDataUrl = `data:image/png;base64,${imageBase64}`;

        const serializedNodes = await extractElements(frame);  // Ensure serialized nodes are processed correctly

        const user_name = figma.currentUser?.name ?? "Unknown User";
        const design_name = figma.root.name ?? "Untitled Design";

        try {
            const processResponse = await fetch("http://localhost:3000/process", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name,
                    design_name,
                    frame: {
                        frameName: frame.name,
                        screen_width: frame.width,
                        screen_height: frame.height
                    },
                    elements: serializedNodes.map(node => {
                        // Exclude imageBase64 for non-image elements
                        const { imageBase64, ...rest } = node;
                        return imageBase64 ? { ...rest, imageBase64 } : rest;
                    })
                }),
            });

            if (!processResponse.ok) throw new Error(`HTTP error! Status: ${processResponse.status}`);

            const result = await processResponse.json() as ConsistencyResult;

            if (result.consistency_results.Feedback) {
                allFeedback.push({
                    frameName: frame.name,
                    consistencyFeedback: result.consistency_results.Feedback,
                    errorPreventionFeedback: result.error_prevention_results.Feedback,
                    errorHandlingFeedback: result.error_handling_results.Feedback,
                    screenshot: imageDataUrl
                });
            }
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify(`Failed to send elements from ${frame.name} to backend.`);
        }
    }

    if (allFeedback.length > 0) {
        figma.ui.postMessage({
            type: 'collective-feedback',
            feedback: allFeedback
        });
        // console.log("Sending feedback:", JSON.stringify(allFeedback, null, 2)); // Debugging
    }
};

// Function to extract elements recursively inside Frames, Groups, and Instances
async function extractElements(node: SceneNode): Promise<any[]> {
    const extractedNodes: any[] = [];

    async function processNode(node: SceneNode) {
        if (!node.visible) return;

        let color = { r: 0, g: 0, b: 0 };
        let isImageRectangle = false;
        let imageBase64 = "";
        let buttonText = "";
        let clickDestination: string = "None"; 

        if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
            const firstFill = node.fills[0];

            if (firstFill.type === "SOLID" && firstFill.color) {
                color = firstFill.color;
            } else if (firstFill.type === "IMAGE") {
                isImageRectangle = true;
                try {
                    const imageBytes = await node.exportAsync({ format: "PNG" });
                    imageBase64 = figma.base64Encode(imageBytes);
                } catch (error) {
                    console.error("Error exporting image:", error);
                }
            }
        }

        // Detect click interactions
        const interactions = 'reactions' in node ? node.reactions : [];
        const hasClickInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_CLICK');

        if (hasClickInteraction) {
            const action = interactions.find(interaction => interaction.trigger?.type === 'ON_CLICK')?.action;
            if (action && typeof action === 'object' && "destinationId" in action) {
                clickDestination = action.destinationId || "Unknown destination";
            }
        }

        const isIcon = node.type === 'VECTOR' || (node.type === 'INSTANCE' && node.name.toLowerCase().includes('icon'));

        if (["FRAME", "GROUP", "INSTANCE", "VECTOR"].includes(node.type) && 'children' in node) {
            const textChildren = node.children.filter(child => child.type === "TEXT") as TextNode[];
            if (textChildren.length > 0) {
                buttonText = textChildren.map(textNode => textNode.characters).join(" ");
            }
        }

        // Push the cleaned data to the extractedNodes array
        extractedNodes.push({
            id: node.id ?? "None", 
            name: node.name,
            type: node.type,
            textContent: buttonText || node.name,
            width: 'width' in node ? node.width : null,
            height: 'height' in node ? node.height : null,
            "position.x": 'x' in node ? node.x : null,
            "position.y": 'y' in node ? node.y : null,
            rotation: 'rotation' in node ? node.rotation : null,
            color_r: color.r,
            color_g: color.g,
            color_b: color.b,
            hasClickInteraction,
            isImageRectangle,
            // imageBase64, // Add extracted image data if applicable
            clickDestination,
            isIcon,
        });

        if ('children' in node && ["FRAME", "GROUP", "INSTANCE", "VECTOR"].includes(node.type)) {
            for (const child of node.children) {
                await processNode(child as SceneNode);
            }
        }
    }

    await processNode(node);
    return extractedNodes;
}
