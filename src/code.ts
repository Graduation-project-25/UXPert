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
            position: { 
                x: 'x' in node ? node.x : null, 
                y: 'y' in node ? node.y : null 
            },
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

            console.log(` ${filteredNodes.length}Features saved successfully!`);
            figma.notify(` ${filteredNodes.length}Features saved successfully!`);

            // // Step 2: Send the extracted features for clustering
            // console.log("Sending extracted features for clustering...");

            // const clusterResponse = await fetch("http://localhost:3000/cluster", {
            //     method: "POST",
            //     headers: { "Content-Type": "application/json" },
            //     body: JSON.stringify(serializedNodes),
            // });

            // if (!clusterResponse.ok) {
            //     throw new Error(`HTTP error! Status: ${clusterResponse.status}`);
            // }

            // const clusterResult = await clusterResponse.json() as { clusters: any[] };
            // console.log("Clustering response:", clusterResult);

            // figma.notify(`Clustering completed! Found ${clusterResult.clusters.length} clusters.`);
        } catch (error) {
            console.error("Error during fetch:", error);
            figma.notify("Failed to process elements.");
        }

        // Close the plugin after processing
        figma.closePlugin();
    }
};
