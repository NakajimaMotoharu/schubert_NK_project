"""Add-only current-source proof with ten meaningful header/physical-size mutations."""
import pg13590_lgs_remaining_config as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_lgs_remaining_vectors as vectors
from pg13569_lgs_boundary_preflight_schema import retained_originals

if __name__ == '__main__':
    stage.original_value = retained_originals
    stage.inverse = vectors.inverse
    stage.negative = vectors.negative
    stage.baseline = vectors.baseline
    stage.preflight(cfg)
