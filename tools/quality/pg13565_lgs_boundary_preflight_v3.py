"""Static-only add-only boundary proof with positive control and ten meaningful token negatives."""
import pg13561_lgs_boundary_config_v2 as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_lgs_boundary_vectors_v3 as vectors

if __name__ == '__main__':
    stage.inverse = vectors.inverse
    stage.negative = vectors.negative
    stage.baseline = vectors.baseline
    stage.preflight(cfg)
