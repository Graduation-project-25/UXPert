import json


def extract_rico_ui_elements(json_file_path):
    """Extract UI elements from Rico dataset."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = []

    def traverse(node):
        if isinstance(node, dict):
            bounds = node.get("bounds", [0, 0, 0, 0])
            element = {
                "type": node.get("class", ""),
                "position": {"x": bounds[0], "y": bounds[1]},
                "width": bounds[2] - bounds[0],
                "height": bounds[3] - bounds[1],
                "name": node.get("text", node.get("content-desc", "")),
                "clickable": node.get("clickable", False),
                "visibility": node.get("visibility", ""),
                "enabled": node.get("enabled", True),
            }
            elements.append(element)

            # Recursively process children
            for child in node.get("children", []):
                traverse(child)

    # Start traversal from the root element
    if "activity" in data and "root" in data["activity"]:
        traverse(data["activity"]["root"])

    return elements