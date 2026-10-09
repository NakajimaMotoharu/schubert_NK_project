"""Independent full current890 after -> enriched Bootstrap baseline, no unit start/writes."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
import pg890_terminal_final as previous
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def namespace():
 env={'__file__':str(R/'pg890_terminal_final.py'),'__name__':'bootstrap_readonly_base'};exec(compile(previous.source(),'<895 full890 independent base>','exec'),env);return env
def payload(proof,seals):
 env=namespace();raw=env['payload'](proof,seals)
 pure=(R/'pg529_dependency_graph.py').read_text()
 marker=" native=snapshot();require(native==snapshot())";assert marker not in raw
 marker="native=snapshot();require(native==snapshot())";assert raw.count(marker)==1
 raw=raw.replace('bus=dbus.SystemBus(private=True);',pure+'\nbus=dbus.SystemBus(private=True);')
 extra='''native=snapshot();require(native==snapshot())
 raw_dependencies={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS}
 dependencies=dependency_graph(raw_dependencies,UNITS)
 roots={name:pathlib.Path('/run/schubert-nk')/name for name in ('backup-request','cleanup-request','expiry-request')};roots['runtime-parent']=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
 namespace={name:{'metadata':metadata(p),'entries':sorted(q.name for q in p.iterdir()),'xattrs':os.listxattr(p)}for name,p in roots.items()}
 value={**after,'dependencies':dependencies,'namespace':namespace,'credentials':tree(pathlib.Path('/etc/schubert-nk/credentials')),'parentPid1':after['pid1'],'native':native,'oldProofs':tree(root),'source':'e01612fcd7f2752df5ae0836b78538fd5e87f120','manifestSha256':'20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'}
 require(len(value['rows']['schubert.batch_runs'])==584 and len(value['rows']['schubert.app_users'])==1 and value['rows']['schubert.app_users'][0]['role']=='ADMIN')
 require(all(not roots[n].is_symlink()and not namespace[n]['entries']and not namespace[n]['xattrs']for n in roots))
 require(not any(os.path.lexists('/etc/schubert-nk/credentials/'+n)for n in ('bootstrap-admin-username','bootstrap-admin-password')))
 require(value['credentials']==tree(pathlib.Path('/etc/schubert-nk/credentials'))and raw_dependencies=={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS})'''
 raw=raw.replace(marker,extra)
 raw=raw.replace('pg890-terminal-final-v1','pg895-bootstrap-before-v1').replace('PG890-terminal-final-v1','PG895-bootstrap-before-v1')
 marker="with(save/'result.safe.json').open('x')as f:";assert raw.count(marker)==1
 raw=raw.replace(marker,"snapshot_raw=json.dumps(value,sort_keys=True).encode()\nwith(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(snapshot_raw);f.flush();os.fsync(f.fileno())\nresult['beforeSha256']=hashlib.sha256(snapshot_raw).hexdigest()\n"+marker)
 ast.parse(raw);return raw
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert (W/'pg890-terminal-final-v1.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg885-completed-readonly-v1.safe.json').read_bytes());final=json.loads((W/'pg890-terminal-final-v1.safe.json').read_bytes());seals={k:v['sha256']for k,v in final['proofHashes'].items()if k in ('before.private.json','after.private.json','parent.private.jsonl','complete.private')}
 hashes=final['toolHashes'];receipt=(W/'pg887-native-tools-v1/pg887_parent_receipt.py').read_text();prefix='HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 base=W/'pg895-bootstrap-before-v1';assert not Path(str(base)+'.private.log').exists()
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=(prefix+payload(proof,seals)).encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k not in ('toolHashes','proofHashes')}));raise SystemExit(r.returncode)
if __name__=='__main__':main()
