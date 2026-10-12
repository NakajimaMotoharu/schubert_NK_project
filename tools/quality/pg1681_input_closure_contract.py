"""Independent closed helper/import and actual input-name contract; no I/O."""
import ast
import re
from pathlib import PurePosixPath

STANDARD = frozenset(['ast', 'datetime', 'hashlib', 'json', 'os', 'pathlib', 're', 'stat', 'subprocess', 'sys', 'time', 'grp', 'tarfile', 'ctypes', 'ipaddress', 'signal', 'select', 'errno', 'contextlib', 'traceback'])


def canonical(name):
    if type(name) is not str or not name or '\\' in name or name.startswith('/') or any(p in ('', '.', '..') for p in name.split('/')) or PurePosixPath(name).as_posix() != name:
        raise ValueError('canonical closed relative name required')
    return name


def validate_graph(pins, sources, archive_name, names):
    if type(pins) is not dict or not pins or type(sources) is not dict or type(names) is not set:
        raise ValueError('complete typed pins/source/input names required')
    if canonical(archive_name) != 'pg1683-release-v4.tar' or names != {'pg1683-release-v4.tar', 'pg1638-manifest-v1.sig', 'bundle.safe.json'}:
        raise ValueError('exact compiled and transferred input basenames required')
    for name, digest in pins.items():
        canonical(name)
        if type(digest) is not str or re.fullmatch('[0-9a-f]{64}', digest) is None:
            raise ValueError('typed complete file digest required')
    expected = {n for n in pins if n.endswith('.py')}
    if set(sources) != expected or 'pg1681_input_preflight.py' not in expected or 'pg1640_native_refs.py' not in expected:
        raise ValueError('all frozen Python source bytes required')
    for name, raw in sources.items():
        if type(raw) is not str:
            raise ValueError('actual frozen source text required')
        for node in ast.walk(ast.parse(raw)):
            modules = []
            if isinstance(node, ast.Import):modules = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level or node.module is None:raise ValueError('absolute dependency required')
                modules = [node.module]
            for module in modules:
                root = module.split('.')[0]
                if root.startswith('pg'):
                    if root + '.py' not in pins:raise ValueError('missing transitive frozen helper')
                elif root not in STANDARD and root != 'dbus':
                    raise ValueError('foreign runtime import refused')
    refs = sources['pg1640_native_refs.py']
    values = {node.value for node in ast.walk(ast.parse(refs)) if isinstance(node, ast.Constant) and type(node.value) is str}
    if archive_name not in values or 'pg1661-release-v1.tar' in values or 'pg1683-release-v1.tar' in values:
        raise ValueError('actual compiled child archive path mismatch')
    if 'Pg1640UnusedStage.class' not in pins or 'Pg1640UnusedStage$References.class' not in pins:
        raise ValueError('actual main and reference class bytes required')
    return True
