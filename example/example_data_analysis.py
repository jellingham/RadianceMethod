# Import the DataAnalysis class from the RadianceMethod.analysis.DataAnalysis module
from RadianceMethod.analysis.DataAnalysis import DataAnalysis
# Import the plot_ec_all class from RadianceMethod.post_processing.results_plots
from RadianceMethod.post_processing.results_plots import plot_ec_all

#Set directory for files to save into
results_dir = 'example_results'
#Set name of experiment and analysis e.g., Test_Camera_Location_File type
exp_name = 'Testexperiment'
#Plot limits
x_min = 0
x_max = 10
y_min = -0.2
y_max = 0.5

# Create an instance of the DataAnalysis class
data_analysis = DataAnalysis()

# Display the documentation string for the DataAnalysis class
print(data_analysis.__doc__)

# Set the directory path where the analysis results will be stored
data_analysis.results_dir = results_dir

# Set the name of the experiment
data_analysis.experiment_name = exp_name

# Load experimental results and ROI coordinates from files
data_analysis.load_result_data()

# Calculate intensities based on experimental results and save them to CSV files
data_analysis.calc_intensities()

# Calculate extinction coefficients from intensities and distances, and save them to CSV files
data_analysis.calc_extinction_coefficients()

#Call plot loop for all 3 channels
plot_ec_all(results_dir=results_dir, exp_name=exp_name, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)