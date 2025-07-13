import logging
from pathlib import Path
import numpy as np
import open3d as o3d

def load_pointcloud(pointcloud_path: Path) -> o3d.geometry.PointCloud:
    """Load a point cloud from a PLY file."""
    logger = logging.getLogger(__name__)
    logger.info(f"Loading point cloud from {pointcloud_path}...")
    pcd = o3d.io.read_point_cloud(str(pointcloud_path))
    if not pcd.has_points():
        logger.error("Loaded point cloud is empty.")
        raise ValueError("Point cloud is empty.")
    logger.info(f"Loaded point cloud with {len(pcd.points)} points.")
    return pcd

def fit_ground_plane(pcd: o3d.geometry.PointCloud, options: dict) -> tuple:
    """Fit a ground plane to the point cloud using RANSAC."""
    logger = logging.getLogger(__name__)
    logger.info("Fitting ground plane using RANSAC...")
    plane_model, inliers = pcd.segment_plane(
        distance_threshold=options['max_distance'],
        ransac_n=3,
        num_iterations=options['num_iterations']
    )
    if len(inliers) < options['min_points']:
        logger.warning(f"Only {len(inliers)} inliers found for ground plane. May not be reliable.")
    else:
        logger.info(f"Ground plane fitted with {len(inliers)} inlier points.")
    return plane_model, inliers

def align_pointcloud(pcd: o3d.geometry.PointCloud, plane_model: np.ndarray) -> o3d.geometry.PointCloud:
    """Align the point cloud so that the ground plane is parallel to the XY plane."""
    logger = logging.getLogger(__name__)
    logger.info("Aligning point cloud to ground plane...")

    # Extract plane normal
    a, b, c, d = plane_model
    normal = np.array([a, b, c])
    normal = normal / np.linalg.norm(normal)

    # Target normal (z-axis)
    target_normal = np.array([0, 0, 1])

    # Compute rotation axis and angle
    axis = np.cross(normal, target_normal)
    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-6:
        logger.info("Ground plane already aligned with XY plane.")
        return pcd
    axis = axis / axis_norm
    angle = np.arccos(np.dot(normal, target_normal))

    # Compute rotation matrix
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    ux, uy, uz = axis
    rotation_matrix = np.array([
        [cos_a + ux*ux*(1-cos_a), ux*uy*(1-cos_a) - uz*sin_a, ux*uz*(1-cos_a) + uy*sin_a],
        [uy*ux*(1-cos_a) + uz*sin_a, cos_a + uy*uy*(1-cos_a), uy*uz*(1-cos_a) - ux*sin_a],
        [uz*ux*(1-cos_a) - uy*sin_a, uz*uy*(1-cos_a) + ux*sin_a, cos_a + uz*uz*(1-cos_a)]
    ])

    # Apply rotation
    points = np.asarray(pcd.points)
    rotated_points = np.dot(points, rotation_matrix.T)
    pcd.points = o3d.utility.Vector3dVector(rotated_points)

    # Translate so that the plane passes through origin (z=0)
    centroid = pcd.get_center()
    translation = np.array([0, 0, centroid[2]])
    pcd.translate(-translation)

    logger.info("Point cloud aligned to ground plane.")
    return pcd
