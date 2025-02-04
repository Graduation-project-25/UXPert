from components.Data_Processor_Component.EGFE_ui_processing import EGFE_UiProcessing
from components.Data_Loader_Component.EGFE_load_data import EGFE_LoadData


class EGFE_HeuristicEvaluation():    
    def __init__(self, designs):
        self.designs = designs
    def apply_dbscan(self):
        print("Evaluate")
        # DBSCAN logic here (e.g., clustering based on screen size)
        # self.clusters = dbscan_clustering(self.designs)

