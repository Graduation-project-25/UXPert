figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Load all pages asynchronously
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();

        // Filter for visible nodes only
        const visibleNodes = allNodes.filter(node => node.visible);

        // Further filter to include only Frames and elements inside Frames
        const filteredNodes = visibleNodes.filter(node => 
            node.type === "FRAME" || (node.parent && node.parent.type === "FRAME")
        );

        // Check if there are any valid elements left after filtering
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
            insideFrame: node.type === "FRAME" ? false : true, // True if the element is inside a Frame
            frameName: node.type === "FRAME" ? node.name : node.parent?.name, // If it's a Frame, use its own name
        }));

        console.log("Serialized Frames and elements inside Frames:", serializedNodes);

        try {
            // Send the serialized nodes to the Flask backend
            const response = await fetch('http://localhost:3000/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ elements: serializedNodes }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const responseText = await response.text(); // Get plain text response from Flask
            console.log(responseText); // Expected: "Elements logged successfully!"
            figma.notify(`${serializedNodes.length} Frames or elements inside Frames sent successfully!`);
        } catch (error) {
            console.error('Error during fetch:', error);
            figma.notify('Failed to send elements to backend.');
        }

        figma.closePlugin();
    }
};
