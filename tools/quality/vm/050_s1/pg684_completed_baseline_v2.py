"""BUG919 fixed extracted-function dependencies, new-only readonly slot."""
from pathlib import Path
from pg684_completed_baseline import source as previous

R = Path(__file__).resolve().parent


def source():
    raw = previous().replace('pg684-completed-baseline-v1', 'pg684-completed-baseline-v2')
    injection = "import sys\ndeps={'pg535_bootstrap_contract.py':'270a8211601f423744d6944e85707b869ecdd783d178c360f9f90b7b5c2ace07','pg536_bootstrap_execution_contract.py':'3e247f0a049f1b39f5c954d3262578df74cf44f19ea9af0354c02c6e4caf87a6'}\nfor name,digest in deps.items():require(hashlib.sha256(strict(base/'pg664-bootstrap-tools-v1'/name,0o400,131072)).hexdigest()==digest)\nsys.path.insert(0,str(base/'pg664-bootstrap-tools-v1'))\nfrom pg535_bootstrap_contract import UNIT,normal20\nfrom pg536_bootstrap_execution_contract import record\n"
    # The occurrence is inside a host raw Python PAYLOAD literal, not executed host code.
    assert raw.count('gc_nodes=') == 1
    return raw.replace('gc_nodes=', injection+'gc_nodes=')


if __name__ == '__main__':
    env = {'__file__': str(R/'pg684_completed_baseline_v2.py'), '__name__': 'fresh_readonly_v2'}
    exec(compile(source(), '<knownGC pinned dependency graph>', 'exec'), env)
    env['main']()
