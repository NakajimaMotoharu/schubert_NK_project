"""New eeae actual eight streams + qualified40ef926 only; old native excluded."""
import ast,json,os,subprocess
from pathlib import Path
from pg879_native_counter import catalog as previous_catalog,code as previous_code
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='40ef6e894573d2ffab1d1732124960f9c98d5f97'
def catalog(before_sha):
    return previous_catalog(before_sha).replace('pg877-native-stop-v1','pg963-native-stop-v1')
def code(hashes,before_sha,after_sha,end):
    raw=previous_code(hashes,before_sha,after_sha)
    for a,b in (('e01612fcd7f2752df5ae0836b78538fd5e87f120',SOURCE),('pg877','pg963'),('pg878','pg968'),('pg879','pg969'),('PG879','PG969'),('189291','213904'),('09167719cb0445fea8da5a6fdbaa3b0f','0bb4d6f3b9e74cdc91c553748a4cd018'),('183192933299','201380374989'),('184317014132',str(end)),('pg857-completed-reference-six-host-v1','pg926-body-six-host-v1'),('fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6','4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'),("tests']==3541","tests']==3560")):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
def main():
    os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
    assert(W/'pg968-terminal-final-v1.exit').read_bytes()==b'0\n'
    final=json.loads((W/'pg968-terminal-final-v1.safe.json').read_bytes());assert final['actualExit']==0 and final['productionSource']==SOURCE
    proof=json.loads((W/'pg960-completed-readonly-v1.safe.json').read_bytes())
    from pg963_current_stop_binding import bindings
    bindings(proof);end=proof['genuineCompletion']['endMonotonicUs']
    seals=final['proofHashes'];before=seals['before.private.json']['sha256'];after=seals['after.private.json']['sha256']
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    hashes=json.loads(subprocess.check_output(ssh,input=catalog(before).encode(),timeout=30));assert len(hashes)==8
    env={'__name__':'fixed40ef_current_native','__file__':str(R/'pg969_current_native_counter.py')}
    exec(compile(code(hashes,before,after,end),'<969 same-source eight native only>','exec'),env);env['main']()
if __name__=='__main__':main()
