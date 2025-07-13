import logging
import os
from pathlib import Path
import pycolmap
from pycolmap import logging as colmap_logging

from utils import ensure_dir

def run_structure_from_motion(input_dir: Path, workspace_dir: Path, options: dict):
    """Run Structure from Motion and Multi-View Stereo using pycolmap."""
    logger = logging.getLogger(__name__)
    logger.info("Initializing COLMAP workspace...")

    # Ensure directories
    database_path = workspace_dir / "database.db"
    image_dir = input_dir
    sparse_dir = workspace_dir / "sparse"
    dense_dir = workspace_dir / "dense"
    ensure_dir(workspace_dir)
    ensure_dir(sparse_dir)
    ensure_dir(dense_dir)

    logger.info(f"Database path: {database_path}")
    logger.info(f"Image directory: {image_dir}")
    logger.info(f"Sparse reconstruction directory: {sparse_dir}")
    logger.info(f"Dense reconstruction directory: {dense_dir}")

    # Step 1: Feature Extraction
    logger.info("Extracting features from images...")
    pycolmap.extract_features(
        database_path=database_path,
        image_path=image_dir,
        camera_mode=pycolmap.CameraMode.AUTO,
        camera_model="OPENCV",
        sift_options=options['feature_extraction']
    )
    logger.info("Feature extraction completed.")

    # Step 2: Feature Matching
    logger.info("Matching features between images...")
    pycolmap.match_features(
        database_path=database_path,
        sift_matching_options=options['feature_matching']
    )
    logger.info("Feature matching completed.")

    # Step 3: Sparse Reconstruction (SfM)
    logger.info("Performing sparse reconstruction (Structure from Motion)...")
    pycolmap.incremental_mapping(
        database_path=database_path,
        image_path=image_dir,
        output_path=sparse_dir,
        mapper_options=options['mapper']
    )
    logger.info("Sparse reconstruction completed.")

    # Step 4: Dense Reconstruction (MVS)
    logger.info("Performing dense reconstruction (Multi-View Stereo)...")
    pycolmap.image_undistorter(
        image_path=image_dir,
        input_path=sparse_dir / "0",
        output_path=dense_dir,
        output_type="COLMAP"
    )
    logger.info("Image undistortion completed.")

    logger.info("Running patch match stereo...")
    pycolmap.patch_match_stereo(
        workspace_path=dense_dir,
        options=options['mvs']
    )
    logger.info("Patch match stereo completed.")

    logger.info("Fusing depth maps to point cloud...")
    pycolmap.stereo_fusion(
        workspace_path=dense_dir,
        output_path=workspace_dir / "fused.ply"
    )
    logger.info("Dense point cloud fusion completed.")

    return workspace_dir / "fused.ply"
