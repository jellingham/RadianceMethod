from analysis.DataAnalaysis import DataAnalysis

analysis = DataAnalysis()
analysis.results_dir = '../test_results'
analysis.experiment_name = 'Testexperiment'
analysis.load_result_data()
# analysis.normalise_results()
analysis.calc_intensities()
a=1