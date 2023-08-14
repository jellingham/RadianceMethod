import os
import numpy as np
import pandas as pd
import warnings


class DataAnalysis:
    """
    A class for calculating intensities and axtinction coefficients based on the extracted experimental data.

    Attributes: results_dir (str or None): The directory path to store the analysis results.
    results_dict (dict or None): A dictionary containing the experimental results for different channels and regions of interest (ROIs).
    normalised_results_dict (dict or None): A dictionary containing normalised experimental results for different
    channels and ROIs.
    dark_roi_real_coordinates (numpy.ndarray or None): An array containing the real-world
    coordinates of the dark region of interest (ROI).
    light_roi_real_coordinates (numpy.ndarray or None): An array
    containing the real-world coordinates of the light region of interest (ROI).
    camera_to_dark_roi_real_distances (numpy.ndarray or None): An array containing the distances between the camera and the dark ROI in the real world.
    camera_to_light_roi_real_distances (numpy.ndarray or None): An array containing the distances between the camera
    and the light ROI in the real world.
    camera_to_roi_centre_real_distances (numpy.ndarray or None): An array
    containing the distances between the camera and the ROI centers in the real world.
    experiment_name (str or None): The name of the experiment.
    channels_to_analyse (list): A list of integers representing the channels to be analyzed.
    baseline_image_bounds (list): A list of integers giving the first and last image of range to normalize intensities.

    Methods:
        set_experiment_name(experiment_name):
            Set the name of the experiment for file naming purposes.

        set_results_dir(results_dir):
            Set the directory where the result files will be saved.

        set_channels_to_analyse(channels_to_analyse):
            Set the list of channels to be analyzed.

        set_baseline_image_bounds(baseline_image_bounds):
            Set the list of first and last image that are use for normalization.

        load_result_data():
            Load experimental results and ROI coordinates from files.

        calc_intensities():
            Calculate the intensities based on the experimental results and save them to CSV files.

        calc_extinction_coefficients():
            Calculate the extinction coefficients from the intensities and distances, and save them to CSV files.
    """

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
        self.baseline_image_bounds = [0, 1]

    def set_experiment_name(self, experiment_name):
        self.experiment_name = experiment_name

    def set_results_dir(self, results_dir):
        self.results_dir = results_dir

    def set_baseline_image_bounds(self, baseline_image_bounds):
        self.baseline_image_bounds = baseline_image_bounds

    def set_channels_to_analyse(self, channels_to_analyse):
        self.channels_to_analyse = channels_to_analyse

    def load_result_data(self):
        print("Loading extracted image data...")
        self.results_dict = {}

        for cb_face in ["dark", "light"]:
            for channel in self.channels_to_analyse:
                file_path = os.path.join(self.results_dir,
                                         f'{self.experiment_name}_{cb_face}_values_channel_{channel}.csv')
                self.results_dict[f"{cb_face}_roi_channel_{channel}"] = pd.read_csv(file_path, header=[0, 1, 2],
                                                                                    index_col=[0, 1, 2])

        self.dark_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_dark_coordinates.csv'),
                                                    delimiter=',')
        self.light_roi_real_coordinates = np.loadtxt(os.path.join(self.results_dir, 'roi_light_coordinates.csv'),
                                                     delimiter=',')
        self.camera_to_dark_roi_real_distances = np.loadtxt(
            os.path.join(self.results_dir, 'dark_roi_to_camera_real_distances.csv'), delimiter=',')
        self.camera_to_light_roi_real_distances = np.loadtxt(
            os.path.join(self.results_dir, 'light_roi_to_camera_real_distances.csv'), delimiter=',')
        self.camera_to_roi_centre_real_distances = (self.camera_to_dark_roi_real_distances +
                                                    self.camera_to_light_roi_real_distances) / 2



    def calc_intensities(self):
        print("Calculating intensities...")
        for channel in self.channels_to_analyse:
            dark_results_df = self.results_dict[f"dark_roi_channel_{channel}"]
            light_results_df = self.results_dict[f"light_roi_channel_{channel}"]

            n_s = dark_results_df - light_results_df
            dar_results_mean = dark_results_df.iloc[self.baseline_image_bounds[0]:self.baseline_image_bounds[1],:].mean()
            light_results_mean = light_results_df.iloc[self.baseline_image_bounds[0]:self.baseline_image_bounds[1],:].mean()

            n_0 = dar_results_mean - light_results_mean

            inteisities = n_s / n_0
            intensities_df = dark_results_df.copy()
            intensities_df.iloc[:, :] = inteisities
            file_path = os.path.join(self.results_dir, f"intensities_channel_{channel}.csv")
            intensities_df.to_csv(file_path)

    def calc_extinction_coefficients(self):
        print("Calculating extinction coefficients...")

        def calc_extinction_coefficients_from_intensities(intensity, distance):
            sigma = -1 * np.log(intensity) / distance
            if np.any(intensity < 0):
                warnings.warn("Invalid intensity detected! Check the ROI pixel positions on the reference image.")
                warnings.warn("Calculated extinction coefficient results may not be correct")
            if np.any(self.camera_to_roi_centre_real_distances < 0):
                warnings.warn("Invalid distance detected! Check the ROI real positions.")
                warnings.warn("Calculated extinction coefficient results may not be correct")

            return sigma

        for channel in self.channels_to_analyse:
            file_path = os.path.join(self.results_dir, f"intensities_channel_{channel}.csv")
            intensities_df = pd.read_csv(file_path, header=[0, 1, 2], index_col=[0, 1, 2])
            intensities = intensities_df.to_numpy()
            extinction_coefficients = calc_extinction_coefficients_from_intensities(intensities,
                                                                                    self.camera_to_roi_centre_real_distances)

            extinction_coefficients_df = self.results_dict["light_roi_channel_0"].copy()
            extinction_coefficients_df.iloc[:, :] = extinction_coefficients
            file_path = os.path.join(self.results_dir, f"extinction_coefficients_channel_{channel}.csv")
            extinction_coefficients_df.to_csv(file_path)
