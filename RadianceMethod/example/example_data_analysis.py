# Import the DataAnalysis class from the RadianceMethod.analysis.DataAnalysis module
from RadianceMethod.analysis.DataAnalysis import DataAnalysis

# Create an instance of the DataAnalysis class
data_analysis = DataAnalysis()

# Display the documentation string for the DataAnalysis class
print(data_analysis.__doc__)

# Set the directory path where the analysis results will be stored
data_analysis.results_dir = 'example_results'

# Set the name of the experiment
data_analysis.experiment_name = 'Testexperiment'

# Load experimental results and ROI coordinates from files
data_analysis.load_result_data()

# Calculate intensities based on experimental results and save them to CSV files
data_analysis.calc_intensities()

# Calculate extinction coefficients from intensities and distances, and save them to CSV files
data_analysis.calc_extinction_coefficients()
