# Lawn Mapper

A Python tool to generate a top-down, colored map of your lawn from video frames using photogrammetry and point cloud processing.

## Overview

Lawn Mapper processes a series of video frames taken while walking over your lawn to create a bird's-eye view map. This tool is designed for cases where the camera is pointed downward, capturing only parts of the lawn in each frame, and uses dense frame extraction to ensure overlap between images for accurate reconstruction.

## Installation

### Prerequisites

- Python 3.8 or higher
- `ffmpeg` (for frame extraction from video, assumed to be installed)

### Setup

1. Clone this repository or download the project files.
2. Navigate to the project directory:
   ```bash
   cd lawn_mapper
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

**Note**: `pycolmap` may require additional setup depending on your system. Refer to the [pycolmap documentation]() for installation instructions if you encounter issues.

## Usage

### Preparing Input

Extract frames from your video using `ffmpeg` or another tool. For example, to extract every 10th frame:

```bash
ffmpeg -i input_video.mp4 -vf "select='not(mod(n,10))'" -vsync vfr frames/frame_%04d.png
```

Place the extracted frames in a directory, e.g., `frames/`.

### Running the Pipeline

Run the Lawn Mapper pipeline with the following command:

```bash
cd lawn_mapper
python main.py ../frames --output-dir ../ --workspace-dir ../workspace --pixels-per-meter 100 --verbose
```

#### Arguments

- `input_dir`: Directory containing the video frames (required).
- `--output-dir`: Directory to save the output map (default: `output`).
- `--workspace-dir`: Directory for temporary workspace files (default: `workspace`).
- `--pixels-per-meter`: Resolution of the output map in pixels per meter (default: 100.0).
- `--verbose`: Enable detailed logging for debugging (optional).

#### Output

The pipeline will generate a top-down map of your lawn as `lawn_map.png` in the specified output directory.

### Pipeline Steps

1. **Structure from Motion (SfM) and Multi-View Stereo (MVS)**: Uses `pycolmap` to extract features, match images, estimate camera poses, and generate a dense colored point cloud.
2. **Ground Plane Fitting and Alignment**: Uses `open3d` to fit a plane to the ground and align the point cloud accordingly.
3. **Rasterization**: Projects the aligned point cloud to a 2D plane and creates a color image using `numpy` and `opencv-python`.

## Project Structure

- `main.py`: Entry point for the pipeline, parses arguments, and orchestrates the process.
- `config.py`: Configuration settings for resolution, COLMAP options, and RANSAC parameters.
- `sfm_pipeline.py`: Handles SfM and MVS using `pycolmap`.
- `pointcloud_tools.py`: Processes the point cloud with `open3d` for plane fitting and alignment.
- `rasterizer.py`: Converts the 3D point cloud to a 2D image.
- `utils.py`: Utility functions for logging and directory management.

## Troubleshooting

- **Memory Issues**: Processing a large number of frames can be memory-intensive. Reduce the number of frames or adjust the `max_image_size` in `config.py` under `COLMAP_OPTIONS['mvs']`.
- **Plane Fitting**: If the ground plane fitting fails or looks incorrect, adjust the `max_distance` or `min_points` in `RANSAC_OPTIONS` in `config.py`.
- **Installation Errors**: Ensure all dependencies are installed correctly. `pycolmap` and `open3d` may require system-specific libraries.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if applicable).

## Acknowledgments

This tool leverages open-source libraries like `pycolmap` and `open3d` for photogrammetry and 3D processing. Special thanks to their communities for providing robust tools for such tasks.
