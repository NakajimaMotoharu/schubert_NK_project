"""BUG1260: preserve already-current negative authorities; namespace-only helpers."""
from pyflakes.api import check
import pg2950_current_cold_resume_sources as prior
import pg2890_network_owned_sources as qualified

SOURCE = prior.SOURCE
BOM = prior.BOM
BOOT = prior.BOOT
BEFORE = prior.BEFORE
RUN = prior.RUN
TOOLS = 'pg2970-current-cold-resume-tools-v1'
SAVE = 'pg2974-current-cold-resume-preparation-v1'
CLASS = 'Pg2970FreshResumePreparation'
HELPERS = ['parent_receipt.py', 'warning_parent_projection.py', 'configuration.py', 'configuration_capture.py', 'row_bound.py', 'stable_journal.py']


def namespace(raw):
    return raw.replace(prior.TOOLS, TOOLS).replace(prior.SAVE, SAVE).replace('pg2950', 'pg2970').replace('Pg2950', 'Pg2970').replace('PG2950', 'PG2970')


def sources():
    values = {namespace(n): namespace(raw) for n, raw in prior.sources().items()}
    current = qualified.sources()
    for suffix in HELPERS:
        # These are already bound to a9/current run. Do not rewrite old-run
        # exclusions as if they were positive authority placeholders.
        values['pg2970_' + suffix] = current['pg2890_' + suffix].replace('pg2890', 'pg2970').replace('Pg2890', 'Pg2970').replace('PG2890', 'PG2970')
    for name, raw in values.items():
        if name.endswith('.py'):
            if check(raw, '<namespace-only current resume ' + name + '>'):
                raise ValueError('complete namespace required')
            compile(raw, '<namespace-only current resume>', 'exec')
    if len(values) != 20:
        raise ValueError('whole twenty-source current graph required')
    return values
