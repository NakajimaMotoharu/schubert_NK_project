"""Static-only current diagnostics and strict Main inverse; no target execution."""
import pg13501_main_assignment_config_v2 as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_main_assignment_sources_v2 as statements

if __name__ == '__main__':
    stage.inverse = statements.inverse
    stage.negative = statements.negative
    stage.baseline = statements.baseline
    stage.preflight(cfg)
