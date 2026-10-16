"""Fresh same-source stopped full11 before unexecuted completed-resume; data, not authority."""
import ast
import inspect
from pyflakes.api import check
from unit_metadata_reference_source import scope
import pg3752_current_preservation_readonly as previous
import pg3822_hygiene_owned_sources as owned
from pg1446_current_cold_stage import W

SOURCE=owned.SOURCE;BOM=owned.BOM;SLOT='pg3840-current-full11-baseline-v1'
AFTER='277f91dc1c1b63f2cea750d0d5b4bdef353d07e74ef0194c05930fa99da00be1'

EXTRA=r'''
states={};cfg={}
for unit,old in expected['units'].items():
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(old))],capture_output=True,text=True,timeout=10);require(r.returncode==0)
 states[unit]=dict(l.split('=',1)for l in r.stdout.splitlines());require(states[unit]==old)
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);require(r.returncode==0)
 cfg[unit]=complete_configuration(r.stdout,unit);require(cfg[unit]==expected['configuration'][unit])
r=subprocess.run(['journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=6f7821fe0af24d95953a9e29abd00c0d','-o','json','--no-pager'],capture_output=True,timeout=20);require(r.returncode==0 and len(r.stdout)<=67108864)
j=json.loads(project(r.stdout));require(j==expected['pid1'])
files={}
for name,item in expected['unitFilesActual'].items():
 p=Path(name);actual=metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()];require(actual==item);files[name]=actual
trees={}
for category,items in categories:
 actual=tree(Path(min(items,key=len)));require(actual==items);trees[category]=actual
runtime=tree(Path('/run/systemd/system'));startup=tree(Path('/run/schubert-nk/startup'));native=tree(Path('/run/schubert-nk/pt-coverage'))
require(set(runtime)=={'/run/systemd/system','/run/systemd/system/schubert-nk-morning-controller.service.d'})
baseline={'units':states,'configuration':cfg,'rows':first,'pid1':j,'startup':startup,'originals':trees['originals'],'backup':trees['backup'],'extraDurable':{'credentials':trees['extraDurable.credentials'],'oldProofs':trees['extraDurable.oldProofs']},'unitFilesActual':files,'runtime':runtime,'native':native}
require(baseline==expected)
for unit,old in states.items():
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(old))],capture_output=True,text=True,timeout=10);require(r.returncode==0 and dict(l.split('=',1)for l in r.stdout.splitlines())==old)
require(read_rows()==first and tree(Path('/run/systemd/system'))==runtime and tree(Path('/run/schubert-nk/startup'))==startup and tree(Path('/run/schubert-nk/pt-coverage'))==native)
save=base/'pg3840-current-full11-baseline-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700);encoded=json.dumps(baseline,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for directory in [save,save.parent]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def payload():
    raw=previous.payload()
    for a,b in [(previous.CURRENT,SOURCE),(previous.BOM,BOM),('PG3420','PG3748'),('pg3420-manifest.sig','pg3748-manifest.sig'),('35f5e07742c6869789f176a3338e9564e2a867039849a6c9230fc4b8147c7317',AFTER),('pg3662-native-stop-v1','pg3822-native-stop-v1'),("==34)","==40)")]:raw=raw.replace(a,b)
    tree=ast.parse(raw);last=tree.body[-1]
    if not isinstance(last,ast.Expr)or not isinstance(last.value,ast.Call)or not isinstance(last.value.func,ast.Name)or last.value.func.id!='print':raise ValueError('one final current readonly boundary')
    raw=''.join(raw.splitlines(keepends=True)[:last.lineno-1]);start=raw.index('units={}')
    values=[]
    for name,names in [('pg3822_configuration_capture.py',{'configuration_value','complete_configuration'}),('pg3822_stable_journal.py',{'pairs','project'})]:
        source=(W/owned.TOOLS/name).read_text()
        values.extend(ast.get_source_segment(source,n)for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name in names)
    header=raw[:start]+'\n'+'\n'.join(values)+"\nFIELDS=set(next(iter(expected['configuration'].values())))\n"
    result=header+scope(raw[start:]+EXTRA)
    result+="print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':data['source']['commit'],'privateBeforeSha256':hashlib.sha256(encoded).hexdigest(),'snapshotKeys':11,'nativeExecs':40,'all10Units18Configuration32AndOriginalJournalUnchanged':True,'all24AndPreservationCategoriesActualRead':{k:len(v)for k,v in categories},'runtimeOnlyOriginalEmptyParent':True,'newTenRefsReturnedNormally':len(refs)==10,'dataOnlyNotAdmissionAuthority':True,'dbWrites':0,'vmConfigurationOrStartStopActions':0,'formalAccepted':False}))\n"
    if check(result,'<fresh current stopped complete11>'):raise ValueError('whole fresh baseline namespace required')
    compile(result,'<current7fff full11/40native/24/187 ownership read>','exec');return result


def main():
    namespace={**previous.__dict__,'CURRENT':SOURCE,'BOM':BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<fresh VM/forward and actual current full11>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
