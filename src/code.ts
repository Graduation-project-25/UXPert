// Define the expected structure of the response
interface ConsistencyResult {
    status: number;
    consistency_results: {
        Feedback: Record<string, string>;
    };
}

// Show the initial UI with the start button
figma.showUI(__html__, { width: 400, height: 200 });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Step 1: Get selected frame(s)
        const selectedNodes = figma.currentPage.selection;

        // If no frame is selected, notify the user and close the plugin
        if (selectedNodes.length === 0) {
            figma.notify('Please select a frame to run the plugin on.');
            figma.closePlugin();
            return;
        }

        // Filter to only include nodes of type "FRAME"
        const selectedFrames = selectedNodes.filter(node => node.type === "FRAME");

        // If no valid frames are selected, notify the user and close the plugin
        if (selectedFrames.length === 0) {
            figma.notify('Please select a valid frame to run the plugin on.');
            figma.closePlugin();
            return;
        }

        // Step 2: Extract features from selected frames and their children
        for (const frame of selectedFrames) {
            // Find all visible children of the selected frame (elements inside the frame)
            const childNodes = frame.findAll(node => node.visible);

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

                figma.notify(`${serializedNodes.length} Features saved successfully!`);

                // Type the response result properly
                const result = await processResponse.json() as ConsistencyResult;

                console.log("Consistency Evaluation Results: ", result.consistency_results);

                if (result.consistency_results.Feedback) {
                    console.log("📤 Attempting to send feedback to UI...");
                    console.log("Feedback Data:", result.consistency_results.Feedback);

                    // Send feedback to UI for each screen
                    figma.ui.postMessage({
                        type: 'feedback',
                        feedback: {
                            frameName: frame.name,
                            feedback: result.consistency_results.Feedback
                        }
                    });

                    console.log("✅ Message sent to UI");

                    const feedbackMessages = Object.values(result.consistency_results.Feedback).join("\n");
                    figma.notify(`Feedback for ${frame.name}:\n${feedbackMessages}`);
                } else {
                    console.log("No feedback available.");
                }

            } catch (error) {
                console.error("Error during fetch:", error);
                figma.notify("Failed to send elements to backend.");
            }
        }

        figma.closePlugin();
    }
};
