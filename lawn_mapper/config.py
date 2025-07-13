# Configuration settings for Lawn Mapper pipeline

# General configuration
CONFIG = {
    'pixels_per_meter': 100.0,  # Resolution of the output map
}

# COLMAP options for Structure from Motion and Multi-View Stereo
COLMAP_OPTIONS = {
    # Options for SIFT feature extraction
    'feature_extraction': {
        'num_octaves': 4,
        'octave_resolution': 3,
        'peak_threshold': 0.02 / 3,
        'edge_threshold': 10,
        'max_num_features': 8192,
    },
    # Options for SIFT feature matching
    'feature_matching': {
        'max_ratio': 0.7,
        'max_distance': 30,
        'cross_check': True,
    },
    # Incremental mapper options (left empty to use defaults)
    'mapper': {},
    # Options for dense reconstruction via PatchMatch
    'mvs': {
        'window_radius': 5,
        'window_step': 1,
        'num_samples': 15,
        'geom_consistency': True,
        'max_image_size': 2000,
    }
}

# RANSAC options for ground plane fitting
RANSAC_OPTIONS = {
    'max_distance': 0.1,  # Maximum distance from point to plane to be considered an inlier (meters)
    'min_points': 1000,   # Minimum number of points to fit the plane
    'num_iterations': 1000  # Number of RANSAC iterations
}
