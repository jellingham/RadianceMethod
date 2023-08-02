import numpy as np
import matplotlib.pyplot as plt
import rawpy
import exifread
from datetime import datetime

def get_channel_arrays_from_jpg_file(file, channel):
    channel_array = plt.imread(file)
    return channel_array[:, :, channel]

def get_channel_arrays_from_raw_file(file, channel):
    with rawpy.imread(file) as raw:
        data = raw.raw_image_visible.copy()
        filter_array = raw.raw_colors_visible
        black_level = raw.black_level_per_channel[0]
        white_level = raw.white_level
        channel_array = data.astype(np.int16) - black_level
        channel_array = (channel_array * (white_level / (white_level - black_level))).astype(np.int16)
        channel_array = np.clip(channel_array, 0, white_level)
        channel_0_array = np.where(filter_array == 0, channel_array, 0)
        channel_1_array = np.where((filter_array == 1) | (filter_array == 3), channel_array, 0)
        channel_2_array = np.where(filter_array == 2, channel_array, 0)
        all_channel_array = [channel_0_array, channel_1_array, channel_2_array]
        return all_channel_array[channel]


def _get_exif_entry(filename, tag):
    with open(filename, 'rb') as f:
        exif = exifread.process_file(f, details=False, stop_tag=tag)
        if f"EXIF {tag}" not in exif:
            raise ValueError("No EXIF entry")
        exif_entry = exif[f"EXIF {tag}"]
    return str(exif_entry)


def get_capture_date_time(file):
    capture_time = _get_exif_entry(file, "DateTimeOriginal")
    return datetime.strptime(capture_time, '%Y:%m:%d %H:%M:%S')