from RadianceMethod import RadianceMethod

test = RadianceMethod()
test.set_experiment_name("Testexperiment")
test.set_image_dir('/Users/kristianboerger/repos/RadianceMethod/test_images')
test.set_camera_position(0,0,0)
test.set_image_series(8711,8713)
test.set_image_name_string('DSC{:05d}.JPG')
test.set_reference_image_id(8711)
test.show_reference_image()
test.set_dark_roi_pixel_bounds((2044, 2015), (2044, 665))
test.set_light_roi_pixel_bounds((2083, 2015), (2083, 665))
test.set_roi_parameters(10, 100)
test.set_dark_roi_real_bounds((0,4,0),(0,4,3))
test.set_light_roi_real_bounds((0.1,4,0),(0.1,4,3))
test._calc_roi_pixel_positions()
test._calc_roi_real_positions()
test._calc_roi_camera_real_distances()
test.plot_reference_image_with_rois()
test.process_image_data()
