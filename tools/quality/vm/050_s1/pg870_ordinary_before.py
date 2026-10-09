"""Fresh canonical private pre-start snapshot, exact869 and signed default noargs."""
import ast,inspect,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg869_completed_codeonly_post import payload as previous
from pg870_ordinary_policy import ordinary_argv
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def parser_source():
    raw=(Path(__file__).parent/'pg477_unit_references.py').read_text()
    tree=ast.parse(raw);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='exec_record'];assert len(nodes)==1
    return ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'
EXTRA='''
def tree_snapshot(root):
 p=pathlib.Path(root);v={}
 for q in (p,*sorted(p.rglob('*'))):
  s=q.lstat();assert not q.is_symlink()and (stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode))
  v[str(q)]={'metadata':metadata(s),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()if q.is_file()else None};assert metadata(q.lstat())==metadata(s)
 return v
def standard_snapshot(value):
 unit_files={}
 for config in value['configuration'].values():
  for name in (config['FragmentPath'],*config['DropInPaths'].split()):
   assert name.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/'))
   p=pathlib.Path(name);s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==0 and not stat.S_IMODE(s.st_mode)&0o022 and s.st_nlink==1
   unit_files[name]={'metadata':metadata(s),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert metadata(p.lstat())==metadata(s)
 assert unit_files==baseline['unitFiles']
 unit_values={u:dict(line.split('=',1)for line in text.splitlines())for u,text in value['units'].items()}
 trees={name:tree_snapshot(name)for name in baseline['trees']}
 assert finite_trees(baseline['trees'],trees,'after',expected_epoch)
 command=ordinary_argv((candidate/'systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 declaration=exec_record(value['configuration']['schubert-nk-morning-controller.service']['ExecStart']);assert declaration is not None and declaration[:3]==('/usr/bin/java',command,'no')
 assert '--resume'not in command
 return {'units':unit_values,'configuration':value['configuration'],'rows':value['rows'],'trees':trees,'unitFiles':unit_files,'current':value['current'],'coverageBefore':tree_snapshot('/run/schubert-nk/pt-coverage'),'ordinaryNoargs':True,'oldOriginalCompleted':True,'oldParent143NotAccepted':True}
'''
def payload():
 raw=previous().replace('pg869-current862-post-v1','pg870-ordinary-before-v1')
 raw=raw.replace('with StageReferences():',inspect.getsource(ordinary_argv)+'\n'+parser_source()+'\n'+EXTRA+'\nwith StageReferences():')
 raw=raw.replace("resources();value=protected();assert value==protected();resources()",'''resources();limited=protected();assert limited==protected();resources()
 assert limited==json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg869-current862-post-v1/after.private.json').read_bytes())
 value=standard_snapshot(limited);assert value==standard_snapshot(protected())''')
 raw=raw.replace("'startupEntries':47,", "'startupEntries':47,'ordinaryNoargs':True,'unitFileCount':len(value['unitFiles']),'nativeBeforeCount':len(value['coverageBefore']),")
 ast.parse(raw);return raw
if __name__=='__main__':
 os.umask(0o077);assert json.loads((W/'pg869-current862-post-v1.safe.json').read_bytes())['actualExit']==0
 base=W/'pg870-ordinary-before-v1';assert not Path(str(base)+'.private.log').exists()
 cmd=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(cmd,input=payload().encode(),capture_output=True)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 safe={'run':'PG870-ordinary-before-v1','actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.flush();os.fsync(f.fileno())
 print(json.dumps(safe));raise SystemExit(r.returncode)
