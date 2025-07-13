import logging
from pathlib import Path
import numpy as np
import cv2
import open3d as o3d
from typing import Tuple

def compute_bounds(pcd: o3d.geometry.PointCloud) -> Tuple[float, float, float, float]:
    """Compute the 2D bounds (min_x, max_x, min_y, max_y) of the point cloud."""
    points = np.asarray(pcd.points)
    min_x, max_x = np.min(points[:, 0]), np.max(points[:, 0])
    min_y, max_y = np.min(points[:, 1]), np.max(points[:, 1])
    return min_x, max_x, min_y, max_y

def rasterize_to_2d_map(pcd: o3d.geometry.PointCloud, output_path: Path, pixels_per_meter: float):
    """Project the 3D point cloud to 2D and rasterize to an image."""
    logger = logging.getLogger(__name__)
    logger.info("Starting rasterization of point cloud to 2D map...")

    # Compute bounds
    min_x, max_x, min_y, max_y = compute_bounds(pcd)
    width_m = max_x - min_x
    height_m = max_y - min_y
    logger.info(f"Point cloud bounds: width={width_m:.2f}m, height={height_m:.2f}m")

    # Compute image dimensions
    width_px = int(width_m * pixels_per_meter)
    height_px = int(height_m * pixels_per_meter)
    if width_px <= 0 or height_px <= 0:
        logger.error("Invalid image dimensions calculated.")
        raise ValueError("Image dimensions must be positive.")
    logger.info(f"Output image dimensions: {width_px}x{height_px} pixels")

    # Initialize image
    image = np.zeros((height_px, width_px, 3), dtype=np.uint8)

    # Get points and colors
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors) * 255  # Open3D colors are in [0,1], convert to [0,255]

    # Project points to image coordinates
    logger.info("Projecting 3D points to 2D image coordinates...")
    x_coords = ((points[:, 0] - min_x) * pixels_per_meter).astype(int)
    y_coords = ((points[:, 1] - min_y) * pixels_per_meter).astype(int)

    # Filter out points outside image bounds
    valid = (x_coords >= 0) & (x_coords < width_px) & (y_coords >= 0) & (y_coords < height_px)
    x_coords = x_coords[valid]
    y_coords = y_coords[valid]
    colors = colors[valid]
    logger.info(f"Projected {len(x_coords)} points within image bounds.")

    # Assign colors to image (last point wins in case of overlap)
    for x, y, color in zip(x_coords, y_coords, colors):
        image[height_px - 1 - y, x] = color  # Flip y-axis so that higher y in 3D is higher in image

    # Save the image
    logger.info(f"Saving output image to {output_path}...")
    cv2.imwrite(str(output_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    logger.info("Rasterization completed and image saved.")
