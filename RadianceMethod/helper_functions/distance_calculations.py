import numpy as np

def _divide_line_2d(point1, point2, n):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the step size for x and y coordinates
    step_x = (x2 - x1) / n
    step_y = (y2 - y1) / n

    # Generate intermediate points
    intermediate_points = []
    for i in range(1, n):
        intermediate_x = x1 + step_x * i
        intermediate_y = y1 + step_y * i
        intermediate_points.append((intermediate_x, intermediate_y))
    points = [point1] + intermediate_points
    points = np.array(points, dtype=int)
    return points, int(step_x), int(step_y)


def _divide_line_3d(point1, point2, n):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    # Calculate the step size for x, y, and z coordinates
    step_x = (x2 - x1) / n
    step_y = (y2 - y1) / n
    step_z = (z2 - z1) / n

    # Generate intermediate points
    intermediate_points = []
    for i in range(1, n):
        intermediate_x = x1 + step_x * i
        intermediate_y = y1 + step_y * i
        intermediate_z = z1 + step_z * i
        intermediate_points.append((intermediate_x, intermediate_y, intermediate_z))
    points = [point1] + intermediate_points
    points = np.array(points)
    return points, step_x, step_y, step_z


def _calc_distance_3d(point1, point2):
    """
    Calculate the Euclidean distance between two 3D points.

    Parameters:
        point1 (tuple or ndarray): A tuple (x1, y1, z1) or ndarray [x1, y1, z1] representing the coordinates of the first point.
        point2 (tuple or ndarray): A tuple (x2, y2, z2) or ndarray [x2, y2, z2] representing the coordinates of the second point.

    Returns:
        float: The Euclidean distance between the two 3D points.
    """
    return np.linalg.norm(np.array(point2) - np.array(point1))