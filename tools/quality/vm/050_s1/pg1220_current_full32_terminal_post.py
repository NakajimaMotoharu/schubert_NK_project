"""Independent fresh terminal/source/full32/all24/resource post, no stops."""
import ast
import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from pg1217_current_full32_compile import source as compiler_source
from pg1216_current_full32_stop_binding import bindings, SOURCE, FULL32, BEFORE_PATH
from pg878_terminal_final import payload as previous
from pg643_terminal_final import SEAL
from pg1196_completed_rows_oracle import output_bound

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SEALS={'before.private.json':'de28ab9000a6b8c6dbe89ac4589a28b0b36de50655883a768e6fb8d0469d749a',
       'after.private.json':'21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36',
       'complete.private':'8f31ba931b056ae9776855ac503403e9688eb34316873169eb20205aae3badae',
       'parent.private.jsonl':'0081125ef04ea7476dc599b9afa3538c2d4252a255a6c252e01b9178065ab600'}


def proof():
    env={'__name__':'qualified_full32_compiler','__file__':str(R/'pg1217_current_full32_compile.py')}
    exec(compile(compiler_source(),'<pure compiler proof definitions>','exec'),env)
    return env['proof']()


def payload():
    p=proof();bindings(p)
    # The qualified previous factory requires its own binding schema; its final
    # payload is mechanically bound to actual current constants, never old data.
    import pg877_stop_binding as historical
    old=historical.SOURCE
    substitute=dict(p,productionSource=old,batchRun=historical.RUN,cutoff=historical.CUTOFF,activation=historical.ACT,
        beforeSha256=FULL32,parentEndedUTC='2026-10-09T18:47:10.000000Z',
        genuineCompletion=dict(p['genuineCompletion'],endMonotonicUs=historical.START+1_000_000_000))
    s=previous(substitute,SEALS)
    for a,b in [(historical.SOURCE,SOURCE),(historical.DIGEST,'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'),
                (historical.RUN,'343a5a1b-d064-47d5-88c2-31c36d7ba7a4'),(historical.CUTOFF,'2026-10-10T12:40:27.396847Z'),(historical.ACT,'ada3f7ff-8287-48d7-9ba9-5cce71f61bd3'),
                ('09167719cb0445fea8da5a6fdbaa3b0f','a14cc600a4fd4f2e9d8c4731ad9d754b'),('183192933299','51172132518'),(str(historical.START+1_000_000_000),'52530445203'),
                ('189291','81093'),('3592151','430851'),('PG862','PG1068'),('pg862-manifest.sig','pg1068-manifest.sig'),
                ('Pg877','Pg1216'),('pg877','pg1216'),('PG878','PG1220'),('pg878','pg1220'),
                ('cc9ed874-7f4f-450e-a188-8de1e42c8441','cbca8738-3b24-4090-b77c-bf029677cdd6')]:
        s=s.replace(a,b)
    # Current before already contains credentials/old-proofs/runtime and exact
    # Unit file9metadata. No nonexistent historical 'transfer' key is invented.
    start=s.index("baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg875-completed-readonly-v1/before.private.json')")
    end=s.index('native=snapshot();require(native==snapshot())',start)
    s=s[:start]+s[end:]
    s=s.replace("require(not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))", "require(tree(pathlib.Path('/run/systemd/system'))==after['runtime'])")
    old="lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();"
    if s.count(old)!=1:raise ValueError('fixed all24 aggregate bound insertion refused')
    s=s.replace(old,"rp=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30);require(type(rp.returncode)is int and rp.returncode==0 and 0<len(rp.stdout)<=67108864);lines=rp.stdout.splitlines();")
    marker="native=snapshot();require(native==snapshot())"
    extra="\n".join('  '+line for line in ["for k,v in after['extraDurable'].items():require(tree(pathlib.Path(min(v,key=len)))==v)","for path,v in after['unitFilesActual'].items():require(metadata(pathlib.Path(path))+[hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()]==v)","return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))"])
    s=s.replace('  return tree(pathlib.Path(\'/run/schubert-nk/pt-coverage\'))',extra)
    compile(s,'<full32 independent terminal payload>','exec');return s


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean source required')
    if(W/'pg1218-stop-v1.exit').read_bytes()!=b'0\n':raise ValueError('actual current normal stop required')
    build=json.loads((W/'pg1217-frozen-v1.safe.json').read_bytes())
    names=['Pg1216NativeStop.class','Pg1216NativeStop$References.class','pg1216_native_refs.py','pg1216_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1216_parent_receipt.py','pg1216_durable.py','pg1216_configuration.py','pg1216_configuration_capture.py','pg1216_row_bound.py','pg1216_stable_journal.py']
    hashes={n:build['fileHashes'][n]for n in names};receipt=(W/'pg1216-native-tools-v1/pg1216_parent_receipt.py').read_text()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    seals=json.loads(subprocess.check_output(ssh,input=SEAL.replace('pg642-native-stop-v1','pg1216-native-stop-v1').encode(),timeout=20))
    if seals!=SEALS:raise ValueError('actual independent sealed hashes required')
    code='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload()
    base=W/'pg1220-full32-terminal-post-v1';started=datetime.datetime.now(datetime.timezone.utc)
    r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    safe={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':started.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({k:v for k,v in safe.items()if k not in {'toolHashes','proofHashes'}}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
