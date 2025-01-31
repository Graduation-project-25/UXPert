from components.Feedback_Generator_Component.heuristics.heuristic import HeuristicInterface

class Minimalist(HeuristicInterface):
    def evaluate_rule(self,cluster_data):
        print("Minimalist Rule")