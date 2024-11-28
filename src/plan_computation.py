import typing as T
import math

import numpy as np

from src.data_model import Camera, DatasetSpec, Waypoint
from src.camera_utils import compute_image_footprint_on_surface, compute_ground_sampling_distance

def compute_distance_between_images(camera: Camera, dataset_spec: DatasetSpec) -> np.ndarray:
    """Compute the distance between images in the horizontal and vertical directions for specified overlap and sidelap.

    Args:
        camera (Camera): Camera model used for image capture.
        dataset_spec (DatasetSpec): user specification for the dataset.

    Returns:
        float: The distance between images in the horizontal direction.
        float: The distance between images in the vertical direction.
    """
    #This function determines the area captured in each image, which directly affects the number of images needed to cover the target area."
    footprint_x, footprint_y = compute_image_footprint_on_surface(camera, dataset_spec.height) 

    distance_x = footprint_x * (1 - dataset_spec.overlap)
    distance_y = footprint_y * (1 - dataset_spec.sidelap)

    return np.array([distance_x, distance_y])



def compute_speed_during_photo_capture(camera: Camera, dataset_spec: DatasetSpec, allowed_movement_px: float = 1) -> float:
    """Compute the speed of drone during an active photo capture to prevent more than 1px of motion blur.

    Args:
        camera (Camera): Camera model used for image capture.
        dataset_spec (DatasetSpec): user specification for the dataset.
        allowed_movement_px (float, optional): The maximum allowed movement in pixels. Defaults to 1 px.

    Returns:
        float: The speed at which the drone should move during photo capture.
    """
    gsd = compute_ground_sampling_distance(camera, dataset_spec.height)
    return gsd * allowed_movement_px / (dataset_spec.exposure_time_ms / 1000)


def generate_photo_plan_on_grid(camera: Camera, dataset_spec: DatasetSpec) -> T.List[Waypoint]:
    """Generate the complete photo plan as a list of waypoints in a lawn-mower pattern.

    Args:
        camera (Camera): Camera model used for image capture.
        dataset_spec (DatasetSpec): user specification for the dataset.

    Returns:
        List[Waypoint]: scan plan as a list of waypoints.

    """
    # assumptions made:
    # - only the area to be scanned is covered, no additional surrounding area is covered

    # gives the distance after overlap
    distance_x, distance_y = compute_distance_between_images(camera, dataset_spec)

    num_of_images_x = math.ceil(dataset_spec.scan_dimension_x / distance_x)
    num_of_images_y = math.ceil(dataset_spec.scan_dimension_y / distance_y)

    speed = compute_speed_during_photo_capture(camera, dataset_spec)

    footprint_x, footprint_y = compute_image_footprint_on_surface(
        camera, dataset_spec.height
    )
    dx = footprint_x / 2
    dy = footprint_y / 2

    waypoints = []

    for ny in range(num_of_images_y):
        y = ny * distance_y
        surface_coord_y1 = y - dy
        surface_coord_y2 = y + dy

        for nx in range(num_of_images_x):
            if ny % 2 == 0:
                x = nx * distance_x
            else:
                x = (num_of_images_x - nx - 1) * distance_x

            surface_coord_x1 = x - dx
            surface_coord_x2 = x + dx
            waypoints.append(
                Waypoint(
                    x,
                    y,
                    surface_coord_x1,
                    surface_coord_x2,
                    surface_coord_y1,
                    surface_coord_y2,
                    dataset_spec.height,
                    speed
                )
            )

    return waypoints