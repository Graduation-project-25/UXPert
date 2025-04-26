from html2image import Html2Image
import os

def generate_visual_ui_from_json(modifications, width=375, height=667):
    html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #f0f0f0;
            }}
            .canvas {{
                position: relative;
                width: {width}px;
                height: {height}px;
                margin: 20px auto;
                background: white;
                border: 2px solid #ccc;
            }}
            .element {{
                position: absolute;
                overflow: hidden;
                font-size: 12px;
                font-family: sans-serif;
                border: 1px solid #999;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="canvas">
    """

    for mod in modifications:
        pos = mod.get("position", {"x": 0, "y": 0})
        width = mod.get("width", 100)
        height = mod.get("height", 30)
        text = mod.get("element_name", "Element")
        color = mod.get("color", {"r": 255, "g": 255, "b": 255})
        background = f"rgb({color['r']},{color['g']},{color['b']})"

        html += f"""
        <div class="element" style="
            left: {pos.get('x', 0)}px;
            top: {pos.get('y', 0)}px;
            width: {width}px;
            height: {height}px;
            background: {background};
            line-height: {height}px;
        ">{text}</div>
        """

    html += "</div></body></html>"
    return html

def html_to_image(html_content, output_path='frontend/static/suggestion.png'):
    hti = Html2Image(output_path='frontend/static')
    hti.screenshot(html_str=html_content, save_as=os.path.basename(output_path))
    return output_path