"""Reuse static-only runner with explicit Main statement inverse and current measured baseline."""
import pg13500_main_assignment_config as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_main_assignment_sources as statements

if __name__ == '__main__':
    stage.inverse = statements.inverse
    stage.negative = statements.negative
    stage.baseline = statements.baseline
    stage.preflight(cfg)
