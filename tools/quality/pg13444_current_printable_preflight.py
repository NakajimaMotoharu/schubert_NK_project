"""All-token inverse and exact current per-file raw PMD/CS delta only."""
import pg13440_current_printable_literal_config as cfg
from f03_literal_batch_preflight_v4 import preflight

if __name__ == '__main__':
    preflight(cfg)
