"""Capture current4 Main and exact7 original diagnostic/owner bindings before editing."""
import pg13500_main_assignment_config as cfg
from f03_main_assignment_sources import originals

if __name__ == '__main__':
    originals(cfg)
