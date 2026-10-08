"""BUG851/SSC214: readonly current fixed-pair profile; no stop/start/reload authority."""
import ast, datetime, hashlib, json, os, pathlib, stat, subprocess, sys, time

def require(value):
 if not value: raise ValueError('current recovery profile refused')

def guest():
 import dbus
 require(os.geteuid()==0);os.umask(0o077)
 root=pathlib.Path('/var/lib/pgpt-s1-preservation');save=root/'pg558-profile-v1'
 require(not save.exists())
 witness=(root/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
 require(hashlib.sha256(witness).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 names={'command','show','metadata','tree','configuration_fields'};parsed=ast.parse(witness)
 nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names]
 require(len(nodes)==len(names))
 nodes += [n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'UNITS','FIELDS'} for t in n.targets)]
 env={'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'pathlib':pathlib,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<sealed readonly>','exec'),env)
 command,show,metadata,tree,cfg=(env[n] for n in ('command','show','metadata','tree','configuration_fields'))
 units,fields=env['UNITS'],env['FIELDS'];old=root/'pg557-native-stop-v1';tools=root/'pg557-native-tools-v1'
 before=json.loads((old/'before.private.json').read_bytes());require(len(before['rows'])==24)
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 try:
  for u in units: manager.RefUnit(u);refs.append(u)
  def capture():
   result={'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'units':{u:show(u,fields) for u in units},'configuration':{u:show(u,cfg()) for u in units},'dependencies':{u:{k:sorted(v.split()) for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()} for u in units},'oldProofs':tree(old),'payloads':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metadata':metadata(p),'xattrs':os.listxattr(p)} for p in tools.iterdir()},'locks':{n:metadata(pathlib.Path('/run/schubert-nk')/n) for n in ('maintenance.lock','startup-admission.lock')},'actors':{},'pid1Stop':{}}
   for pid in (900001,900030):
    p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text().rpartition(')')[2].split()
    result['actors'][str(pid)]={'pid':pid,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),'children':sorted({int(c) for t in (p/'task').iterdir() for c in (t/'children').read_text().split()}),'fds':sorted({str(p.readlink()) for p in (p/'fd').iterdir()})}
   for u in ('schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service'):
    raw=command(['/usr/bin/journalctl','--boot='+result['boot'].replace('-',''),'_PID=1','UNIT='+u,'-o','json','--no-pager'])
    entries=[json.loads(l) for l in raw.splitlines()]
    done=[r for r in entries if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286' and r.get('JOB_TYPE')=='stop' and r.get('JOB_RESULT')=='done' and r.get('INVOCATION_ID')==before['units'][u]['InvocationID'] and int(r['__MONOTONIC_TIMESTAMP'])>=int(before['units'][u]['ExecMainStartTimestampMonotonic'])]
    require(len(done)==1);result['pid1Stop'][u]=done[0]
   q="begin isolation level repeatable read read only;set local timezone='UTC';"
   for t in before['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
   result['rows']={}
   for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
    v=json.loads(line);require(v['table'] not in result['rows']);result['rows'][v['table']]=v['rows']
   for n,p in {'startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage'}.items():result[n]=tree(pathlib.Path(p))
   result['current']=str(pathlib.Path('/opt/schubert-nk/current').readlink())
   result['manifestSha256']=hashlib.sha256(pathlib.Path(result['current'],'RELEASE-MANIFEST.json').read_bytes()).hexdigest()
   return result
  value=capture();require(value==capture());require(value['rows']==before['rows'])
  require(all(value[n]==before[n] for n in ('startup','originals','backup')))
  require(value['actors']['900001']['children']==[900030] and value['actors']['900030']['children']==[])
  require(len(value['payloads'])==7)
  save.mkdir(mode=0o700)
  with (save/'profile.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
  print(json.dumps({'readOnly':True,'all24UnchangedTwice':True,'profileSha256':hashlib.sha256((save/'profile.private.json').read_bytes()).hexdigest(),'actors':{k:{n:v[n] for n in ('pid','ticks','argv','parent','children')} for k,v in value['actors'].items()},'payloads':{k:v['sha256'] for k,v in value['payloads'].items()},'locks':value['locks'],'beforeSha256':hashlib.sha256((old/'before.private.json').read_bytes()).hexdigest(),'errorSha256':hashlib.sha256((old/'refs-prepare.private.log').read_bytes()).hexdigest(),'stopJobs':{k:{n:v.get(n) for n in ('JOB_ID','__MONOTONIC_TIMESTAMP','INVOCATION_ID')} for k,v in value['pid1Stop'].items()},'manifestSha256':value['manifestSha256']}))
 finally:
  for u in reversed(refs): manager.UnrefUnit(u)
  bus.close()

if __name__=='__main__':
 if os.geteuid()==0:guest()
 else:
  os.umask(0o077);p=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
  cmd=['ssh','-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
  with (w/'pg558-profile-v1.private.log').open('xb') as f:r=subprocess.run(cmd,input=pathlib.Path(__file__).read_bytes(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  with (w/'pg558-profile-v1.exit').open('x') as f:f.write(str(r.returncode)+'\n')
  print('PG558_PROFILE actualExit='+str(r.returncode));sys.exit(r.returncode)
