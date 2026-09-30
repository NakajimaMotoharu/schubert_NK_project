"""Append separately executed independent oracle/same-byte union, retaining actual hashes."""
import pathlib,json,hashlib,subprocess
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
base=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG386-native-backup-failure'
for src,dst in [('pg386-artifact-oracle.json.log','artifact-oracle.json.log'),('pg386-batch-union.json','batch-host-native-union.json')]:
 (out/dst).write_bytes((base/src).read_bytes())
ssh=['ssh','-i','/home/mini/codex/project1/work/pgpt-vm/private/vm-access','-p','22222','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/mini/codex/project1/work/pgpt-vm/private/known_hosts','ubuntu@127.0.0.1']
command='sudo -n pg_restore --list /srv/schubert-nk/backup/20260930-130116-31100027-2222-4333-8444-555555555555/schubert_nk.dump | awk \'BEGIN{n=0} !/^;/&&NF{n++} END{print "RESTORE_LIST_ENTRIES="n}\''
p=subprocess.run(ssh+[command],text=True,capture_output=True,check=True)
assert not p.stderr.strip() and p.stdout.strip()=='RESTORE_LIST_ENTRIES=224'
(out/'restore-list-summary.txt').write_text(p.stdout)
m=json.loads((out/'manifest.json').read_text())
m['commands']['restore-list-summary.txt']={'command':command,'exitCode':0}
m['actual']['artifactOracle']='independent literal run/cutoff/attempt5/rows9+10/time+versions; four actual file hash/size; fixed7 config/fixed16 encrypted credential decrypted private; pg_restore-list224'
m['coverage']['batchHostNativeUnion']=json.loads((out/'batch-host-native-union.json').read_text())
m['files']=[{'path':str(p.relative_to(repo)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json']
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('PG386 native manifestSha256='+hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest())
