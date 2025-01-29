figma.showUI(__html__);
// async function fetchUserDesigns(userId: string) {
//     try {
//         const response = await fetch(`http://localhost:3000/designs/${userId}`);
//         const designs = await response.json();
//         console.log("User Designs:", designs);
//     } catch (error) {
//         console.error("Error fetching designs:", error);
//     }
// }

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

            const userId = "user123";  // This should be dynamically set based on the logged-in user

            try {
                const response = await fetch("http://localhost:3000/process", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        user_id: userId,  // Include the user ID
                        elements: serializedNodes,  // Send extracted UI elements
                    }),
                });
            
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
            
                const responseData = await response.json();
                console.log(responseData);
                figma.notify(`${serializedNodes.length} visible elements sent successfully!`);
                // fetchUserDesigns("user123")
            } catch (error) {
                console.error("Error during fetch:", error);
                figma.notify("Failed to send elements to backend.");
            }

            figma.closePlugin();
        }
    }
};
