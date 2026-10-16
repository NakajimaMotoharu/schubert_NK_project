"""One durable new-source ordinary start, only after full preserved publication post."""
import ast
import inspect
import json
from pyflakes.api import check
import pg3802_hygiene_current_noargs_once as previous
import pg4008_literal_invariant_publication_post as post
from pg4012_literal_invariant_current_observer import SOURCE, BOM, namespace
from pg4029_literal_invariant_browser_ready_serial import require_ready
from pg1446_current_cold_stage import W

SLOT = 'pg4016-literal-invariant-current-noargs-once-v1'


def body():
    raw = previous.body()
    changes = {'pg3798': 'pg4012', previous.SLOT: SLOT, previous.SOURCE: SOURCE, previous.BOM: BOM, 'PG3748': 'PG3976', 'require(len(records)==34)': 'require(len(records)==46)'}
    for old, new in changes.items():
        if old not in raw: raise ValueError('exact new-source ordinary46 boundary required: ' + old)
        raw = raw.replace(old, new)
    return raw


def payload(hashes):
    raw = post.payload(); cut = raw.index("save=base/'pg4008-literal-invariant-publication-independent-post-v1'"); raw = raw[:cut]
    tree = ast.parse(raw)
    scopes = [n for n in tree.body if isinstance(n, ast.Try) and any(isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'units' for t in x.targets) for x in n.body)]
    if len(scopes) != 1: raise ValueError('one actual ten-reference ordinary admission scope')
    selected = scopes[0]; lines = raw.splitlines(keepends=True)
    end = next(i for i in range(selected.lineno - 1, selected.end_lineno) if lines[i].startswith('finally:'))
    action = body().replace('print(json.dumps(current))\nraise SystemExit(r.returncode)', '')
    if action == body(): raise ValueError('ordinary client output after reference scope closure only')
    _, summary, _ = post.role.ro.unused.current_tuple()
    original = inspect.getsource(previous.payload)
    # Reuse only the immutable parser/prelude constant; it contains no Root start or proof substitution.
    parsed = ast.parse(original)
    prelude_node = next(n.value for n in ast.walk(parsed) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'prelude' for t in n.targets))
    leading = prelude_node
    while isinstance(leading, ast.BinOp) and isinstance(leading.op, ast.Add): leading = leading.left
    if not isinstance(leading, ast.Constant) or not isinstance(leading.value, str) or not leading.value.startswith('parser_raw='):
        raise ValueError('one immutable original parser/prelude constant required')
    prelude = leading.value + 'summary=' + repr(summary) + '\n'
    result = 'import ast\nWATCH_FILES=' + repr(hashes) + '\n' + ''.join(lines[:end]) + '\n'.join(' ' + line if line else line for line in (prelude + action).splitlines()) + '\n' + ''.join(lines[end:selected.end_lineno])
    result += '\ncurrent.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n'
    if check(result, '<whole new7bb ordinary admission>'): raise ValueError('complete ordinary namespace required')
    compile(result, '<one new current Root admission>', 'exec')
    return result


def main():
    require_ready()
    transport = previous.transport
    if transport.subprocess.check_output(['git', 'diff', '--name-only', SOURCE, 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('qualified source unchanged before admission')
    proof = json.loads((W / post.SLOT / 'manifest.safe.json').read_bytes())
    if proof.get('actualExit') != 0 or proof.get('result', {}).get('productionSource') != SOURCE or proof['result'].get('unitExchangeAndReload') is not False:
        raise ValueError('actual independent new publication post required')
    raw = inspect.getsource(transport.main).replace('pg2176', 'pg4012').replace('pg2174-normal-publication-full-post-v1', post.SLOT).replace("post['guest']", "post['result']")
    values = {**transport.__dict__, 'namespace': namespace, 'SOURCE': SOURCE, 'BOM': BOM, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<one new current ordinary admission transport>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
