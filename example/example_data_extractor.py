# Import the DataExtractor class from the RadianceMethod.processing.DataExtractor module
from RadianceMethod.processing.DataExtractor import DataExtractor

# Create an instance of the DataExtractor class
data_extractor = DataExtractor()

# Display the documentation string for the DataExtractor class
print(data_extractor.__doc__)

# Set various parameters for the DataExtractor instance
data_extractor.set_experiment_name("Testexperiment")
data_extractor.set_image_dir('example_images')
data_extractor.set_results_dir('example_results')

# Set the real-world position of the camera (x=0, y=0, z=0)
data_extractor.set_camera_position(0, 0, 0)

# Set the range of image IDs for the image series (9682 to 9686, skipping every 1 image)
data_extractor.set_image_series(9682, 9686)

# Set the image file format to 'raw'
data_extractor.set_image_file_format('jpg')

# Set the template string for forming image filenames with image IDs
data_extractor.set_image_name_string('DSC{:05d}.jpg')

# Set the ID of the reference image used for time delta calculation
data_extractor.set_reference_image_id(9682)

# Display the reference image for channel 1
data_extractor.show_reference_image(1)

# Set pixel bounds for the dark and light ROIs
data_extractor.set_dark_roi_pixel_bounds((2440, 1984), (2440, 557))
data_extractor.set_light_roi_pixel_bounds((2483, 1984), (2483, 557))

# Set parameters for ROIs: pixel width and number of ROIs
data_extractor.set_roi_parameters(10, 100)

# Set real-world bounds for the dark and light ROIs
data_extractor.set_dark_roi_real_bounds((0, 4, 0), (0, 4, 3.37))
data_extractor.set_light_roi_real_bounds((0, 4, 0), (0, 4, 3.37))

# Calculate ROI positions and distances in both pixel and real-world units
data_extractor.calc_geometrics()

# Set heights for height markers (1m, 2m, 3m)
data_extractor.set_height_marker_heights([1, 2, 3])

# Plot the reference image with ROIs for channel 1
data_extractor.plot_reference_image_with_rois(1)

# Process image data for the specified image series
data_extractor.process_image_data()

# Write real-world coordinates of ROIs to CSV files
data_extractor.write_roi_real_coordinates()

# Write camera-to-ROI real distances to CSV files
data_extractor.write_roi_camera_to_roi_real_distances()
