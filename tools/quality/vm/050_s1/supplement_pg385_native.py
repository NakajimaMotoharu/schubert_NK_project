"""Allowlisted PID1 receipt and independent artifact evidence; never raw journal."""
import pathlib,json,subprocess,hashlib
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG385-native-deployment'
ssh=['ssh','-i','/home/mini/codex/project1/work/pgpt-vm/private/vm-access','-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/mini/codex/project1/work/pgpt-vm/private/known_hosts','ubuntu@127.0.0.1']
command='''sudo -n journalctl --since "2026-09-30 03:00:00 UTC" -o json --no-pager | python3 -c 'import sys,json
for line in sys.stdin:
 x=json.loads(line)
 if x.get("UNIT")=="schubert-nk-backup.service" and x.get("INVOCATION_ID")=="a7d870091a45446fa19aa1506b01783f":
  print(json.dumps({k:x[k] for k in ["__REALTIME_TIMESTAMP","UNIT","INVOCATION_ID","JOB_TYPE","JOB_RESULT","_PID","_EXE"] if k in x}))' '''
p=subprocess.run(ssh+[command],text=True,capture_output=True,check=True)
assert not p.stderr.strip()
rows=[json.loads(s) for s in p.stdout.splitlines()]
assert any(x.get('JOB_TYPE')=='start' and x.get('JOB_RESULT')=='done' for x in rows)
assert any(x.get('JOB_TYPE')=='stop' and x.get('JOB_RESULT')=='done' for x in rows)
assert all(x['_PID']=='1' and x['_EXE']=='/usr/lib/systemd/systemd' for x in rows)
(out/'worker-pid1-receipt.jsonl').write_text(p.stdout)
manifest=json.loads((out/'manifest.json').read_text())
manifest['actual']['workerReceipt']='independent PID1 start done and explicit stop done, fixed fresh Invocation'
manifest['actual']['artifactOracle']='literal run/cutoff/handles/UTC/version; independently matching hash/size; fixed7 config/fixed16 credential decrypt; pg_restore-list224'
manifest['commands']['worker-pid1-receipt.jsonl']={'command':command,'exitCode':0}
manifest['testIds']=['PT-OPS-BARCHIVE001/POS','PT-OPS-BGATE010/VM','PT-OPS-BREQFILE010/VM','PT-OPS-MDB016/VM']
manifest['ssc']=list(dict.fromkeys([*manifest['ssc'],'SSC-114']))
manifest['bugs']=list(dict.fromkeys([*manifest['bugs'],'BUG-348']))
manifest['files']=[{'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json']
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('PG385 native supplemented manifestSha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
