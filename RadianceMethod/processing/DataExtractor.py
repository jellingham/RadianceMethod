import os
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import csv
from tqdm import tqdm

from RadianceMethod.helper_functions.distance_calculations import calc_distance_3d, divide_line_2d, divide_line_3d
from RadianceMethod.helper_functions.image_reading import get_capture_date_time, get_channel_arrays_from_jpg_file, \
    get_channel_arrays_from_raw_file


class DataExtractor:
    def __init__(self):
        self.dark_roi_pixel_dy = None
        self.dark_roi_real_dx = None
        self.image_dir = None
        self.image_file_format = 'jpg'
        self.results_dir = None
        self.reference_image_id = None
        self.first_image_id = None
        self.last_image_id = None
        self.skip_n_images = None
        self.image_name_string = None
        self.image_series = None
        self.dark_roi_pixel_bounds = None
        self.light_roi_pixel_bounds = None
        self.dark_roi_real_bounds = None
        self.light_roi_real_bounds = None
        self.camera_real_position = None
        self.number_of_rois = None
        self.roi_pixel_width = None
        self.experiment_name = None
        self.dark_roi_camera_real_distances = None
        self.light_roi_camera_real_distances = None
        self.height_marker_heights = None

    def set_image_series(self, first_image_id, last_image_id, skip_n_images=0):
        self.first_image_id = first_image_id
        self.last_image_id = last_image_id
        self.skip_n_images = skip_n_images

    def set_image_name_string(self, image_name_string):
        self.image_name_string = image_name_string

    def set_reference_image_id(self, reference_image_id):
        self.reference_image_id = reference_image_id

    def set_image_dir(self, image_dir):
        self.image_dir = image_dir

    def set_image_file_format(self, image_file_format):
        self.image_file_format = image_file_format

    def set_results_dir(self, results_dir):
        self.results_dir = results_dir
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

    def set_height_marker_heights(self, height_marker_heights):
        self.height_marker_heights = height_marker_heights

    def set_dark_roi_pixel_bounds(self, lower_pixel_bound, upper_pixel_bound):
        self.dark_roi_pixel_bounds = (lower_pixel_bound, upper_pixel_bound)

    def set_light_roi_pixel_bounds(self, lower_pixel_bound, upper_pixel_bound):
        self.light_roi_pixel_bounds = (lower_pixel_bound, upper_pixel_bound)

    def set_dark_roi_real_bounds(self, lower_real_bound, upper_real_bound):
        self.dark_roi_real_bounds = (lower_real_bound, upper_real_bound)

    def set_light_roi_real_bounds(self, lower_real_bound, upper_real_bound):
        self.light_roi_real_bounds = (lower_real_bound, upper_real_bound)

    def set_roi_parameters(self, roi_pixel_width, number_of_rois):
        self.roi_pixel_width = roi_pixel_width
        self.number_of_rois = number_of_rois

    def set_experiment_name(self, experiment_name):
        self.experiment_name = experiment_name

    def set_camera_position(self, x, y, z):
        self.camera_real_position = np.array([x, y, z])

    def _calc_roi_pixel_positions(self):
        print("Calculating ROI pixel positions...")
        self.dark_roi_pixel_coordinates, self.dark_roi_pixel_dx, self.dark_roi_pixel_dy = divide_line_2d(
            self.dark_roi_pixel_bounds[0], self.dark_roi_pixel_bounds[1], self.number_of_rois)
        self.light_roi_pixel_coordinates, self.light_roi_pixel_dx, self.light_roi_pixel_dy = divide_line_2d(
            self.light_roi_pixel_bounds[0], self.light_roi_pixel_bounds[1], self.number_of_rois)

    def _calc_roi_real_positions(self):
        print("Calculating ROI real positions...")
        self.dark_roi_real_coordinates, self.dark_roi_real_dx, self.dark_roi_real_dy, self.dark_roi_real_dz = divide_line_3d(
            self.dark_roi_real_bounds[0], self.dark_roi_real_bounds[1], self.number_of_rois)
        self.light_roi_real_coordinates, self.light_roi_real_dx, self.light_roi_real_dy, self.light_roi_real_dz = divide_line_3d(
            self.light_roi_real_bounds[0], self.light_roi_real_bounds[1], self.number_of_rois)

    def _calc_roi_camera_real_distances(self):
        print("Calculating distances between camera and ROIs...")
        self.light_roi_camera_real_distances = []
        self.dark_roi_camera_real_distances = []
        for i in range(self.number_of_rois):
            dark_roi_camera_real_distance = calc_distance_3d(self.dark_roi_real_coordinates[i],
                                                             self.camera_real_position)
            self.dark_roi_camera_real_distances.append(dark_roi_camera_real_distance)
            light_roi_camera_real_distance = calc_distance_3d(self.light_roi_real_coordinates[i],
                                                              self.camera_real_position)
            self.light_roi_camera_real_distances.append(light_roi_camera_real_distance)

    def _get_image_data(self, image_id, channel):
        file_path = self._get_image_file_path(image_id)
        image_array = None
        if self.image_file_format == 'jpg':
            image_array = get_channel_arrays_from_jpg_file(file_path, channel)
        elif self.image_file_format == 'raw':
            image_array = get_channel_arrays_from_raw_file(file_path, channel)
        return image_array

    def _get_image_file_path(self, image_id):
        filename = self.image_name_string.format(image_id)
        file_path = os.path.join(self.image_dir, filename)
        return file_path

    def _extract_pixel_values(self, image_array,  roi_pixel_coordinates, roi_pixel_dy):

        roi_pixel_values = []
        for coord in roi_pixel_coordinates:
            y_bottom = coord[1]
            y_top = y_bottom + roi_pixel_dy
            x_left = coord[0] - int(self.roi_pixel_width / 2)
            x_right = x_left + self.roi_pixel_width
            roi = image_array[y_top:y_bottom, x_left:x_right]
            roi_mean = roi.mean()
            roi_pixel_values.append(roi_mean)

        return roi_pixel_values

    def calc_geometrics(self):
        self._calc_roi_pixel_positions()
        self._calc_roi_real_positions()
        self._calc_roi_camera_real_distances()

    def write_roi_real_coordinates(self):
        dark_roi_real_center_coordinates = self.dark_roi_real_coordinates + np.array([0, 0, self.light_roi_real_dz / 2])
        light_roi_real_center_coordinates = self.light_roi_real_coordinates + np.array(
            [0, 0, self.light_roi_real_dz / 2])
        file_1_path = os.path.join(self.results_dir, 'roi_dark_coordinates.csv')
        np.savetxt(file_1_path, dark_roi_real_center_coordinates, header='X, Y, Z', delimiter=',')
        file_2_path = os.path.join(self.results_dir, 'roi_light_coordinates.csv')
        np.savetxt(file_2_path, light_roi_real_center_coordinates, header='X, Y, Z', delimiter=',')

    def write_roi_camera_to_roi_real_distances(self):
        file_1_path = os.path.join(self.results_dir, 'dark_roi_to_camera_real_distances.csv')
        file_2_path = os.path.join(self.results_dir, 'light_roi_to_camera_real_distances.csv')
        np.savetxt(file_1_path, self.dark_roi_camera_real_distances)
        np.savetxt(file_2_path, self.light_roi_camera_real_distances)


    def process_image_data(self):
        self.image_series = range(self.first_image_id, self.last_image_id, self.skip_n_images + 1)
        print(f"Processing {self.last_image_id - self.first_image_id} images...")

        channels = [0, 1, 2]

        for channel in channels:
            dark_file_path = os.path.join(self.results_dir, f'{self.experiment_name}_dark_values_channel_{channel}.csv')
            light_file_path = os.path.join(self.results_dir,
                                           f'{self.experiment_name}_light_values_channel_{channel}.csv')

            self._process_channel_data(channel, self.dark_roi_pixel_coordinates, self.dark_roi_pixel_dy, self.dark_roi_real_coordinates, self.dark_roi_real_dz, self.dark_roi_camera_real_distances, dark_file_path)
            self._process_channel_data(channel, self.light_roi_pixel_coordinates, self.light_roi_pixel_dy, self.light_roi_real_coordinates, self.light_roi_real_dz, self.light_roi_camera_real_distances, light_file_path)

        print("All images processed!")

    def _process_channel_data(self, channel, roi_pixel_coordinates, roi_pixel_dy,  roi_real_coordinates, roi_real_dz, roi_camera_real_distances, file_path):
        with open(file_path, 'w') as csvfile:
            writer = csv.writer(csvfile)

            header_1 = ["ROI height", "", "m"] + list(roi_real_coordinates[:, 2] + roi_real_dz / 2)
            header_2 = ["Camera to ROI real distances", "", "m"] + list(roi_camera_real_distances)
            header_3 = ["Image ID", "Time", "Timedelta"] + [f"ROI {i}" for i in range(self.number_of_rois)]

            writer.writerow(header_1)
            writer.writerow(header_2)
            writer.writerow(header_3)

            reference_image_file_path = self._get_image_file_path(self.reference_image_id)
            reference_image_capture_time = get_capture_date_time(reference_image_file_path)

            for image_id in tqdm(self.image_series):
                image_array = self._get_image_data(image_id, channel)
                image_file_path = self._get_image_file_path(image_id)
                capture_time = get_capture_date_time(image_file_path)
                time_delta = capture_time - reference_image_capture_time

                roi_values = self._extract_pixel_values(image_array, roi_pixel_coordinates, roi_pixel_dy)
                data_row = [image_id, capture_time, time_delta] + roi_values
                writer.writerow(data_row)

            time.sleep(0.1)
            print(f"Channel {channel} processed!")

    def show_reference_image(self, channel, upscale=True):
        image_array = self._get_image_data(self.reference_image_id, channel)
        if upscale:
            plt.imshow(image_array, cmap='gray', vmax=np.percentile(image_array, 99))
        else:
            plt.imshow(image_array, cmap='gray')
        plt.show()

    def plot_reference_image_with_rois(self, channel=0, upscale=True, show_height_markers=True):
        def draw_roi(x_pos, y_pos, width, height, color, label):
            rect = patches.Rectangle((x_pos, y_pos), width, height, linewidth=0.1, edgecolor=color, facecolor='none',
                                     label=label)
            return rect

        image_array = self._get_image_data(self.reference_image_id, channel)

        fig, ax = plt.subplots()
        if upscale:
            plt.imshow(image_array, cmap='gray', vmax=np.percentile(image_array, 99))
        else:
            plt.imshow(image_array, cmap='gray')
        for i, (roi_dark, roi_light) in enumerate(
                zip(self.dark_roi_pixel_coordinates, self.light_roi_pixel_coordinates)):
            label = 'Dark ROIs' if i == 0 else '_nolegend_'
            rect_dark = draw_roi(roi_dark[0], roi_dark[1], self.roi_pixel_width, self.dark_roi_pixel_dy, 'red', label)
            label = 'Light ROIs' if i == 0 else '_nolegend_'
            rect_light = draw_roi(roi_light[0], roi_light[1], self.roi_pixel_width, self.light_roi_pixel_dy, 'blue',
                                  label)
            ax.add_patch(rect_dark)
            ax.add_patch(rect_light)

            if self.dark_roi_pixel_coordinates[i, 0].max() < self.light_roi_pixel_coordinates[i, 0].max():
                dark_roi_text_x_position = roi_dark[0]
                light_roi_text_x_position = roi_light[0] + self.roi_pixel_width
                dark_roi_text_alignment = 'right'
                light_roi_text_alignment = 'left'
            else:
                dark_roi_text_x_position = roi_dark[0] + self.roi_pixel_width
                light_roi_text_x_position = roi_light[0]
                dark_roi_text_alignment = 'left'
                light_roi_text_alignment = 'right'

            ax.text(dark_roi_text_x_position, roi_dark[1], i, fontsize=0.1, color='red',
                    horizontalalignment=dark_roi_text_alignment)
            ax.text(light_roi_text_x_position, roi_light[1], i, fontsize=0.1, color='blue',
                    horizontalalignment=light_roi_text_alignment)

        if show_height_markers:
            for height in self.height_marker_heights:
                dark_marker_height = self.dark_roi_pixel_coordinates[0][1] + height * (
                        self.dark_roi_pixel_bounds[1][1] - self.dark_roi_pixel_bounds[0][1]) / (
                                        self.dark_roi_real_bounds[1][2] - self.dark_roi_real_bounds[0][2])
                light_marker_height = self.light_roi_pixel_coordinates[0][1] + height * (
                        self.light_roi_pixel_bounds[1][1] - self.light_roi_pixel_bounds[0][1]) / (
                                        self.light_roi_real_bounds[1][2] - self.light_roi_real_bounds[0][2])
                plt.axhline(dark_marker_height, color='orange', linestyle='--', linewidth=0.5, label=f'{height} m marker (Dark)')
                plt.axhline(light_marker_height, color='yellow', linestyle=':', linewidth=0.5, label=f'{height} m marker (Light)')

        plt.legend()
        file_path = os.path.join(self.results_dir, "ROIs.pdf")
        plt.savefig(file_path)
