import logging
import os
from pathlib import Path

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
