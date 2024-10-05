// // This plugin will open a window to prompt the user to enter a number, and
// // it will then create that many rectangles on the screen.

// // This file holds the main code for plugins. Code in this file has access to
// // the *figma document* via the figma global object.
// // You can access browser APIs in the <script> tag inside "ui.html" which has a
// // full browser environment (See https://www.figma.com/plugin-docs/how-plugins-run).

// // This shows the HTML page in "ui.html".
// figma.showUI(__html__);

// // Calls to "parent.postMessage" from within the HTML page will trigger this
// // callback. The callback will be passed the "pluginMessage" property of the
// // posted message.
// figma.ui.onmessage =  (msg: {type: string, count: number}) => {
//   // One way of distinguishing between different types of messages sent from
//   // your HTML page is to use an object with a "type" property like this.
//   if (msg.type === 'create-shapes') {
//     // This plugin creates rectangles on the screen.
//     const numberOfRectangles = msg.count;

//     const nodes: SceneNode[] = [];
//     for (let i = 0; i < numberOfRectangles; i++) {
//       const rect = figma.createRectangle();
//       rect.x = i * 150;
//       rect.fills = [{ type: 'SOLID', color: { r: 1, g: 0.5, b: 0 } }];
//       figma.currentPage.appendChild(rect);
//       nodes.push(rect);
//     }
//     figma.currentPage.selection = nodes;
//     figma.viewport.scrollAndZoomIntoView(nodes);
//   }

//   // Make sure to close the plugin when you're done. Otherwise the plugin will
//   // keep running, which shows the cancel button at the bottom of the screen.
//   figma.closePlugin();
// };
// Detect and log all elements on the current page using findAll()
const allNodes = figma.currentPage.findAll();

// Check if there are any nodes on the page
if (allNodes.length === 0) {
    console.log('No elements found on the page.');
    figma.notify('No elements found on the page.');
    figma.closePlugin();
} else {
    console.log(`Detected ${allNodes.length} elements:`);
    
    // Loop through each detected node and log its properties
    allNodes.forEach((node, index) => {
        console.log(`Element ${index + 1}:`);
        console.log(`Name: ${node.name}`);
        console.log(`Type: ${node.type}`);

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
