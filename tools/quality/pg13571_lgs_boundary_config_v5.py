"""Same two vectors and original budget; new source after standard-format correction."""
import pg13559_lgs_boundary_config_v4 as previous

globals().update({key: value for key, value in vars(previous).items() if not key.startswith('_') and key != 'previous'})
PREFLIGHT_NUMBER = 13573
NORMAL_NUMBER = 13572
STATIC_NUMBER = 13574
POST_NUMBER = 13576
