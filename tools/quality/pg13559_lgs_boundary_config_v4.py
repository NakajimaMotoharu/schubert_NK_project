"""Frozen add-only LGS plan with separate static schema-recovery identity."""
import pg13561_lgs_boundary_config_v2 as previous

globals().update({key: value for key, value in vars(previous).items() if not key.startswith('_') and key != 'previous'})
PREFLIGHT_NUMBER = 13569
