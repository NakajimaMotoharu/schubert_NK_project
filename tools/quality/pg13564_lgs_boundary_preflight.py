"""Static-only add-only vector inverse and unchanged current PMD diagnostics."""
import pg13560_lgs_boundary_config as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_lgs_boundary_vectors_v2 as vectors

if __name__ == '__main__':
    stage.inverse = vectors.inverse
    stage.negative = vectors.negative
    stage.baseline = vectors.baseline
    stage.preflight(cfg)
