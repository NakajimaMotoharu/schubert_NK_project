"""Freeze current originals/mapping before any PG edits; no Product Test."""
import pg13356_api_maintenance_literal_config as cfg
from f03_literal_batch_sources import originals
if __name__ == '__main__':originals(cfg)
