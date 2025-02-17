// src/services/FeatureExtractor.ts
export class FeatureExtractor {
    static extractElements(node: SceneNode): any[] {
        const extractedNodes: any[] = [];

        function processNode(node: SceneNode) {
            if (!node.visible) return;

            let color = { r: 0, g: 0, b: 0 };
            let isImageRectangle = false;
            let buttonText = "";
            let clickDestination: string = "None";

            if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
                const firstFill = node.fills[0];

                if (firstFill.type === "SOLID" && firstFill.color) {
                    color = firstFill.color;
                } else if (firstFill.type === "IMAGE") {
                    isImageRectangle = true;
                }
            }

            const interactions = 'reactions' in node ? node.reactions : [];
            const hasClickInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_CLICK');

            if (hasClickInteraction) {
                const action = interactions.find(interaction => interaction.trigger?.type === 'ON_CLICK')?.action;
                if (action && typeof action === 'object' && "destinationId" in action) {
                    clickDestination = action.destinationId ?? "Unknown destination";
                }
            }

            extractedNodes.push({
                id: node.id ?? "None",
                name: node.name,
                type: node.type,
                textContent: buttonText || node.name,
                width: 'width' in node ? node.width : null,
                height: 'height' in node ? node.height : null,
                "position.x": 'x' in node ? node.x : null,
                "position.y": 'y' in node ? node.y : null,
                rotation: 'rotation' in node ? node.rotation : null,
                color_r: color.r,
                color_g: color.g,
                color_b: color.b,
                hasClickInteraction,
                isImageRectangle,
                clickDestination,
            });

            if ('children' in node && ["FRAME", "GROUP", "INSTANCE", "VECTOR"].includes(node.type)) {
                for (const child of node.children) {
                    processNode(child as SceneNode);
                }
            }
        }

        processNode(node);
        return extractedNodes;
    }
}
