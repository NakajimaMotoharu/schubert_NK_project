"""Independent current Bootstrap20/full24/full32/signature/resources post, no Unit action."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg895_bootstrap_before import payload as previous,W,P
from pg894_sources_v3 import files
R=Path(__file__).resolve().parent
EXTRA='''
fixed=base/'pg894-bootstrap-existing-v3'
def newproof(name):
 p=fixed/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 value=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return value
boot_raw_before=newproof('before.private.json');boot_raw_after=newproof('after.private.json')
boot_before=json.loads(boot_raw_before);boot_after=json.loads(boot_raw_after)
require(newproof('complete.private')==b'allNewScopesReturnedNormally=true\\nall24DatabaseUnchanged=true\\nmode=execute\\n')
bootstrap=CONTRACT['UNIT'];terminal=boot_after['units'][bootstrap]
CONTRACT['same_terminal_cohort'](boot_before['units'],boot_after['units'],terminal)
require(boot_before['units']==after['units']and boot_before['configuration']==after['configuration']and boot_before['rows']==boot_after['rows']==after['rows'])
require(all(CONFIG['same'](after['configuration'][u],boot_after['configuration'][u],exec_record)for u in after['units']))
CONTRACT['credential_tree'](boot_before['credentials'],boot_after['credentials'],{})
baseline895=json.loads(strict(base/'pg895-bootstrap-before-v1/after.private.json',0o600,33554432))
require(boot_before['native']==baseline895['native'])
CONTRACT['native_tree'](boot_before['native'],boot_after['native'],terminal['InvocationID'])
for name in CONTRACT['SOURCES']:
 p=fixed/(name+'.retired.private');s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and 0<s.st_size<=256 and not os.path.lexists('/etc/schubert-nk/credentials/'+name))
require(boot_after['credentials']==tree(pathlib.Path('/etc/schubert-nk/credentials')))
journal=newproof('pid1.private.jsonl');journal_rows=[json.loads(l)for l in journal.splitlines()]
done=[v for v in journal_rows if v.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and v.get('JOB_TYPE')=='start'and v.get('JOB_RESULT')=='done'];require(len(done)==1)
d=done[0];require(d.get('_BOOT_ID')=='cc9ed8747f4f450ea1888de1e42c8441'and d.get('_PID')=='1'and d.get('_UID')=='0'and d.get('INVOCATION_ID')==terminal['InvocationID'])
start=int(terminal['ExecMainStartTimestampMonotonic']);end=int(terminal['ExecMainExitTimestampMonotonic']);require(0<end-start<=30000000)
bootstrap_meta={'unitElapsedSeconds':(end-start)/1000000,'actualPid1Job':d['JOB_ID'],'invocationSha256':hashlib.sha256(terminal['InvocationID'].encode()).hexdigest(),'lowerMs':(int(d['__REALTIME_TIMESTAMP'])-(int(d['__MONOTONIC_TIMESTAMP'])-start))//1000-1000,'upperMs':int(d['__REALTIME_TIMESTAMP'])//1000+1000,'files':[]}
for suffix in ('terminal.exec','closing.exec'):
 p=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-bootstrap196')/(terminal['InvocationID']+'.'+suffix)
 bootstrap_meta['files'].append({'relative':str(p.relative_to('/run/schubert-nk/pt-coverage')),'sha256':boot_after['native'][str(p)]['sha256'],'bytes':boot_after['native'][str(p)]['metadata'][6]})
after={**after,'units':boot_after['units'],'configuration':boot_after['configuration']}
'''
def payload(proof,seals):
 raw=previous(proof,seals)
 generated=files('2a4f222e0d9759ac7c764f3e3c581a9774ad74de01971f15bf28e759dbc04e6e')
 prefix="CONTRACT={};exec("+repr(generated['pg894_bootstrap_contract.py'])+",CONTRACT)\nCONFIG={};exec("+repr(generated['pg894_configuration.py'])+",CONFIG)\n"+generated['pg894_exec_record.py']+'\n'
 marker='bus=dbus.SystemBus(private=True);';assert raw.count(marker)==1
 raw=raw.replace(marker,prefix+EXTRA+'\n'+marker)
 marker='native=snapshot();require(native==snapshot())';assert raw.count(marker)==1
 raw=raw.replace(marker,marker+";require(native==boot_after['native']and boot_raw_before==newproof('before.private.json')and boot_raw_after==newproof('after.private.json'))")
 raw=raw.replace('pg895-bootstrap-before-v1\';require(not os.path.lexists(save))','pg901-bootstrap-post-v1\';require(not os.path.lexists(save))')
 raw=raw.replace("'run':'PG895-bootstrap-before-v1'","'run':'PG901-bootstrap-post-v1'")
 marker="with(save/'result.safe.json').open('x')as f:";assert raw.count(marker)==1
 raw=raw.replace(marker,"result['bootstrap']=bootstrap_meta\nresult['bootstrapProofHashes']={name:hashlib.sha256(newproof(name)).hexdigest()for name in ('before.private.json','after.private.json','pid1.private.jsonl','complete.private')}\nresult['currentCredentialsRetired']=True\n"+marker)
 ast.parse(raw);return raw
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert(W/'pg894-execute-v3.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg885-completed-readonly-v1.safe.json').read_bytes());final=json.loads((W/'pg890-terminal-final-v1.safe.json').read_bytes());seals={k:v['sha256']for k,v in final['proofHashes'].items()if k in('before.private.json','after.private.json','parent.private.jsonl','complete.private')}
 prefix='HASHES='+repr(final['toolHashes'])+'\nRECEIPT='+repr((W/'pg887-native-tools-v1/pg887_parent_receipt.py').read_text())+'\n'
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 base=W/'pg901-bootstrap-post-v1';assert not Path(str(base)+'.private.log').exists()
 started=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=(prefix+payload(proof,seals)).encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps({k:v for k,v in safe.items()if k not in('toolHashes','proofHashes','bootstrap')}));raise SystemExit(r.returncode)
if __name__=='__main__':main()
