import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import exifread
from datetime import datetime
import time

import csv
from tqdm import tqdm


class RadianceMethod:
    def __init__(self):
        self.dark_roi_pixel_dy = None
        self.dark_roi_real_dx = None
        self.image_dir = None
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
        self.camera_real_position = (x, y, z)

    def _calc_roi_pixel_positions(self):
        self.dark_roi_pixel_coordinates, self.dark_roi_pixel_dx, self.dark_roi_pixel_dy = _divide_line(
            self.dark_roi_pixel_bounds[0], self.dark_roi_pixel_bounds[1], self.number_of_rois)
        self.light_roi_pixel_coordinates, self.light_roi_pixel_dx, self.light_roi_pixel_dy = _divide_line(
            self.light_roi_pixel_bounds[0], self.light_roi_pixel_bounds[1], self.number_of_rois)

    def _calc_roi_real_positions(self):
        self.dark_roi_real_coordinates, self.dark_roi_real_dx, self.dark_roi_real_dy = _divide_line(
            self.dark_roi_real_bounds[0], self.dark_roi_real_bounds[1], self.number_of_rois, coordinates='real')
        self.light_roi_real_coordinates, self.light_roi_real_dx, self.light_roi_real_dy = _divide_line(
            self.light_roi_real_bounds[0], self.light_roi_real_bounds[1], self.number_of_rois, coordinates='real')

    def _get_image_data(self, image_id, channel='all'):
        file_path = self._get_image_file_path(image_id)
        image_array = _get_channel_arrays_from_jpg_file(file_path, channel)
        return image_array

    def _get_image_file_path(self, image_id):
        filename = self.image_name_string.format(image_id)
        file_path = os.path.join(self.image_dir, filename)
        return file_path

    def _extract_pixel_values(self, image_array):  # TODO: outsource in single function
        roi_dark_values = []
        roi_light_values = []

        for coord in self.dark_roi_pixel_coordinates[:-1]:
            y_bottom = coord[1]
            y_top = y_bottom + self.light_roi_pixel_dy
            x_left = coord[0] - int(self.roi_pixel_width / 2)
            x_right = x_left + self.roi_pixel_width
            roi = image_array[y_top:y_bottom, x_left:x_right]
            roi_mean = roi.mean()
            roi_dark_values.append(roi_mean)

        for coord in self.light_roi_pixel_coordinates[:-1]:
            y_bottom = coord[1]
            y_top = y_bottom + self.light_roi_pixel_dy
            x_left = coord[0] - int(self.roi_pixel_width / 2)
            x_right = x_left + self.roi_pixel_width
            roi = image_array[y_top:y_bottom, x_left:x_right]
            roi_mean = roi.mean()
            roi_light_values.append(roi_mean)

        return roi_dark_values, roi_light_values

    def process_image_data(self):
        self.image_series = range(self.first_image_id, self.last_image_id, self.skip_n_images + 1)
        print(f"Processing {self.last_image_id - self.first_image_id} images...")
        for channel in [0, 1, 2]:
            filename_1 = f'{self.experiment_name}_dark_values_channel_{channel}.csv'
            filename_2 = f'{self.experiment_name}_light_values_channel_{channel}.csv'

            with open(filename_1, 'w') as csvfile_1, open(filename_2, 'w') as csvfile_2:
                writer_1 = csv.writer(csvfile_1)
                writer_2 = csv.writer(csvfile_2)

                header_1_black_rois = ["ROI real coordinates", "[m m]"] + list(self.dark_roi_real_coordinates)
                header_1_light_rois = ["ROI real coordinates", "[m m]"] + list(self.light_roi_real_coordinates)
                header_2 = ["Time", "Timedelta"] + [f"ROI {i}" for i in range(self.number_of_rois)]
                writer_1.writerow(header_1_black_rois)
                writer_1.writerow(header_2)
                writer_2.writerow(header_1_light_rois)
                writer_2.writerow(header_2)

                reference_image_file_path = self._get_image_file_path(self.reference_image_id)
                reference_image_capture_time = _get_capture_date_time(reference_image_file_path)

                for image_id in tqdm(self.image_series):
                    image_array = self._get_image_data(image_id, channel)
                    image_file_path = self._get_image_file_path(image_id)
                    capture_time = _get_capture_date_time(image_file_path)
                    time_delta = capture_time - reference_image_capture_time

                    roi_dark_values, roi_light_values = self._extract_pixel_values(image_array)
                    writer_1.writerow([capture_time, time_delta] + roi_dark_values)
                    writer_2.writerow([capture_time, time_delta] + roi_light_values)
                time.sleep(0.1)
                print(f"Channel {channel} processed!")

    def plot_reference_image_with_roi(self):
        def draw_roi(x_pos, y_pos, width, height, color, label):
            rect = patches.Rectangle((x_pos, y_pos), width, height, linewidth=0.1, edgecolor=color, facecolor='none',
                                     label=label)
            return rect

        image_array = self._get_image_data(self.reference_image_id)
        fig, ax = plt.subplots()
        plt.imshow(image_array)
        for i, (roi_dark, roi_light) in enumerate(
                zip(self.dark_roi_pixel_coordinates, self.light_roi_pixel_coordinates)):
            label = 'Dark ROIs' if i == 0 else '_nolegend_'
            rect_dark = draw_roi(roi_dark[0], roi_dark[1], self.roi_pixel_width, self.dark_roi_pixel_dy, 'red', label)
            label = 'Light ROIs' if i == 0 else '_nolegend_'
            rect_light = draw_roi(roi_light[0], roi_light[1], self.roi_pixel_width, self.light_roi_pixel_dy, 'blue',
                                  label)
            ax.add_patch(rect_dark)
            ax.add_patch(rect_light)
            ax.text(roi_dark[0], roi_dark[1], i, fontsize=0.1, color='red', horizontalalignment='right')
            ax.text(roi_light[0], roi_light[1], i, fontsize=0.1, color='blue', horizontalalignment='right')
        plt.legend()
        plt.savefig("ROIs.pdf")


def _divide_line(point1, point2, n, coordinates='pixel'):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the step size for x and y coordinates
    step_x = (x2 - x1) / n
    step_y = (y2 - y1) / n

    # Generate intermediate points
    intermediate_points = []
    for i in range(1, n):
        intermediate_x = x1 + step_x * i
        intermediate_y = y1 + step_y * i
        intermediate_points.append((intermediate_x, intermediate_y))
        points = [point1] + intermediate_points + [point2]
    if coordinates == 'real':
        points = np.array(points, dtype=float)
        return points, step_x, step_y
    points = np.array(points, dtype=int)
    return points, int(step_x), int(step_y)


def _get_channel_arrays_from_jpg_file(file, channel):
    channel_array = plt.imread(file)
    if channel == 'all':
        return channel_array
    return channel_array[:, :, channel]


def _get_exif_entry(filename, tag):
    with open(filename, 'rb') as f:
        exif = exifread.process_file(f, details=False, stop_tag=tag)
        if f"EXIF {tag}" not in exif:
            raise ValueError("No EXIF entry")
        exif_entry = exif[f"EXIF {tag}"]
    return str(exif_entry)


def _get_capture_date_time(file):
    capture_time = _get_exif_entry(file, "DateTimeOriginal")
    return datetime.strptime(capture_time, '%Y:%m:%d %H:%M:%S')
