from RadianceMethod.post_processing.results_plots import plot_ec_all

results_dir = 'C:/Users/jpilm/Documents/RadianceMethodResults/V006/V006_Sony1_Left_raw/results/'
exp_name = 'V006_Sony1_Left_raw'
x_min = 0
x_max = 1600
y_min = -0.2
y_max = 0.5

plot_ec_all(results_dir=results_dir, exp_name=exp_name, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)