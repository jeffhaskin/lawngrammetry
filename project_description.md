# Project Description

## Original Idea

My goal is to walk around my lawn while taking a video. Then I would extract every n frames from the video to use as the input images; that's not important since it's a solved problem. The focus point is that this video wouldn't really have landmarks or really even see the whole object (the lawn) in any one frame, it would be the camera constantly sweeping over the grass as I walked. So, the camera would be able to locate images be comparing to previous n images depending on frame rate or density of frame extraction, but there would not be any frames where the entire lawn was visible since the camera is mostly pointed down at the ground while I walk. My end goal is to be able to produce a bird's eye image of the lawn from above so I can see the shape and where the grass is more or less green like a flat map. Photo Catch is struggling with this use case since it's optimize for capturing objects where the entire object usually fits within frame. I know the math can do it since it's still just comparing overlapping images to each other (the denser the frame extraction, the more overlap there will be between images) and creating a point cloud with color values. But, because most apps assume small object capture, they struggle. I want a program that can do this.

## Math Pipeline and Tech Stack

 📂 **Input**: A folder of video frames (e.g., `frames/`)  
> 🗺️ **Output**: A top-down `lawn_map.png` showing a flattened, colored map of the lawn surface.

* * *

### 🧠 What This Script Will Do (End-to-End):


1.  **Run SfM and MVS with `pycolmap`**:
    
    *   Extract features and match images
        
    *   Estimate camera poses
        
    *   Generate a **dense colored point cloud**
        
2.  **Fit and align the ground plane** using `open3d`.
    
3.  **Project the cloud to 2D and rasterize** into a flat color image using `numpy` and `opencv-python`.
    

* * *

### 🐍 Tools Used (All via `pip install`):


*   `pycolmap` – photogrammetry engine
    
*   `open3d` – point cloud geometry & visualization
    
*   `opencv-python` – image writing
    
*   `numpy` – math
    
*   `ffmpeg` – (you already have for frame extraction)
    

* * *

### 🧱 Deliverable


This script will:

*   Build a COLMAP workspace in a temp dir
    
*   Run feature extraction + matching + mapping
    
*   Create a dense point cloud (`fused.ply`)
    
*   Load, plane-fit, project, and rasterize it
    
*   Save the top-down lawn image
    

---


For a project like this, where we're combining image processing, 3D geometry, and photogrammetry pipelines, it’s worth organizing your code into **modular Python files (modules)** that mirror the pipeline stages. This improves readability, testing, and long-term flexibility.

* * *

### ✅ Suggested File Structure (for your lawn mapping project)

    lawn_mapper/
    │
    ├── main.py                  # Entry point: parses args and runs the full pipeline
    ├── config.py                # Central location for constants, paths, resolution
    │
    ├── sfm_pipeline.py          # SfM + MVS steps using pycolmap
    ├── pointcloud_tools.py      # Plane fitting, rotation, transformations
    ├── rasterizer.py            # Projects cloud to plane, rasterizes to 2D image
    │
    ├── utils.py                 # Small helper functions (e.g., logging, paths)
    ├── requirements.txt         # Python dependencies
    └── README.md                # Usage & setup instructions
    

* * *

### 🧠 What Goes Where?

#### `main.py`

*   Top-level script:
    
    *   Parses CLI args (`argparse`)
        
    *   Calls `run_structure_from_motion()`
        
    *   Calls `generate_lawn_map()`
        
    *   Logs outputs
        

#### `sfm_pipeline.py`

*   Encapsulates:
    
    *   Feature extraction
        
    *   Matching
        
    *   SfM (camera pose estimation)
        
    *   MVS (dense point cloud)
        
*   Uses `pycolmap` internally
    

#### `pointcloud_tools.py`

*   Loads `.ply` file using `open3d`
    
*   Fits plane using RANSAC
    
*   Aligns plane to XY
    
*   Transforms point cloud accordingly
    

#### `rasterizer.py`

*   Takes a transformed point cloud
    
*   Projects 3D points onto 2D
    
*   Fills a NumPy image array with color values
    
*   Saves final image via OpenCV
    

#### `config.py`

*   Resolution settings (`pixels_per_meter`)
    
*   Default COLMAP options
    
*   RANSAC thresholds
    

#### `utils.py`

*   Safe mkdirs
    
*   Logging helpers
    
*   Common NumPy helpers (e.g., `normalize()`)
    

* * *

🧪 Benefits of This Split
-------------------------

| Benefit | How this structure helps |
| --- | --- |
| 🧼 **Clean codebase** | Each file does one job |
| 🔁 **Reusable parts** | You can swap `sfm_pipeline.py` with OpenSfM, or `rasterizer.py` with a GIS rasterizer |
| 🧪 **Testability** | Easier to write unit tests for projection math or plane fitting |
| 🧰 **Extensibility** | Add future tools: NDVI calc, heightmap export, grid overlays, etc. |
| 🔄 **Partial reruns** | You can run SfM once and rerun just the projection/rasterization |
