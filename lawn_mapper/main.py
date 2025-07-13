import argparse
import logging
import sys
import os
from pathlib import Path

from sfm_pipeline import run_structure_from_motion
from pointcloud_tools import load_pointcloud, fit_ground_plane, align_pointcloud
from rasterizer import rasterize_to_2d_map
from config import CONFIG, COLMAP_OPTIONS, RANSAC_OPTIONS
from utils import (
    setup_logging,
    ensure_dir,
    download_video,
    extract_frames,
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Lawn Mapper: Generate a top-down map of your lawn from video frames.")
    parser.add_argument("input_dir", type=Path, help="Directory to store or read video frames")
    parser.add_argument("--video-url", type=str, default=None, help="Direct URL to the input video")
    parser.add_argument("--frame-step", type=int, default=10, help="Extract every n-th frame when downloading a video")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Output directory for results")
    parser.add_argument("--workspace-dir", type=Path, default=Path("workspace"), help="Workspace directory for temporary files")
    parser.add_argument("--pixels-per-meter", type=float, default=CONFIG['pixels_per_meter'], help="Resolution of the output map in pixels per meter")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    """Main function to run the lawn mapping pipeline."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Lawn Mapper pipeline...")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Workspace directory: {args.workspace_dir}")
    
    # Ensure directories exist
    ensure_dir(args.output_dir)
    ensure_dir(args.workspace_dir)
    ensure_dir(args.input_dir)
    logger.info("Directories initialized.")

    if args.video_url:
        video_path = args.workspace_dir / "input_video.mp4"
        download_video(args.video_url, video_path)
        extract_frames(video_path, args.input_dir, step=args.frame_step)
    
    # Step 1: Structure from Motion and Multi-View Stereo with COLMAP
    pointcloud_path = args.workspace_dir / "fused.ply"
    if not pointcloud_path.exists():
        logger.info("Running Structure from Motion and Multi-View Stereo...")
        run_structure_from_motion(
            input_dir=args.input_dir,
            workspace_dir=args.workspace_dir,
            options=COLMAP_OPTIONS
        )
        logger.info("SfM and MVS completed. Dense point cloud generated.")
    else:
        logger.info("Dense point cloud already exists. Skipping SfM and MVS.")
    
    # Step 2: Load and process point cloud
    logger.info("Loading point cloud...")
    pcd = load_pointcloud(pointcloud_path)
    logger.info(f"Point cloud loaded with {len(pcd.points)} points.")
    
    # Step 3: Fit ground plane and align point cloud
    logger.info("Fitting ground plane using RANSAC...")
    plane_model, inliers = fit_ground_plane(pcd, RANSAC_OPTIONS)
    logger.info(f"Ground plane fitted with {len(inliers)} inlier points.")
    
    logger.info("Aligning point cloud to ground plane...")
    aligned_pcd = align_pointcloud(pcd, plane_model)
    logger.info("Point cloud alignment completed.")
    
    # Step 4: Rasterize to 2D map
    logger.info("Rasterizing point cloud to 2D map...")
    output_image_path = args.output_dir / "lawn_map.png"
    rasterize_to_2d_map(
        pcd=aligned_pcd,
        output_path=output_image_path,
        pixels_per_meter=args.pixels_per_meter
    )
    logger.info(f"Top-down lawn map saved to {output_image_path}")
    
    logger.info("Lawn Mapper pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
