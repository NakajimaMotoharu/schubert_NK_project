"""Fresh actual Source owned-stop graph; only sealed current identities are authority."""
import json
from pyflakes.api import check
import pg2458_question_current_owned_sources as previous
from pg2544_strict_current_terminal import payload as terminal_payload
from pg2516_current_strict_candidate_sources import SOURCE, W
from pg2532_strict_normal_publication_sources import candidate_bom

TOOLS = 'pg2554-strict-current-owned-stop-tools-v1'


def context():
    seal = json.loads((W / 'pg2548-strict-current-full-seal-v1/manifest.safe.json').read_bytes())
    terminal = json.loads((W / 'pg2544-strict-current-terminal-v1/manifest.safe.json').read_bytes())
    if (any(type(v.get('actualExit')) is not int or v['actualExit'] != 0 or v.get('productionSource') != SOURCE for v in [seal, terminal])
            or seal.get('sqlOracleQualified') is not True or seal.get('currentFourOwnedLive') is not True
            or terminal.get('normalUnit0or10') is not True):
        raise ValueError('actual fresh Source terminal/all24/four owned identities required')
    return seal['privateBeforeSha256'], seal['observedOwned'], seal['genuineCompletion'], seal['doneEndUtc']


def emit_receipt(live, state):
    import ast
    raw = terminal_payload({**live['binding'], 'rootPid':live['rootPid']})
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name in {'classify', '_normal_classify'}]
    if len(nodes) != 2:
        raise ValueError('two independent actual new terminal classifiers required')
    return 'BINDING=' + repr(live['binding']) + '\nGC=' + repr(state) + '\n' + ast.unparse(
        ast.Module(body=nodes, type_ignores=[])) + "\ndef completed(rows,done):\n    return classify(BINDING,GC,rows,done)\n"


def emit(ctx, live, state, fields, bom=None):
    if bom is None:
        bom = candidate_bom()
    result = {}
    for name, raw in previous.emit(ctx, live, state, fields).items():
        name = name.replace('pg2458', 'pg2554').replace('Pg2458', 'Pg2554')
        if name == 'pg2554_parent_receipt.py':
            raw = emit_receipt(live, state)
        else:
            for before, after in [(previous.TOOLS, TOOLS), ('pg2458', 'pg2554'), ('Pg2458', 'Pg2554'),
                ('PG2458', 'PG2554'), ('pg2456-question-current-full-seal-v1', 'pg2548-strict-current-full-seal-v1'),
                (previous.SOURCE, SOURCE), (previous.BOM, bom), ('PG2428', 'PG2512'), ('pg2428', 'pg2512')]:
                raw = raw.replace(before, after)
        if name.endswith('.py'):
            if check(raw, '<complete actual fresh owned-stop graph>'):
                raise ValueError('whole actual owned-stop namespace required')
            compile(raw, '<fresh current owned graph>', 'exec')
        result[name] = raw
    return result


def sources():
    live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
    terminal = json.loads((W / 'pg2544-strict-current-terminal-v1/manifest.safe.json').read_bytes())
    projection = json.loads((W / 'pg2552-strict-current-parent-projection-v1.safe.json').read_bytes())
    ctx = context()
    if (type(live.get('actualExit')) is not int or live['actualExit'] != 0
            or type(projection.get('actualExit')) is not int or projection['actualExit'] != 0
            or projection.get('sealedBeforeSha256') != ctx[0] or projection.get('source') != SOURCE):
        raise ValueError('actual new binding/fullseal/parent18 required')
    return emit(ctx, live, terminal['parentState'], projection['parentState18'])
