import os
import numpy as np
import matplotlib.pyplot as plt

import csv
from tqdm import tqdm

class RadianceMethod:
    def __init__(self):
        self.image_dir = None
        self.reference_image_id = None
        self.first_image_id = None
        self.last_image_id = None
        self.skip_n_images = 0
        self.image_name_string = None
        self.image_series = None
        self.dark_roi_bounds = None
        self.light_roi_bounds = None
        self.number_of_rois = None
        self.roi_width = 10
        self.experiment_name = 'test'

    def calc_roi_positions(self):
        self.dark_roi_coordinates,self.dark_roi_dx, self.dark_roi_dy = divide_line(self.dark_roi_bounds[0], self.dark_roi_bounds[1], self.number_of_rois)
        self.light_roi_coordinates, self.light_roi_dx, self.light_roi_dy = divide_line(self.light_roi_bounds[0], self.light_roi_bounds[1], self.number_of_rois)


    def get_image_data(self, image_id, channel=0):
        filename = self.image_name_string.format(image_id)
        file_path = os.path.join(self.image_dir, filename)
        image_array = get_channel_arrays_from_jpg_file(file_path, channel)
        return image_array

    def extract_pixel_values(self, image_array):# TODO: outsource in single function
        roi_dark_values = []
        roi_light_values = []

        for coord in self.dark_roi_coordinates[:-1]:
            y_bottom = coord[1]
            y_top = y_bottom + self.light_roi_dy
            x_left = coord[0] - int(self.roi_width/2)
            x_right = x_left + self.roi_width
            roi = image_array[y_top:y_bottom, x_left:x_right]
            roi_mean = roi.mean()
            roi_dark_values.append(roi_mean)

        for coord in self.light_roi_coordinates[:-1]:
            y_bottom = coord[1]
            y_top = y_bottom + +self.light_roi_dy
            x_left = coord[0] - int(self.roi_width/2)
            x_right = x_left + self.roi_width
            roi = image_array[y_top:y_bottom, x_left:x_right]
            roi_mean = roi.mean()
            roi_light_values.append(roi_mean)

        return np.array(roi_dark_values), np.array(roi_light_values)

    def process_image_data(self): #test comment
        self.image_series = range(self.first_image_id, self.last_image_id, self.skip_n_images+1)
        print(f"Processing {self.last_image_id-self.first_image_id} images...")
        for channel in [0,1,2]:
            filename_1 = f'{self.experiment_name}_dark_values_channel_{channel}.csv'
            filename_2 = f'{self.experiment_name}_light_values_channel_{channel}.csv'

            with open(filename_1, 'w') as csvfile_1, open(filename_2, 'w') as csvfile_2:
                writer_1 = csv.writer(csvfile_1)
                writer_2 = csv.writer(csvfile_2)

                header = [f"ROI {i}" for i in range(self.number_of_rois)]
                writer_1.writerow(header)
                writer_2.writerow(header)
                for image_id in tqdm(self.image_series):
                    image_array = self.get_image_data(image_id, channel)
                    roi_dark_values, roi_light_values = self.extract_pixel_values(image_array)
                    writer_1.writerow(roi_dark_values)
                    writer_2.writerow(roi_light_values)
                print(f"Channel {channel} processed!")


    def plot_reference_image_with_roi(self):
        image_array = self.get_image_data(self.reference_image_id)
        plt.imshow(image_array)
        plt.plot(self.dark_roi_coordinates[:,0], self.dark_roi_coordinates[:,1], marker='.', color='red', label='Dark')
        plt.plot(self.light_roi_coordinates[:,0], self.light_roi_coordinates[:,1], marker='.', color='blue', label='Light')
        plt.legend()
        plt.show()

def divide_line(point1, point2, n):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the step size for x and y coordinates
    step_x = int((x2 - x1) / n)
    step_y = int((y2 - y1) / n)

    # Generate intermediate points
    intermediate_points = []
    for i in range(1, n):
        intermediate_x = x1 + step_x * i
        intermediate_y = y1 + step_y * i
        intermediate_points.append((intermediate_x, intermediate_y))
        points = np.array([point1] + intermediate_points + [point2], dtype=int)

    return points, step_x, step_y

def get_channel_arrays_from_jpg_file(file, channel):
    channel_array = plt.imread(file)
    return channel_array[:, :, channel]