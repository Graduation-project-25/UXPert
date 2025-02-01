# Example of how to use the Consistency class

import pandas as pd

from components.Feedback_Generator_Component.heuristics.consistency import Consistency

# Example dataset (replace with your extracted features)
data = {
    'width': [100, 100, 150, 150],
    'height': [50, 50, 60, 60],
    'color_r': [255, 255, 0, 0],
    'color_g': [0, 0, 255, 255],
    'color_b': [0, 0, 0, 0],
    'position.x': [10, 20, 10, 20],
    'position.y': [30, 30, 50, 50]
}

# Convert to DataFrame
cluster_data = pd.DataFrame(data)

# Initialize the Consistency heuristic evaluator
consistency_evaluator = Consistency()

# Evaluate the consistency of the cluster
consistency_scores = consistency_evaluator.evaluate_rule(cluster_data)

# Print the scores
print(consistency_scores)
