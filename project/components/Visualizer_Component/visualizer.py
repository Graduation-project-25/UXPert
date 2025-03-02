import os
import cv2
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from abc import ABC, abstractmethod


class VisualizerInterface(ABC):

    @abstractmethod
    def visualize_ui_elements(self, image_folder, json_folder, output_folder, limit=50):
        pass

    @abstractmethod
    def scatter_plot_ui_elements(self, df):
        pass
    
    @abstractmethod
    def visualize_alignment_consistency(self, cluster_data):
        pass

    @abstractmethod
    def visualize_color_consistency(self, cluster_data):
        pass

    @abstractmethod
    def clustering_visualization_by_color(self, DBSCAN_dataset, clusters):
        pass

