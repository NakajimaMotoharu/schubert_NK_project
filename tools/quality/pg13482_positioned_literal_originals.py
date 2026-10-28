"""Freeze actual source-position/current-SHA literal values and metadata controls, no Product execution."""
import pg13480_positioned_literal_config as cfg
from f03_positioned_ascii_literals import originals

if __name__ == '__main__':
    originals(cfg)
