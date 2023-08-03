import os
import numpy as np
import pandas as pd

class DataAnalysis():
    def __init__(self):
        self.results_dir = None
        self.results_dict = None
        self.normalised_results_dict = None
        self.dark_roi_real_coordinates = None
        self.light_roi_real_coordinates = None
        self.camera_to_dark_roi_real_distances = None
        self.camera_to_light_roi_real_distances = None
        self.experiment_name = None

    def load_result_data(self):
        self.results_dict = {}

        for cb_face in ["dark", "light"]:
            for channel in range(3):
                file_path = os.path.join(self.results_dir, f'{self.experiment_name}_{cb_face}_values_channel_{channel}.csv')
                self.results_dict[f"{cb_face}_roi_channel_{channel}"] = pd.read_csv(file_path, skiprows=2)

        self.dark_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_dark_coordinates.csv'), delimiter=',')
        self.light_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_light_coordinates.csv'), delimiter=',')
        self.camera_to_dark_roi_real_distances = np.loadtxt(os.path.join(self.results_dir, 'dark_roi_to_camera_real_distances.csv'), delimiter=',')
        self.camera_to_light_roi_real_distances = np.loadtxt(os.path.join(self.results_dir, 'light_roi_to_camera_real_distances.csv'),delimiter=',')

    def normalise_results(self):
        self.normalised_results_dict = {}

        for cb_face in ["dark", "light"]:
            for channel in range(3):
                results_df = self.results_dict[f"{cb_face}_roi_channel_{channel}"]
                results_df_normlised = results_df.copy()
                results_df_normlised.iloc[:, 3:] /= results_df_normlised.iloc[0, 3:]
                self.normalised_results_dict[f"{cb_face}_roi_channel_{channel}"] = results_df_normlised
