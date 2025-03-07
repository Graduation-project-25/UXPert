 export class FeatureExtractor {
    static async extractElements(node: SceneNode): Promise<any[]> {
        const extractedNodes: any[] = [];

        async function processNode(node: SceneNode) {
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

            // 🔹 Extract overridden text (if applicable)
            let textContent = buttonText || node.name;
            if (node.type === "TEXT") {
                textContent = node.characters; // Default text from the TextNode

                const parentInstance = node.parent;
                if (parentInstance?.type === "INSTANCE") {
                    try {
                        if (typeof parentInstance.getMainComponentAsync === "function") {
                            console.log("Fetching main component...");
                            const mainComponent = await parentInstance.getMainComponentAsync();
                            console.log("Main Component:", mainComponent);

                            if (mainComponent && "componentProperties" in parentInstance) {
                                console.log("Extracting overridden properties...");
                                const propertyOverrides = parentInstance.componentProperties;

                                // 🔹 Fix for TypeScript error
                                const propertyReferences = parentInstance.componentPropertyReferences as Record<string, string> | null;

                                for (const key in propertyOverrides) {
                                    const prop = propertyOverrides[key];

                                    // Check if this property corresponds to the overridden text
                                    if (prop && typeof prop === "object" && "value" in prop) {
                                        console.log(`Found overridden text for key '${key}':, prop.value`);

                                        // Ensure propertyReferences is valid and maps the key to this node's ID
                                        if (propertyReferences && propertyReferences[key] === node.id) {
                                            textContent = prop.value as string;
                                            break; // Exit once the correct text override is found
                                        }
                                    }
                                }
                            } else {
                                console.log("No overridden text found.");
                            }
                        } else {
                            console.error("getMainComponentAsync is not available on this instance:", parentInstance);
                        }
                    } catch (error) {
                        console.error("Error fetching main component:", error);
                    }
                }
            }

            extractedNodes.push({
                id: node.id ?? "None",
                name: node.name,
                type: node.type,
                textContent: textContent, // ✅ Extracts actual overridden text
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
                    await processNode(child as SceneNode);
                }
            }
        }

        await processNode(node);
        return extractedNodes;
    }
}