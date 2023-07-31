import matplotlib.pyplot as plt
from RadianceMethod import RadianceMethod

test = RadianceMethod()

test.image_name_string = 'DSC{:05d}.JPG'
test.image_dir = '/Users/kristianboerger/repos/RadianceMethod/test_images'

# test.image_dir = '/Volumes/N-1/22_04_27/V006/sony_1/'

test.number_of_rois = 100
test.reference_image_id = 8711
test.first_image_id = 8711
test.last_image_id = 8713
test.skip_n_images = 0

test.dark_roi_pixel_bounds = ((2044, 2015), (2044, 665))
test.light_roi_pixel_bounds = ((2083, 2015), (2083, 665))

test.calc_roi_pixel_positions()
test.plot_reference_image_with_roi()
test.process_image_data()

