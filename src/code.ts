figma.showUI(__html__);

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'start-detection') {
        await figma.loadAllPagesAsync();
        const allNodes = figma.currentPage.findAll();

        // Filter out elements that are hidden (visible = false)
        const visibleNodes = allNodes.filter(node => node.visible);

        if (visibleNodes.length === 0) {
            console.log('No visible elements found on the page.');
            figma.notify('No visible elements found on the page.');
            figma.closePlugin();
        } else {
            console.log(`Detected ${visibleNodes.length} visible elements:`);
            visibleNodes.forEach((node, index) => {
                console.log(`Element ${index + 1}:`);
                console.log(`Name: ${node.name}`);
                console.log(`Type: ${node.type}`);

                // Additional properties
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

            figma.notify(`${visibleNodes.length} visible elements detected!`);
        }
    }
};
