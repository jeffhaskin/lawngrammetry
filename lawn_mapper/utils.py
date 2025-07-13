import logging
import os
from pathlib import Path
from urllib.request import urlopen
import shutil
import cv2

def setup_logging(level=logging.INFO):
    """Setup logging configuration with the specified level."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized.")
    return logger

def ensure_dir(directory: Path):
    """Ensure the directory exists, creating it if necessary."""
    directory.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.debug(f"Ensured directory exists: {directory}")

def download_video(video_url: str, output_path: Path):
    """Download a video from a URL to the given path."""
    logger = logging.getLogger(__name__)
    logger.info(f"Downloading video from {video_url}...")
    with urlopen(video_url) as response, open(output_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)
    logger.info(f"Video saved to {output_path}")

def extract_frames(video_path: Path, frames_dir: Path, step: int = 10):
    """Extract every n-th frame from a video file using OpenCV."""
    logger = logging.getLogger(__name__)
    ensure_dir(frames_dir)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Unable to open video file {video_path}")
    frame_idx = 0
    saved = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            frame_path = frames_dir / f"frame_{frame_idx:04d}.png"
            cv2.imwrite(str(frame_path), frame)
            saved += 1
        frame_idx += 1
    cap.release()
    logger.info(f"Extracted {saved} frames to {frames_dir}")
