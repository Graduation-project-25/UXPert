from abc import ABC, abstractmethod
import os
import random

from sklearn.model_selection import train_test_split
from components.Data_Splitter_Component.data_splitter import DataSplitterInterface

class JSONDataSplitter(DataSplitterInterface):
    def __init__(self, json_folder, train_ratio=0.8, seed=42):
        self.json_folder = json_folder
        self.train_ratio = train_ratio
        self.seed = seed

    def get_json_files(self):
        """Retrieve all JSON file paths from the folder."""
        return [os.path.join(self.json_folder, f) for f in os.listdir(self.json_folder) if f.endswith('.json')]

    def split_data(self):
        """Split JSON files into training and testing sets."""
        json_files = self.get_json_files()

        # Shuffle and split
        random.seed(self.seed)
        train_files, test_files = train_test_split(json_files, train_size=self.train_ratio, random_state=self.seed)

        return train_files, test_files

    def save_split_files(self, train_folder, test_folder):
        """Move JSON files into separate train and test folders."""
        os.makedirs(train_folder, exist_ok=True)
        os.makedirs(test_folder, exist_ok=True)

        train_files, test_files = self.split_data()

        for file in train_files:
            os.rename(file, os.path.join(train_folder, os.path.basename(file)))

        for file in test_files:
            os.rename(file, os.path.join(test_folder, os.path.basename(file)))

        print(f"Moved {len(train_files)} files to {train_folder}")
        print(f"Moved {len(test_files)} files to {test_folder}")

