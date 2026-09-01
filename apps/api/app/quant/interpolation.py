import numpy as np
from scipy.interpolate import Rbf, griddata


def linear_interpolate_2d(
    known_x: list[float],
    known_y: list[float],
    known_z: list[float],
    query_x: list[float],
    query_y: list[float],
) -> list[float]:
    points = np.column_stack([known_x, known_y])
    values = np.array(known_z)
    query_points = np.column_stack([query_x, query_y])

    result = griddata(points, values, query_points, method="linear")
    nan_mask = np.isnan(result)
    if np.any(nan_mask):
        nearest = griddata(points, values, query_points, method="nearest")
        result[nan_mask] = nearest[nan_mask]

    return result.tolist()


def cubic_interpolate_2d(
    known_x: list[float],
    known_y: list[float],
    known_z: list[float],
    query_x: list[float],
    query_y: list[float],
) -> list[float]:
    points = np.column_stack([known_x, known_y])
    values = np.array(known_z)
    query_points = np.column_stack([query_x, query_y])

    result = griddata(points, values, query_points, method="cubic")
    nan_mask = np.isnan(result)
    if np.any(nan_mask):
        linear_fallback = griddata(points, values, query_points, method="linear")
        result[nan_mask] = linear_fallback[nan_mask]
        nan_mask = np.isnan(result)
    if np.any(nan_mask):
        nearest = griddata(points, values, query_points, method="nearest")
        result[nan_mask] = nearest[nan_mask]

    return result.tolist()


def rbf_interpolate_2d(
    known_x: list[float],
    known_y: list[float],
    known_z: list[float],
    query_x: list[float],
    query_y: list[float],
    function: str = "multiquadric",
    smooth: float = 0.0,
) -> list[float]:
    rbf = Rbf(known_x, known_y, known_z, function=function, smooth=smooth)
    result = rbf(np.array(query_x), np.array(query_y))
    return np.asarray(result).tolist()


INTERPOLATION_METHODS = {
    "linear": linear_interpolate_2d,
    "cubic": cubic_interpolate_2d,
    "rbf": rbf_interpolate_2d,
}
