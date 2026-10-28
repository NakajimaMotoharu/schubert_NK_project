"""Static-only final4 token inverse/current diagnostic preservation; no target lifecycle."""
import pg13530_main_assignment_final_config as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_main_assignment_final_sources as statements

if __name__ == '__main__':
    stage.inverse = statements.inverse
    stage.negative = statements.negative
    stage.baseline = statements.baseline
    stage.preflight(cfg)
