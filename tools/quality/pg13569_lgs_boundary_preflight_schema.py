"""Raw retained diagnostics need no removal IDs; strict add-only adapter, no Product execution."""
import copy
from collections import Counter
import pg13559_lgs_boundary_config_v4 as cfg
import f03_literal_batch_preflight_v5 as stage
import f03_lgs_boundary_vectors_v3 as vectors
from f03_literal_batch_sources import original_value
from f03_literal_batch_diagnostic_v3 import signature

def retained_originals(config):
    value = copy.deepcopy(original_value(config))
    assert config.EXPECTED_CORRECTIONS == 0 and len(value['sources']) == 1
    for row in value['sources']:
        assert row['mapping'] == [] and row['path'] == config.PATH
        measured, _ = vectors.baseline(config, row)
        sig = lambda rows: Counter(signature(r['attributes'], r['message']) for r in rows)
        assert len(row['findings']) == len(measured) == 2 and sig(row['findings']) == sig(measured)
        for index, finding in enumerate(row['findings']):
            assert 'id' not in finding
            finding['id'] = 'UNSELECTED_RETAINED_' + str(index)
        assert len({r['id'] for r in row['findings']}) == 2
    return value

if __name__ == '__main__':
    stage.original_value = retained_originals
    stage.inverse = vectors.inverse
    stage.negative = vectors.negative
    stage.baseline = vectors.baseline
    stage.preflight(cfg)
