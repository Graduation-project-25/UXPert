// Define the expected structure of the response
interface ConsistencyResult {
    status: number;
    consistency_results: {
        Feedback: Record<string, string>;
    };
}

// Show the initial UI with the start button
figma.showUI(__html__, { width: 700, height: 500 });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Step 1: Get all frames on the current page
        const frames = figma.currentPage.children.filter(node => node.type === "FRAME") as FrameNode[];

        // If no valid frames are found, notify the user
        if (frames.length === 0) {
            figma.notify('No frames found on the current page.');
            return; // Don't close the plugin.
        }

        // Array to accumulate all feedback
        const allFeedback = [];

        // Step 2: Extract features from frames and their children
        for (const frame of frames) {
            // Check if the frame is visible
            if (!frame.visible) {
                console.log(`Frame ${frame.name} is hidden. Skipping its children.`);
                continue; // Skip processing if the frame is hidden
            }

            // Find all visible children of the selected frame (elements inside the frame)
            const childNodes = frame.children.filter(node => node.visible);

            // Extract features for each child node within the selected frame
            const serializedNodes = childNodes.map(node => {
                let color = { r: 0, g: 0, b: 0 }; // Default color

                if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
                    const firstFill = node.fills[0];
                    if (firstFill.type === "SOLID" && firstFill.color) {
                        color = firstFill.color;
                    }
                }

                const fontSize = (node.type === "TEXT" && 'fontSize' in node) ? node.fontSize : null;

                return {
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
                    insideFrame: true, // All children are inside the selected frame
                    frameName: frame.name,
                    fontSize: fontSize
                };
            });

            const user_name = figma.currentUser ? figma.currentUser.name : "Unknown User";
            const design_name = figma.root.name ?? "Untitled Design";

            console.log(`Detected User: ${user_name}`);
            console.log(`Detected Design Name: ${design_name}`);

            try {
                console.log("Sending extracted features to the backend...");

                const processResponse = await fetch("http://localhost:3000/process", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_name,
                        design_name,
                        elements: serializedNodes
                    }),
                });

                if (!processResponse.ok) {
                    throw new Error(`HTTP error! Status: ${processResponse.status}`);
                }

                figma.notify(`${serializedNodes.length} Features saved successfully from ${frame.name}!`);

                // Type the response result properly
                const result = await processResponse.json() as ConsistencyResult;

                console.log("Consistency Evaluation Results: ", result.consistency_results);

                if (result.consistency_results.Feedback) {
                    console.log("📤 Sending feedback to UI...");

                    // Accumulate feedback for each frame
                    allFeedback.push({
                        frameName: frame.name,
                        feedback: result.consistency_results.Feedback,
                    });

                    console.log("✅ Feedback recorded for frame:", frame.name);
                } else {
                    console.log("No feedback available for frame:", frame.name);
                }

            } catch (error) {
                console.error("Error during fetch:", error);
                figma.notify(`Failed to send elements from ${frame.name} to backend.`);
            }
        }

        // After processing all frames, send consolidated feedback to UI
        if (allFeedback.length > 0) {
            figma.ui.postMessage({
                type: 'collective-feedback',
                feedback: allFeedback
            });
        }

        // Keep the plugin open to show feedback
    }
};
