import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS


os.makedirs("designs", exist_ok=True)


app = Flask(__name__)
CORS(app, supports_credentials=True)


def analyze_design(elements):
    issues = []


    colors = set()
    for element in elements:
        if 'color' in element:
            colors.add(tuple(element['color']))
    
    if len(colors) > 3: 
        issues.append("🚨 Too many different colors used, consider reducing them.")

    
    button_sizes = []
    for element in elements:
        if element.get('type') == 'button':
            button_sizes.append((element['width'], element['height']))
    
    if len(set(button_sizes)) > 2:  
        issues.append("⚠️ Inconsistent button sizes detected.")

 
    positions = [element.get("x", 0) for element in elements]
    if len(set(positions)) > 3:
        issues.append("🔍 Elements are not aligned properly.")

    return issues


@app.route('/process', methods=['POST', 'OPTIONS'])
def process_elements():
    if request.method == 'OPTIONS':
        return '', 200  


    data = request.get_json()
    user_name = data.get('user_name', "Unknown User")
    design_name = data.get('design_name', "Untitled Design")
    elements = data.get('elements', [])

    if not elements:
        return jsonify({"error": "No elements found"}), 400

 
    issues = analyze_design(elements)

   
    design_data = {
        "user_name": user_name,
        "design_name": design_name,
        "elements": elements,
        "issues": issues
    }

    file_path = f"designs/{user_name}_{design_name}.json"
    with open(file_path, 'w') as json_file:
        json.dump(design_data, json_file, indent=4)

    print(f"✅ Design saved: {file_path}")

    return jsonify({
        "message": "Design analyzed successfully!",
        "issues": issues  
    }), 200


@app.route('/', methods=['GET'])
def home():
    return "🚀 Welcome to the UX Analysis API!", 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
