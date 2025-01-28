import os
import cv2
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from abc import ABC, abstractmethod

from components.Feature_Extractor_Component.EGFE_ui_extraction import extract_egfe_ui_elements, save_ui_elements


class Visualizer(ABC):

    @abstractmethod
    def visualize_ui_elements(self, image_folder, json_folder, output_folder, limit=50):
        pass

    @abstractmethod
    def scatter_plot_ui_elements(self, df):
        pass

    @abstractmethod
    def clustering_visualization_by_size(self, DBSCAN_dataset, clusters):
        pass

    @abstractmethod
    def clustering_visualization_by_position(self, DBSCAN_dataset, clusters):
        pass

    @abstractmethod
    def visualize_alignment_consistency(self, cluster_data):
        pass

    @abstractmethod
    def visualize_color_consistency(self, cluster_data):
        pass

    @abstractmethod
    def visualize_size_proportionality(self, cluster_data):
        pass

