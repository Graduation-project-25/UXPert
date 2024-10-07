figma.showUI(__html__);

figma.ui.onmessage = (msg) => {
    if (msg.type === 'start-detection') {
        // Detect all elements on the current page
        const allNodes = figma.currentPage.findAll();

        // Check if there are any nodes on the page
        if (allNodes.length === 0) {
            console.log('No elements found on the page.');
            figma.notify('No elements found on the page.');
            figma.closePlugin();
        } else {
            console.log(`Detected ${allNodes.length} elements:`);
            allNodes.forEach((node, index) => {
                console.log(`Element ${index + 1}:`);
                console.log(`Name: ${node.name}`);
                console.log(`Type: ${node.type}`);

                // Log other properties if applicable
                if ('width' in node && 'height' in node) {
                    console.log(`Width: ${node.width}, Height: ${node.height}`);
                }
                if ('x' in node && 'y' in node) {
                    console.log(`Position: (X: ${node.x}, Y: ${node.y})`);
                }
                if ('rotation' in node) {
                    console.log(`Rotation: ${node.rotation}°`);
                }
                if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
                    const firstFill = node.fills[0] as Paint;
                    console.log(`Fill color: ${JSON.stringify(firstFill)}`);
                }
                if ('characters' in node) {
                    console.log(`Text Content: ${node.characters}`);
                }
                console.log('--------------------------------');
            });

            figma.notify(`${allNodes.length} elements detected!`);
            figma.closePlugin();
        }
    }
};

