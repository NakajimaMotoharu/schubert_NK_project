"""Exact public no-argument Python entrypoint provenance, never serialize arbitrary CLI values."""
import hashlib
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def public_script(path, root):
    value=Path(path).absolute()
    try:
        value.relative_to(root/'tools/quality')
    except ValueError as exc:
        raise ValueError('public quality tool scope required') from exc
    if value.is_symlink() or not value.is_file() or value.suffix!='.py' or value.resolve()!=value:
        raise ValueError('regular canonical public Python script required')
    return value


def capture(library, root=ROOT):
    if len(sys.argv)!=1 or not isinstance(sys.argv[0],str) or not sys.argv[0]:
        raise ValueError('no-argument public tool entrypoint required')
    entry=public_script(sys.argv[0],root)
    logic=public_script(library,root)
    original=list(sys.orig_argv)
    if (len(original) not in (2,3) or not all(isinstance(v,str) for v in original)
        or not re.fullmatch(r'python3(?:\.\d+)?',Path(original[0]).name)
        or original[-1]!=sys.argv[0] or original[1:-1] not in ([],['-B'])):
        raise ValueError('unambiguous ordinary Python invocation required')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    loaded={}
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if not isinstance(filename,str):continue
        path=Path(filename).absolute()
        if path.is_relative_to(root/'tools/quality') and path.suffix=='.py':
            path=public_script(path,root)
            loaded[str(path.relative_to(root))]=digest(path)
    return dict(actualPythonCommand=original,entrypointPath=str(entry.relative_to(root)),
      entrypointSha256=digest(entry),libraryPath=str(logic.relative_to(root)),librarySha256=digest(logic),
      helperPath=str(Path(__file__).relative_to(ROOT)),helperSha256=digest(Path(__file__)),
      loadedProjectPythonSources=loaded,
      arbitraryArgumentsRecorded=False,provenance='OBSERVED_SYS_ARGV_AND_ORIG_ARGV_NOT_RECONSTRUCTED')


def verify(record,root=ROOT):
    bindings={**record['loadedProjectPythonSources'],record['entrypointPath']:record['entrypointSha256'],
              record['libraryPath']:record['librarySha256']}
    for name,digest in bindings.items():
        path=public_script(root/name,root)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('public tool source changed during execution')
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=record['helperSha256']:
        raise ValueError('invocation helper changed during execution')
