figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Load all pages asynchronously
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();

        // Filter out elements that are hidden (visible = false)
        const visibleNodes = allNodes.filter(node => node.visible);

        // Check if there are any visible nodes
        if (visibleNodes.length === 0) {
            console.log('No visible elements found on the page.');
            figma.notify('No visible elements found on the page.');
            figma.closePlugin();
        } else {
            console.log(`Detected ${visibleNodes.length} visible elements:`);

            // Serialize nodes into a JSON-compatible structure
            const serializedNodes = visibleNodes.map(node => ({
                name: node.name,
                type: node.type,
                width: 'width' in node ? node.width : null,
                height: 'height' in node ? node.height : null,
                x: 'x' in node ? node.x : null,
                y: 'y' in node ? node.y : null,
                rotation: 'rotation' in node ? node.rotation : null,
                fills: 'fills' in node && Array.isArray(node.fills) ? node.fills : null,
                characters: 'characters' in node ? node.characters : null,
            }));

            console.log("Serialized visible elements:", serializedNodes);

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
                figma.notify(`${serializedNodes.length} visible elements sent successfully!`);
            } catch (error) {
                console.error('Error during fetch:', error);
                figma.notify('Failed to send elements to backend.');
            }

            figma.closePlugin();
        }
    }
};
