import matplotlib.pyplot as plt
from time import time
from RadianceMethod import RadianceMethod

st = time()
test = RadianceMethod()

test.image_name_string = 'DSC{:05d}.JPG'
# test.image_dir = '/Users/kristianboerger/repos/RadianceMethod/test_images'

test.image_dir = '/Volumes/N-1/22_04_27/V006/sony_1/'

test.number_of_rois = 10
test.reference_image_id = 4237
test.first_image_id = 4237
test.last_image_id = 5237
test.skip_n_images = 0

test.dark_roi_bounds = ((2044, 2015), (2044,665))
test.light_roi_bounds = ((2083, 2015), (2083,665))

test.calc_roi_positions()
test.plot_reference_image_with_roi()
test.process_image_data()
et = time.time()
print(et-st)