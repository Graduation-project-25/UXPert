# # Example of how to use the Consistency class

import pandas as pd

from components.Feedback_Generator_Component.heuristics.consistency import Consistency

# # Example dataset (replace with your extracted features)
# data = {
#     'width': [100, 100, 150, 150],
#     'height': [50, 50, 60, 60],
#     'color_r': [255, 255, 0, 0],
#     'color_g': [0, 0, 255, 255],
#     'color_b': [0, 0, 0, 0],
#     'position.x': [10, 20, 10, 20],
#     'position.y': [30, 30, 50, 50]
# }

# # Convert to DataFrame
# cluster_data = pd.DataFrame(data)

# # Initialize the Consistency heuristic evaluator
# consistency_evaluator = Consistency()

# # Evaluate the consistency of the cluster
# consistency_scores = consistency_evaluator.evaluate_rule(cluster_data)

# # Print the scores
# print(consistency_scores)


# -------------------------------
# Example design data with consistency to evaluate
design_data = {
    "user_id": "unknown_user",
    "user_name": "Asmaa",
    "design_name": "Consistency Test Design",
    "elements": [
        {
            "name": "Header",
            "type": "TEXT",
            "width": 300,
            "height": 50,
            "position.x": 50,
            "position.y": 20,
            "rotation": 0,
            "color_r": 0.2,
            "color_g": 0.2,
            "color_b": 0.5,
            "insideFrame": False,
            "frameName": "Header"
        },
        {
            "name": "Button 1",
            "type": "RECTANGLE",
            "width": 150,
            "height": 50,
            "position.x": 50,
            "position.y": 100,
            "rotation": 0,
            "color_r": 0.2,
            "color_g": 0.2,
            "color_b": 0.5,
            "insideFrame": True,
            "frameName": "Header"
        },
        {
            "name": "Button 2",
            "type": "RECTANGLE",
            "width": 150,
            "height": 50,
            "position.x": 250,
            "position.y": 100,
            "rotation": 0,
            "color_r": 0.24444444444444,
            "color_g": 0.333333333333332,
            "color_b": 0.5222222222,
            "insideFrame": True,
            "frameName": "Header"
        },
        {
            "name": "Logo",
            "type": "IMAGE",
            "width": 100,
            "height": 100,
            "position.x": 200,
            "position.y": 200,
            "rotation": 0,
            "color_r": 1,
            "color_g": 1,
            "color_b": 1,
            "insideFrame": False,
            "frameName": "Logo"
        }
    ]
}

# Extract data from the design elements for consistency evaluation
extracted_features = {
    'width': [element['width'] for element in design_data['elements']],
    'height': [element['height'] for element in design_data['elements']],
    'color_r': [element['color_r'] for element in design_data['elements']],
    'color_g': [element['color_g'] for element in design_data['elements']],
    'color_b': [element['color_b'] for element in design_data['elements']],
    'position_x': [element['position.x'] for element in design_data['elements']],
    'position_y': [element['position.y'] for element in design_data['elements']]
}

# Prepare the data for evaluation using the Consistency class
consistency_checker = Consistency()
cluster_data = consistency_checker.prepare_data_for_evaluation(extracted_features)

# Run the consistency evaluation
result = consistency_checker.evaluate_rule(cluster_data)

# Print the feedback and consistency score
print("Consistency Evaluation Results:")
print(f"Color Consistency: {result['ColorConsistency']}%")
print(f"Alignment Consistency: {result['AlignmentConsistency']}%")
print(f"Size Proportionality: {result['SizeProportionality']}%")
print(f"Total Consistency: {result['TotalConsistency']}%")
