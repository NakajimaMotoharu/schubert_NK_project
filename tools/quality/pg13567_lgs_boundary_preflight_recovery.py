"""Independent current static validation; no Product Test and no replay of previous entry."""
import pg13563_lgs_boundary_config_v3 as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_lgs_boundary_vectors_v3 as vectors

if __name__ == '__main__':
    stage.inverse = vectors.inverse
    stage.negative = vectors.negative
    stage.baseline = vectors.baseline
    stage.preflight(cfg)
