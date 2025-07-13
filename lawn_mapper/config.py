# Configuration settings for Lawn Mapper pipeline

# General configuration
CONFIG = {
    'pixels_per_meter': 100.0,  # Resolution of the output map
}

# COLMAP options for Structure from Motion and Multi-View Stereo
COLMAP_OPTIONS = {
    'feature_extraction': {
        'SiftExtraction.num_octaves': 4,
        'SiftExtraction.octave_resolution': 3,
        'SiftExtraction.peak_threshold': 0.02 / 3,
        'SiftExtraction.edge_threshold': 10,
        'SiftExtraction.max_num_features': 8192,
    },
    'feature_matching': {
        'SiftMatching.num_samples': 20,
        'SiftMatching.min_ratio': 0.7,
        'SiftMatching.min_distance': 30,
        'SiftMatching.cross_check': True,
    },
    'mapper': {
        'Mapper.min_num_matches': 15,
        'Mapper.ignore_watermarks': False,
        'Mapper.multiple_models': False,
        'Mapper.min_model_size': 10,
    },
    'mvs': {
        'PatchMatchStereo.window_radius': 5,
        'PatchMatchStereo.window_step': 1,
        'PatchMatchStereo.num_samples': 15,
        'PatchMatchStereo.geom_consistency': True,
        'PatchMatchStereo.max_image_size': 2000,
    }
}

# RANSAC options for ground plane fitting
RANSAC_OPTIONS = {
    'max_distance': 0.1,  # Maximum distance from point to plane to be considered an inlier (meters)
    'min_points': 1000,   # Minimum number of points to fit the plane
    'num_iterations': 1000  # Number of RANSAC iterations
}
