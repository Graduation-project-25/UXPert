figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Load all pages and find visible nodes (Frames or elements inside Frames)
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();
        const visibleNodes = allNodes.filter(node => node.visible);
        const filteredNodes = visibleNodes.filter(node => 
            node.type === "FRAME" || (node.parent && node.parent.type === "FRAME")
        );

        if (filteredNodes.length === 0) {
            figma.notify('No valid Frames or elements inside Frames found.');
            figma.closePlugin();
            return;
        }

 const serializedNodes = filteredNodes.map(node => {
    let color = { r: 0, g: 0, b: 0 }; // Default color

    if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
        const firstFill = node.fills[0];
        if (firstFill.type === "SOLID" && firstFill.color) {
            color = firstFill.color;
        }
    }

    return {
        name: node.name,
        type: node.type,
        width: 'width' in node ? node.width : null,
        height: 'height' in node ? node.height : null,
        "position.x": 'x' in node ? node.x : null, // Flattened position.x
        "position.y": 'y' in node ? node.y : null, // Flattened position.y
        rotation: 'rotation' in node ? node.rotation : null,
        color_r: color.r,  
        color_g: color.g,  
        color_b: color.b,  
        insideFrame: node.type === "FRAME" ? false : true,
        frameName: node.type === "FRAME" ? node.name : node.parent?.name,
    };
});

        const user_name = figma.currentUser ? figma.currentUser.name : "Unknown User";
        const design_name = figma.root.name ?? "Untitled Design";

        console.log(`Detected User: ${user_name}`);
        console.log(`Detected Design Name: ${design_name}`);

        try {
            // Step 1: Send extracted features to backend for storage in the database
            console.log("Sending extracted features to the backend...");

            const processResponse = await fetch("http://localhost:3000/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_name,
                    design_name,
                    elements: serializedNodes
                }),
            });

            if (!processResponse.ok) {
                throw new Error(`HTTP error! Status: ${processResponse.status}`);
            }

            console.log(` ${filteredNodes.length} Features saved successfully!`);
            figma.notify(` ${filteredNodes.length} Features saved successfully!`);

        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify("Failed to send elements to backend.");
            figma.notify("Failed to process elements.");
        }

        // Close the plugin after processing
        figma.closePlugin();
    }
};
