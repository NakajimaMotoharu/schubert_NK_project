"""Fresh22-source preflight after two private-name repairs; original failed run remains immutable."""
import pg13481_positioned_literal_config_v2 as cfg
from f03_literal_batch_preflight_v5 import preflight

if __name__ == '__main__':
    preflight(cfg)
