// Define the expected structure of the response
interface ConsistencyResult {
    status: number;
    consistency_results: {
        Feedback: Record<string, string>;
        MinimalistFeedback: Record<string, string>;
    };
    error_prevention_results: {
        ErrorPreventionScore: string;
        ValidationIssues: string[];
        ConfirmationIssues: string[];
        Feedback: string;
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

        const serializedNodes = extractElements(frame);

        console.log(`Frame: ${frame.name}`);
        console.log(`Screen Dimensions: ${frame.width}x${frame.height}`);
        console.log("Extracted Features:", serializedNodes); // Debugging

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
                    elements: serializedNodes
                }),
            });

            if (!processResponse.ok) throw new Error(`HTTP error! Status: ${processResponse.status}`);

            const result = await processResponse.json() as ConsistencyResult;

            if (result.consistency_results.Feedback || result.consistency_results.MinimalistFeedback) {
                allFeedback.push({
                    frameName: frame.name,
                    consistencyFeedback: result.consistency_results.Feedback,
                    minimalistFeedback: result.consistency_results.MinimalistFeedback,
                    errorPreventionFeedback: result.error_prevention_results.Feedback,
                    errorPreventionScore: result.error_prevention_results.ErrorPreventionScore,
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
        console.log("Sending feedback:", JSON.stringify(allFeedback, null, 2)); // Debugging
    }
};

// Function to extract elements recursively inside Frames, Groups, and Instances
function extractElements(node: SceneNode): any[] {
    const extractedNodes: any[] = [];

    function processNode(node: SceneNode) {
        if (!node.visible) return;

        let color = { r: 0, g: 0, b: 0 };
        let isImageRectangle = false;

        if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
            const firstFill = node.fills[0];

            if (firstFill.type === "SOLID" && firstFill.color) {
                color = firstFill.color;
            } else if (firstFill.type === "IMAGE") {
                isImageRectangle = true;
            }
        }

        // Extract interactions from 'reactions' property
        const interactions = 'reactions' in node ? node.reactions : [];

        const hasClickInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_CLICK');
        const hasHoverInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_HOVER');
        const hasDragInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_DRAG');

        extractedNodes.push({
            name: node.name,
            type: node.type,
            width: 'width' in node ? node.width : null,
            height: 'height' in node ? node.height : null,
            "position.x": 'x' in node ? node.x : null,
            "position.y": 'y' in node ? node.y : null,
            rotation: 'rotation' in node ? node.rotation : null,
            color_r: color.r,
            color_g: color.g,
            color_b: color.b,
            hasClickInteraction,
            hasHoverInteraction,
            hasDragInteraction,
            isImageRectangle
        });

        // Recursively process child nodes if the node is a Frame, Group, or Instance
        if ('children' in node && ["FRAME", "GROUP", "INSTANCE"].includes(node.type)) {
            for (const child of node.children) {
                processNode(child as SceneNode);
            }
        }
    }

    processNode(node);
    return extractedNodes;
}
