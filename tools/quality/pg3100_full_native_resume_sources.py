"""BUG1266: retain the complete latest snapshot, independently re-reading native bytes too."""
import ast
import json
from pyflakes.api import check
import pg3080_retained_parent_resume_sources as previous
from pg1446_current_cold_stage import W

SOURCE, BOM, BOOT, RUN, BEFORE = previous.SOURCE, previous.BOM, previous.BOOT, previous.RUN, previous.BEFORE
TOOLS = 'pg3100-full-native-resume-tools-v1'
SAVE = 'pg3104-full-native-resume-preparation-v1'
CLASS = 'Pg3100FreshResumePreparation'


def bind(raw):
    return raw.replace(previous.TOOLS, TOOLS).replace(previous.SAVE, SAVE).replace('pg3080', 'pg3100').replace('Pg3080', 'Pg3100').replace('PG3080', 'PG3100')


def sources():
    proof = json.loads((W / 'pg3096-recovered-native-schema-full-post-v1/manifest.safe.json').read_bytes())
    if not (proof['actualExit'] == 0 and proof['allClientAdvisoryFlock0'] and proof['proofHashes']['after.private.json']['sha256'] == BEFORE):
        raise ValueError('actual latest recovered whole original/native/resource post required')
    values = {bind(n): bind(raw) for n, raw in previous.sources().items()}
    raw = values['pg3100_native_refs.py']
    capture = next(n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef) and n.name == 'capture_data')
    returns = [n for n in ast.walk(capture) if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict)]
    if len(returns) != 1 or len(returns[0].value.keys) != 10 or any(isinstance(k, ast.Constant) and k.value == 'native' for k in returns[0].value.keys):
        raise ValueError('one diagnosed ten-key legacy snapshot expected')
    old = ast.get_source_segment(raw, returns[0])
    if not old.endswith("'runtime': runtime}"):
        raise ValueError('exact unmodified original/runtime return boundary required')
    new = old[:-1] + ", 'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))}"
    raw = raw.replace(old, new, 1)
    if 'require(set(prior) == set(first) and same_value(first, prior))' not in raw:
        raise ValueError('full strict baseline equality must not be filtered or weakened')
    values['pg3100_native_refs.py'] = raw
    for name, value in values.items():
        if name.endswith('.py'):
            if check(value, '<whole snapshot returned ' + name + '>'):
                raise ValueError('complete generated globals required')
            compile(value, '<all original and real native bytes>', 'exec')
    return values
