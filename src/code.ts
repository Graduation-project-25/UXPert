// Figma Plugin Code

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

        // Serialize UI elements data
        const serializedNodes = filteredNodes.map(node => ({
            name: node.name,
            type: node.type,
            width: 'width' in node ? node.width : null,
            height: 'height' in node ? node.height : null,
            x: 'x' in node ? node.x : null,
            y: 'y' in node ? node.y : null,
            rotation: 'rotation' in node ? node.rotation : null,
            fills: 'fills' in node && Array.isArray(node.fills) ? node.fills : null,
            characters: 'characters' in node ? node.characters : null,
            insideFrame: node.type === "FRAME" ? false : true,
            frameName: node.type === "FRAME" ? node.name : node.parent?.name,
        }));

        const user_name = figma.currentUser ? figma.currentUser.name : "Unknown User";
        const design_name = figma.root.name ?? "Untitled Design";

        console.log(`Detected User: ${user_name}`);
        console.log(`Detected Design Name: ${design_name}`);

        try {
            // Send serialized nodes to backend
            const response = await fetch("http://localhost:3000/process", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_name: user_name,
                    design_name: design_name,
                    elements: serializedNodes,  
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const responseText = await response.text();
            console.log(responseText);
            figma.notify(`${serializedNodes.length} Frames or elements inside Frames sent successfully!`);
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify("Failed to send elements to backend.");
        }

        // Close the plugin after processing
        figma.closePlugin();
    }
};
