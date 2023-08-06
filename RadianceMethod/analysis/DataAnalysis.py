import os
import numpy as np
import pandas as pd


class DataAnalysis:
    def __init__(self):
        self.results_dir = None
        self.results_dict = None
        self.normalised_results_dict = None
        self.dark_roi_real_coordinates = None
        self.light_roi_real_coordinates = None
        self.camera_to_dark_roi_real_distances = None
        self.camera_to_light_roi_real_distances = None
        self.camera_to_roi_centre_real_distances = None
        self.experiment_name = None
        self.channels_to_analyse = [0, 1, 2]

    def set_channels_to_analyse(self, channels_to_analyse):
        self.channels_to_analyse = channels_to_analyse

    def load_result_data(self):
        self.results_dict = {}

        for cb_face in ["dark", "light"]:
            for channel in self.channels_to_analyse:
                file_path = os.path.join(self.results_dir,
                                         f'{self.experiment_name}_{cb_face}_values_channel_{channel}.csv')
                self.results_dict[f"{cb_face}_roi_channel_{channel}"] = pd.read_csv(file_path, skiprows=2)

        self.dark_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_dark_coordinates.csv'),
                                                    delimiter=',')
        self.light_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_light_coordinates.csv'),
                                                     delimiter=',')
        self.camera_to_dark_roi_real_distances = np.loadtxt(
            os.path.join(self.results_dir, 'dark_roi_to_camera_real_distances.csv'), delimiter=',')
        self.camera_to_light_roi_real_distances = np.loadtxt(
            os.path.join(self.results_dir, 'light_roi_to_camera_real_distances.csv'), delimiter=',')
        self.camera_to_roi_centre_real_distances = (self.camera_to_dark_roi_real_distances + self.camera_to_light_roi_real_distances) / 2

    def calc_intensities(self):
        for channel in self.channels_to_analyse:
            dark_results_df = self.results_dict[f"dark_roi_channel_{channel}"]
            light_results_df = self.results_dict[f"light_roi_channel_{channel}"]

            n_s = dark_results_df.iloc[:, 3:] - light_results_df.iloc[:, 3:]
            n_0 = dark_results_df.iloc[0, 3:] - light_results_df.iloc[0, 3:]
            inteisities = n_s / n_0
            intensities_df = dark_results_df.copy()
            intensities_df.iloc[:, 3:] = inteisities
            roi_mean_heights = (self.dark_roi_real_coordinates[:, 2] + self.light_roi_real_coordinates[:, 2]) / 2
            intensities_df.columns = [["ROI height", " ", "m"] + list(roi_mean_heights), intensities_df.columns]
            file_path = os.path.join(self.results_dir, f"intensities_channel_{channel}.csv")
            intensities_df.to_csv(file_path)

    def calc_extinction_coefficients(self):  # TODO: Change form on how extinction coefficients are stored
        sigma = lambda intensity, distance: -1 * np.log(intensity) / distance
        for channel in self.channels_to_analyse:
            file_path = os.path.join(self.results_dir, f"intensities_channel_{channel}.csv")
            intensities_df = pd.read_csv(file_path, skiprows=2)
            intensities = intensities_df.iloc[:, 4:].to_numpy()
            extinction_coefficients = sigma(intensities, self.camera_to_roi_centre_real_distances)
            file_path = os.path.join(self.results_dir, f"extinction_coefficients_channel_{channel}.csv")
            np.savetxt(file_path, extinction_coefficients, delimiter=',')
