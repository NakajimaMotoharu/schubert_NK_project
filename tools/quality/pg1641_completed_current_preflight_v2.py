"""BUG1143: exact actual full-post schema; native has independent catalog.

Old1639 failure preserved. No artificial native field is added to the baseline.
All current eight and six historical streams are reauthenticated, not recaptured.
"""
import ast
import inspect
import json
import pg1639_completed_current_preflight as prior
from pg1616_current_ordinary_native_catalog_v2 import catalog_source

KEYS = frozenset(['backup', 'configuration', 'extraDurable', 'originals', 'pid1', 'rows', 'runtime', 'startup', 'unitFilesActual', 'units'])


def validate_schema(value):
    if type(value) is not dict or set(value) != KEYS:
        raise ValueError('exact actual completed full schema required')
    if any(type(value[k]) is not dict for k in KEYS):
        raise ValueError('actual full schema value types required')
    return True


def payload():
    post = json.loads((prior.W / 'pg1613-current-ordinary-terminal-post-v1.safe.json').read_bytes())
    seals = {n: post['proofHashes'][n]['sha256'] for n in prior.seal_contract.previous.SEALS}
    native = catalog_source()
    marker = "print(json.dumps({'selected':selected"
    if native.count(marker) != 1:
        raise ValueError('exact current independent catalog result required')
    native = native.replace(marker, "return ({'selected':selected")
    native = native.replace("'guestWritesStartsStops0':True}))", "'guestWritesStartsStops0':True})")
    ast.parse(native)
    raw = prior.payload()
    boundary = "require(native==after['native'])"
    if raw.count(boundary) != 1:
        raise ValueError('one failed nonexistent schema boundary required')
    definitions = 'KEYS=' + repr(KEYS) + '\n' + inspect.getsource(validate_schema)
    definitions += '\ndef independent_native_catalog():\n SEALS=' + repr(seals) + '\n' + ''.join(' ' + line + '\n' for line in native.splitlines())
    proof = "validate_schema(after)\nindependent=independent_native_catalog();require(len(independent['selected'])==8 and len(independent['excludedHistorical'])==6)\nrequire(tree(pathlib.Path('/run/schubert-nk/pt-coverage'))==native)"
    raw = raw.replace(boundary, definitions + '\n' + proof).replace('pg1639-completed-current-before-v1', 'pg1641-completed-current-before-v2')
    compile(raw, '<schema-fixed complete current and independent native>', 'exec')
    return raw


def main():
    raw = inspect.getsource(prior.main).replace('pg1639-completed-current-before-v1', 'pg1641-completed-current-before-v2')
    ns = {**prior.__dict__, 'payload': payload}
    exec(compile(raw, '<new-only actual schema preflight>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
