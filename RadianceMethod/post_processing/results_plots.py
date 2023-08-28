import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_ec_all(results_dir, exp_name, x_min, x_max, y_min, y_max):
    for channel in [0,1,2]:
        data_path = os.path.join(results_dir,f'extinction_coefficients_channel_{channel}.csv')
        plot_ec(data_path, results_dir, exp_name, channel, x_min, x_max, y_min, y_max)

def plot_ec(data_path, results_dir, exp_name, channel, x_min, x_max, y_min, y_max):
    data = pd.read_csv(data_path, skiprows=3)
    data['Timedelta'] = pd.to_timedelta(data['Timedelta'])
    data['Timedelta_seconds'] = data['Timedelta'].dt.total_seconds()
    x = data['Timedelta_seconds']
    y = data.iloc[:, 3:]
    plt.plot(x, y)

    plt.xlabel('Time [s]')
    plt.ylabel('Extinction Coefficient [1/m]')
    plt.title(f'{exp_name} EC Ch{channel}'.replace('_',' '))
    plt.grid()
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    output_file_path = os.path.join(results_dir,f'{exp_name}_plot_ec_channel_{channel}.pdf')
    plt.savefig(output_file_path)
    plt.close()
    print(f'Plot_EC_Ch{channel} complete')

