"""Explicit Caddy2 oracle; immutable selected input only."""
import hashlib
import inspect
import json
import os
from pg1627_selected_contract_qualification import qualified_tests as base_oracle
from pg1745_root_exact_qualification import server as root_server
from pg1719_current_bootstrap_sources import SOURCE
from pg1625_unsupported_ports_selected import W
from lan_server import run, copy

METHODS={'dev.codex.schubert.nk.batch.file.CaddyAddressBoundaryTest:'+n for n in ('caddy1746001MissingBodyAndPartialBracketRejectBeforeUri','caddy1746002Ipv4ZeroAndIpv6UnspecifiedHaveExactTlsLoginUri')}

def qualified_tests(manifest, xml_bytes, expected):
    # One direct source boundary, not nested generator-to-generator rewriting.
    raw = inspect.getsource(base_oracle).replace('len(expected) not in (3, 6)', 'len(expected) != 2')
    ns = {}
    exec(compile(raw, '<explicit two unique XML oracle>', 'exec'), ns)
    return ns['qualified_tests'](manifest, xml_bytes, expected)

def generated_oracle():
    return inspect.getsource(base_oracle).replace('len(expected) not in (3, 6)', 'len(expected) != 2')

def server():
    return root_server().replace('PG1745','PG1747').replace('1743','1746').replace("results['1746']['tests']==8", "results['1746']['tests']==2")

def main():
    os.umask(0o077)
    host = json.loads((W/'pg1746-caddy-address-selected-v1/manifest.safe.json').read_bytes())
    if host.get('actualExit') != 0 or host.get('tests') != 2 or host.get('productionSource') != SOURCE:
        raise ValueError('actual current two required before creating slot')
    code = 'INPUT='+repr({'1746':host['manifestSha256']})+'\nSOURCE='+repr(SOURCE)+'\nMETHODS='+repr(METHODS)+'\n'+generated_oracle()+'\n'+server()
    from pyflakes.api import check
    if check(code, '<explicit two immutable qualifier>'):
        raise ValueError('static gate refused')
    out=W/'pg1747-caddy-exact-qualified-v1'
    out.mkdir(mode=0o700)
    path=out/'pg1747-qualification.private.py'
    path.write_text(code)
    status, output=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/pg1747-qualification.private.py && test ! -e /home/mini/schubert-nk-pgpt/runs/PG1747-selected-qualification-v1', timeout=30)
    if status: raise ValueError('new slot required')
    status, output=copy(path, '/home/mini/schubert-nk-pgpt/transfer/', timeout=60)
    if status: raise ValueError('transfer refused')
    status, output=run('python3 -B /home/mini/schubert-nk-pgpt/transfer/pg1747-qualification.private.py', timeout=60)
    (out/'server.private.log').write_text(output)
    safe={'actualExit':status, 'scriptSha256':hashlib.sha256(code.encode()).hexdigest(), 'formalAccepted':False}
    if status == 0:
        safe.update(json.loads(next(v for v in output.splitlines() if v.startswith('{'))))
    with (out/'manifest.safe.json').open('x') as f:
        json.dump(safe,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(safe))
    return status

if __name__ == '__main__': raise SystemExit(main())
