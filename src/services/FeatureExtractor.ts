export class IconDetector {
    // Detects if the node is an icon (a Frame or Component containing Vectors)
    static isIcon(node: SceneNode): boolean {
        // Check if the node is a Frame or Component (which are typical containers for icons)
        if (node.type === "FRAME" || node.type === "INSTANCE"  || node.type === "COMPONENT") {
            // Check if the node contains any vector shapes (VECTOR type)
            const containsVectors = node.children?.some(child => child.type === "VECTOR");

            // If the node contains vectors, it's likely an icon
            if (containsVectors) {
                return true;
            }
        }
        return false;
    }
    // Checks if the icon is near a text node (based on position and whether they are in the same component/group)
    static isNearText(node: SceneNode, threshold: number = 100): boolean {
        if ('children' in node && (node.type === "FRAME" || node.type === "INSTANCE" || node.type === "COMPONENT")) {
            for (const child of node.children || []) {
                if (child.type === "TEXT") {
                    // Check if the icon and text are close based on their positions
                    const distance = Math.sqrt(Math.pow(node.x - child.x, 2) + Math.pow(node.y - child.y, 2));
                    if (distance < threshold) {
                        return true;
                    }
                    
                    // Check if both icon and text are in the same component or group
                    if (node.parent && child.parent && node.parent.id === child.parent.id) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
}

export class FeatureExtractor {

    // Extract metadata and elements from the Figma node
    static async extractForAI(node: SceneNode): Promise<any> {
        // Extract elements from the Figma node
        const elements = await this.extractElements(node);

        // Filter out icons based on the `isIcon` method
        const iconElements = elements.filter(el => IconDetector.isIcon(el));
        // Label icons that are near a text node or inside a component containing text
        const labeledIcons = iconElements.map(el => {
            const isNearText = IconDetector.isNearText(el);
            return {
                ...el,
                label: isNearText 
            };
        });
        

        return {
            metadata: {
                screenWidth: 'width' in node ? node.width : null,
                screenHeight: 'height' in node ? node.height : null
            },
            elements: elements.map(el => ({
                id: el.id,
                type: el.type,
                text: el.textContent,
                color: `rgb(${el.color_r*255},${el.color_g*255},${el.color_b*255})`,
                interactions: el.hasClickInteraction ? {
                    destination: el.clickDestination
                } : null
            })),
        };
    }

    // Extract elements and their details from the Figma node recursively
    static async extractElements(node: SceneNode): Promise<any[]> {
        const extractedNodes: any[] = [];

        // Recursive function to process each node
        async function processNode(node: SceneNode) {
            if (!node.visible) return;

            // Skip VECTOR nodes
            if (node.type === "VECTOR") {
                return;
            }

            // Check if the current node is an icon
            const isIcon = IconDetector.isIcon(node); // Flag to check if the node is an icon

            let color = { r: 0, g: 0, b: 0 };
            let buttonText = "";
            let clickDestination: string = "None";
            
            // Process fills to extract color or image details
            if ('fills' in node && Array.isArray(node.fills) && node.fills.length > 0) {
                const firstFill = node.fills[0];

                if (firstFill.type === "SOLID" && firstFill.color) {
                    color = firstFill.color;  // Extract color
                }
            }

            // Check for click interactions (if applicable)
            const interactions = 'reactions' in node ? node.reactions : [];
            const hasClickInteraction = interactions.some(interaction => interaction.trigger?.type === 'ON_CLICK');

            if (hasClickInteraction) {
                const action = interactions.find(interaction => interaction.trigger?.type === 'ON_CLICK')?.action;
                if (action && typeof action === 'object' && "destinationId" in action) {
                    clickDestination = action.destinationId ?? "Unknown destination";
                }
            }

            // Extract text (default or overridden)
            let textContent = buttonText || node.name;
            if (node.type === "TEXT") {
                textContent = node.characters;  // Default text from the TextNode
            }

            // Store the extracted node data
            extractedNodes.push({
                id: node.id ?? "None",
                name: node.name,
                type: isIcon ? "symbolInstance" : node.type,
                textContent: textContent, 
                width: 'width' in node ? node.width : null,
                height: 'height' in node ? node.height : null,
                "position.x": 'x' in node ? node.x : null,
                "position.y": 'y' in node ? node.y : null,
                rotation: 'rotation' in node ? node.rotation : null,
                color_r: color.r, 
                color_g: color.g,
                color_b: color.b,
                hasClickInteraction,
                clickDestination,
                isIconLabeled:  isIcon ? IconDetector.isNearText(node) : null,
            });

            // Recursively process children nodes (if any)
            if ('children' in node && ["FRAME", "GROUP", "INSTANCE", "VECTOR"].includes(node.type)) {
                
                for (const child of node.children) {
                    await processNode(child as SceneNode);
                }
            }
        }

        // Start processing the root node
        await processNode(node);
        return extractedNodes;
    }
}
