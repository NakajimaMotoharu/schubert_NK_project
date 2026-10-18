"""Independent SS324/331/341 new-day cleanup plus authenticated query expiry."""
import ast
from pyflakes.api import check
import pg4632_current_new_day_rows_oracle as new_day
import pg4742_same_day_query_oracle as query


EXPECTED_INBOX = '''def expected_inbox(rows, expected):
    # Approved execution order: planned session cleanup precedes Inbox lookup.
    removed = set(expected['auth_sessions'])
    after_sessions = {**rows, 'schubert.auth_sessions': [r for r in rows['schubert.auth_sessions']
                      if str(r['id']) not in removed]}
    return classify_query_inbox(after_sessions, expected['inbox_scan_candidates'], KEY, LAYOUTS)
'''


def source():
    raw = new_day.source()
    tree = ast.parse(raw)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'expected_inbox')
    raw = raw.replace(ast.get_source_segment(raw, node), EXPECTED_INBOX, 1)
    selected = {'aad', 'plaintext', 'fields', 'validate_base', 'validate_query', 'query_wire', 'classify_query_inbox'}
    q = query.source()
    nodes = [n for n in ast.parse(q).body if isinstance(n, ast.FunctionDef) and n.name in selected
             or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'LAYOUTS' for t in n.targets)]
    if {n.name for n in nodes if isinstance(n, ast.FunctionDef)} != selected:
        raise ValueError('complete independently authenticated query codec required')
    raw = ('import struct,unicodedata,zlib\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\n'
           + raw + '\n' + '\n'.join(ast.get_source_segment(q, n) for n in nodes))
    if check('KEY=bytes(32)\n' + raw, '<new-day full24 and authenticated query oracle>'):
        raise ValueError('complete independent namespace required')
    compile(raw, '<new-day independent normal oracle>', 'exec')
    return raw


def namespace(key):
    ns = {'KEY': key}
    exec(compile(source(), '<independent newday query oracle>', 'exec'), ns)
    return ns


if __name__ == '__main__':
    raise SystemExit('library only; no DB, clock or Production mutation')
