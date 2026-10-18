"""Genuine same-source full11/all80, raw-first all24 and newday oracle seal."""
import ast
import inspect
from pyflakes.api import check
import pg4760_new_current_whole_seal as previous
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as terminal
import pg5040_current_newday_rows as rows
import pg5030_new_day_query_oracle as oracle

SLOT = 'pg5042-current-newday-whole-seal-v1'


def payload(observed, before_hash):
    # Rebuild the current genuine guard from actual5038, never rewrite a saved
    # historical capsule. Replace the SQL capsule with independently planned day1.
    raw = terminal.bind(previous.previous.seal_payload(observed, before_hash))
    raw = raw.replace(previous.previous.SEAL, SLOT).replace(previous.previous.ROWS, rows.SLOT)
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'project')
    raw = raw.replace(ast.get_source_segment(raw, node), admission.project_source(), 1)
    genuine = terminal.payload(observed)
    marker = "out=pathlib.Path('/var/lib/pgpt-s1-preservation/" + terminal.TERM + "')"
    if genuine.count(marker) != 1:
        raise ValueError('one current genuine terminal boundary')
    guard = genuine[:genuine.index(marker)]
    independent = oracle.source() + '\nimport base64,stat\nfrom pathlib import Path\n' + rows.key_source()
    independent += '\ndef qualify(old, new, cutoff, done, upper):\n'
    independent += '    try:\n        require(instant(cutoff)<=instant(done)<=instant(upper))\n'
    independent += '        return qualify_current(old,new,' + repr(observed['run']) + ',cutoff,upper)\n'
    independent += '''
    finally:
        KEY[:]=b'\\0'*len(KEY)
'''
    # Core4586 already applied the tested raw-first transform exactly once.
    # Preserve it and replace only explicitly rebuilt current oracle/guard.
    raw = previous.replace_constant(raw, 'ORACLE', independent)
    raw = previous.replace_constant(raw, 'GUARD', guard)
    if check(independent, '<independent newday query full24 capsule>'):
        raise ValueError('complete independent capsule static0')
    if check(raw, '<actuala2ecc full11/all80/newday whole seal>'):
        raise ValueError('complete emitted namespace static0')
    return raw


def main():
    ns = {**vars(previous), 'admission': admission, 'terminal': terminal, 'rows': rows,
          'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<genuine terminal and24 before whole>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
