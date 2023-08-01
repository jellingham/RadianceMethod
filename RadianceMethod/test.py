from RadianceMethod import RadianceMethod

test = RadianceMethod()
test.set_experiment_name("Testexperiment")
test.set_image_dir('/Users/kristianboerger/repos/RadianceMethod/test_images')
test.set_image_series(8711,8713, 'DSC{:05d}.JPG')
test.set_reference_image_id(8711)
test.set_roi_pixel_bounds(((2044, 2015), (2044, 665)),((2083, 2015), (2083, 665)), 10, 100)
test.set_roi_real_bounds(((0,0),(0,3)),((0.1,0),(0.1,3)))
test.calc_roi_pixel_positions()
test.calc_roi_real_positions()
test.plot_reference_image_with_roi()
test.process_image_data()
