// figma.showUI(__html__);

// //Sending a message from the UI to the plugin code
// figma.ui.onmessage = async (msg) => { 
//     // console.log("got this from the UI", msg)

//     if (msg.type === 'start-detection') {
//         // Detect all elements on the current page
//         await figma.loadAllPagesAsync();
//         const allNodes = figma.currentPage.findAll();

//         // Check if there are any nodes on the page
//         if (allNodes.length === 0) {
//             console.log('No elements found on the page.');
//             figma.notify('No elements found on the page.');
//             figma.closePlugin();
//         } else {
//             console.log(`Detected ${allNodes.length} elements:`);
//             allNodes.forEach((node, index) => {
//                 console.log(`Element ${index + 1}:`);
//                 console.log(`Name: ${node.name}`);
//                 console.log(`Type: ${node.type}`);

//                 // Log other properties if applicable
//                 if ('width' in node && 'height' in node) {
//                     console.log(`Width: ${node.width}, Height: ${node.height}`);
//                 }
//                 if ('x' in node && 'y' in node) {
//                     console.log(`Position: (X: ${node.x}, Y: ${node.y})`);
//                 }
//                 if ('rotation' in node) {
//                     console.log(`Rotation: ${node.rotation}°`);
//                 }
//                 if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
//                     const firstFill = node.fills[0] as Paint;
//                     console.log(`Fill color: ${JSON.stringify(firstFill)}`);
//                 }
//                 if ('characters' in node) {
//                     console.log(`Text Content: ${node.characters}`);
//                 }
//                 console.log('--------------------------------');
//             });

//             figma.notify(`${allNodes.length} elements detected!`);

//             // (async () => {
//             //     try {
//             //         const response = await fetch('http://localhost:3000');
//             //         if (!response.ok) {
//             //             throw new Error(`HTTP error! Status: ${response.status}`);
//             //         }
//             //         const json = await response.json();
//             //         console.log('Response from backend:', json);
//             //         figma.notify(`Backend connected`);
//             //     } catch (error) {
//             //         console.error('Error connecting to backend:', error);
//             //         figma.notify(`Error connecting to backend: ${error}`);
//             //     } finally {
//             //         figma.closePlugin();
//             //     }
//             // })();
            



            
//             // (async () => {
//             //     const response = await fetch('http://localhost:3000')
//             //     const json: any = await response.json()

//             //     console.log(JSON.stringify(json.args, null, 2))
//             //     figma.notify(`Backend connected`);

//             //     figma.closePlugin()
//             // })()

//             figma.closePlugin();
//         }
//     }
// };





figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        // Detect all elements on the current page
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();

        // Check if there are any nodes on the page
        if (allNodes.length === 0) {
            console.log('No elements found on the page.');
            figma.notify('No elements found on the page.');
            figma.closePlugin();
        } else {
            console.log(`Detected ${allNodes.length} elements:`);

            // Clean up the nodes data for JSON serialization
            const serializedNodes = allNodes.map((node, index) => {
                const nodeData: any = {
                    name: node.name,
                    type: node.type,
                    width: node.width || null,
                    height: node.height || null,
                    position: { x: node.x, y: node.y },
                    // rotation: node.rotation || null,
                    // fills: node.fills && Array.isArray(node.fills) && node.fills.length > 0
                        // ? JSON.stringify(node.fills[0]) // Only sending the first fill for simplicity
                        // : null,
                    // textContent: node.characters || null
                };
                return nodeData;
            });

            console.log(serializedNodes);

            fetch('http://localhost:3000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nodes: serializedNodes }), // Send the cleaned data
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log('Response from backend:', data);
                    figma.notify('Features sent successfully!');
                })
                .catch((error) => {
                    console.error('Error:', error);
                    figma.notify('Failed to send features.');
                });
        }
        figma.closePlugin();
    }
};

