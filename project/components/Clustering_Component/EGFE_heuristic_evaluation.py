import json
import os
from components.Feedback_Generator_Component.heuristics.heuristic_factory import HeuristicFactory
from components.Feedback_Generator_Component.heuristics.minimalist import Minimalist


class EGFE_HeuristicEvaluation():    
    # def __init__(self, cluster_json_file):
    #     with open(cluster_json_file, 'r') as f:
    #         self.clusters = json.load(f)


    def evaluate_minimalist_on_designs(self, train_folder):
        minimalist = Minimalist()
        minimalist_instance = HeuristicFactory.check_rule("minimalist")

        for file_name in os.listdir(train_folder):
            file_path = os.path.join(train_folder, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # print(data.get('width'))
                    print(file_name,'\n' )

                    result = minimalist.calculate_white_space_ratio(data,data['screen_size']['screen_width'],data['screen_size']['screen_width'])
                # print(result)


            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {file_name}: {e}. Skipping file.")
        # for element in data['elements']:

        # print(data)


        # print(self.clusters)
        # minimalist = Minimalist()
        # for cluster_id, elements in self.clusters.items():
        #     print(elements)
        #     if not elements:  # If the cluster is empty, assume full white space
        #         evaluation = "Pass - Minimalist Design"
        #     else:
        #         screen_width = elements[0]["screen_width"]
        #         screen_height = elements[0]["screen_height"]
        #         evaluation = minimalist.evaluate_minimalist(elements, screen_width, screen_height)
        #     # Store evaluation in each element
        #     for element in elements:
        #         element["aesthetic_evaluation"] = evaluation
            # Save results to JSON
            # with open('evaluated_clusters.json', 'w') as f:
                # json.dump(self.clusters, f, indent=4)







        # Optionally, save the updated clusters back to a new file
        # with open('evaluated_clusters.json', 'w') as f:
        #     json.dump(self.clusters, f, indent=4)
