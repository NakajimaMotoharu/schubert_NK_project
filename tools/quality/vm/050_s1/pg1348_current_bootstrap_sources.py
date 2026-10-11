"""Fresh-only namespace; failed1345 partial compiler artifacts remain untouched."""
from pg1345_current_bootstrap_sources import files as previous, SOURCE, BEFORE, W

def files(baseline_sha):
    return {name.replace('1345', '1348'): raw.replace('Pg1345', 'Pg1348').replace('pg1345', 'pg1348').replace('PG1345', 'PG1348')
            for name, raw in previous(baseline_sha).items()}
