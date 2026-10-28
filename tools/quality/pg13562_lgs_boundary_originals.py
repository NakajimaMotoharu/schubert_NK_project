"""Freeze original whole8 LGS oracle and exact current diagnostic baseline before add-only changes."""
import pg13560_lgs_boundary_config as cfg
from f03_lgs_boundary_vectors import originals

if __name__ == '__main__':
    originals(cfg)
