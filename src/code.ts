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
    if (msg.type === 'start-detection') {
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

            const screenWidth = frame.width;
            const screenHeight = frame.height;

            const childNodes = frame.children.filter(node => node.visible);
            const serializedNodes = childNodes.map(node => {
                let color = { r: 0, g: 0, b: 0 };
                let isImageRectangle = false;
            
                if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
                    const firstFill = node.fills[0];
            
                    if (firstFill.type === "SOLID" && firstFill.color) {
                        color = firstFill.color;
                    } else if (firstFill.type === "IMAGE") {
                        isImageRectangle = true; // هذا المستطيل يحتوي على صورة
                    }
                }
            
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
                    isImageRectangle // تحديد ما إذا كان المستطيل يحتوي على صورة
                };
            });
            
            console.log(`Frame: ${frame.name}`);
            console.log(`Screen Width: ${screenWidth}, Screen Height: ${screenHeight}`);
            console.log("Extracted Features:", serializedNodes); // Print extracted features in console

            const user_name = figma.currentUser ? figma.currentUser.name : "Unknown User";
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
                            screen_width: screenWidth,
                            screen_height: screenHeight
                        },
                        elements: serializedNodes
                    }),
                });

                if (!processResponse.ok) throw new Error(`HTTP error! Status: ${processResponse.status}`);

                const result = await processResponse.json() as ConsistencyResult;

                if (result.consistency_results.Feedback || result.consistency_results.MinimalistFeedback !== undefined) {
                    allFeedback.push({
                        frameName: frame.name,
                        consistencyFeedback: result.consistency_results.Feedback,           // Consistency feedback
                        minimalistFeedback: result.consistency_results.MinimalistFeedback, // Minimalist feedback
                        errorPreventionFeedback: result.error_prevention_results.Feedback, // Error Prevention feedback
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
            console.log("Sending feedback:", JSON.stringify(allFeedback, null, 2));  // Debugging
        }
    }
};