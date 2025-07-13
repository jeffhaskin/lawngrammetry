import logging
import os
from pathlib import Path
import pycolmap
from pycolmap import logging as colmap_logging

from utils import ensure_dir


def _dict_to_options(data: dict, options_cls, prefix: str = ""):
    """Convert a dictionary of option values to a pycolmap options object."""
    opts = options_cls()
    for key, value in data.items():
        if prefix and key.startswith(prefix):
            key = key[len(prefix):]
        if hasattr(opts, key):
            setattr(opts, key, value)
    return opts

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

    # Prepare option objects
    feat_opts = _dict_to_options(
        options.get('feature_extraction', {}),
        pycolmap.SiftExtractionOptions,
    )
    match_opts = _dict_to_options(
        options.get('feature_matching', {}),
        pycolmap.SiftMatchingOptions,
    )
    mapper_opts = _dict_to_options(
        options.get('mapper', {}),
        pycolmap.IncrementalMapperOptions,
    )
    mvs_opts = _dict_to_options(
        options.get('mvs', {}),
        pycolmap.PatchMatchOptions,
    )

    # Step 1: Feature Extraction
    logger.info("Extracting features from images...")
    pycolmap.extract_features(
        database_path=database_path,
        image_path=image_dir,
        camera_mode=pycolmap.CameraMode.AUTO,
        camera_model="OPENCV",
        sift_options=feat_opts,
    )
    logger.info("Feature extraction completed.")

    # Step 2: Feature Matching
    logger.info("Matching features between images...")
    # pycolmap's API exposes various matching functions depending on the desired
    # strategy.  The previous implementation attempted to call
    # `match_features`, however this function was removed in newer versions of
    # pycolmap.  Exhaustive matching most closely replicates the old behaviour
    # and requires only the SiftMatchingOptions, so we use it here.
    pycolmap.match_exhaustive(
        database_path=database_path,
        sift_options=match_opts,
    )
    logger.info("Feature matching completed.")

    # Step 3: Sparse Reconstruction (SfM)
    logger.info("Performing sparse reconstruction (Structure from Motion)...")
    pycolmap.incremental_mapping(
        database_path=database_path,
        image_path=image_dir,
        output_path=sparse_dir,
        mapper_options=mapper_opts,
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
        options=mvs_opts,
    )
    logger.info("Patch match stereo completed.")

    logger.info("Fusing depth maps to point cloud...")
    pycolmap.stereo_fusion(
        workspace_path=dense_dir,
        output_path=workspace_dir / "fused.ply"
    )
    logger.info("Dense point cloud fusion completed.")

    return workspace_dir / "fused.ply"
