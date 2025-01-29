figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Get user information
        const userId = figma.currentUser?.id || "unknown_user";
        // const userName = figma.currentUser ? figma.currentUser.name  : "Unknown User";
        // const designName = figma.root.name || "Untitled Design";

        // Load all pages asynchronously
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();

        // Filter for visible nodes only
        const visibleNodes = allNodes.filter(node => node.visible);

        // Further filter to include only Frames and elements inside Frames
        const filteredNodes = visibleNodes.filter(node => 
            node.type === "FRAME" || (node.parent && node.parent.type === "FRAME")
        );

        if (filteredNodes.length === 0) {
            console.log('No valid Frames or elements inside Frames found.');
            figma.notify('No valid Frames or elements inside Frames found.');
            figma.closePlugin();
            return;
        }

        console.log(`Detected ${filteredNodes.length} valid Frames or elements inside Frames:`);

        // Serialize nodes into a JSON-compatible structure
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

        console.log("Serialized Frames and elements inside Frames:", serializedNodes);
        const user_name = msg.user_name || "Unknown User";
        const design_name = msg.design_name || "Untitled Design";

        try {
            const response = await fetch("http://localhost:3000/process", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: userId,  
                    user_name,
                    design_name,
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

        figma.closePlugin();
    }
};
