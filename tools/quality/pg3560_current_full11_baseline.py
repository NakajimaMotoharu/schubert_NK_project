"""Independent actual eleven-key baseline for a future fresh preparation, no write authority."""
import ast
import types
from pyflakes.api import check
import pg3556_current_stopped_readonly as stopped
from pg1446_current_cold_stage import W

SLOT='pg3560-current-full11-baseline-v1'


EXTRA=r'''
def command(args):
 r=subprocess.run(args,capture_output=True,timeout=30);require(r.returncode==0 and len(r.stdout)<=67108864);return r.stdout
FIELDS=set(next(iter(expected['configuration'].values())))
states={};cfg={}
for unit,old in expected['units'].items():
 states[unit]=dict(l.split('=',1)for l in command(['systemctl','show',unit,'--property='+','.join(sorted(old))]).decode().splitlines())
 require(states[unit]==old)
 cfg[unit]=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit)
 require(cfg[unit]==expected['configuration'][unit])
journal_raw=command(['journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=01dd090d1eef4b2ea13afa18cfc00155','-o','json','--no-pager'])
j=json.loads(project(journal_raw));require(j==expected['pid1'])
files={}
for name,item in expected['unitFilesActual'].items():
 p=Path(name);value=metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()];require(value==item);files[name]=value
actual_trees={}
for category,items in preservation_trees(expected):
 actual=tree(Path(min(items,key=len)));require(actual==items);actual_trees[category]=actual
baseline={'units':states,'configuration':cfg,'rows':tables,'pid1':j,'startup':startup,
          'originals':actual_trees['originals'],'backup':actual_trees['backup'],
          'extraDurable':{'credentials':actual_trees['extraDurable.credentials'],'oldProofs':actual_trees['extraDurable.oldProofs']},
          'unitFilesActual':files,'runtime':runtime,'native':native}
require(set(baseline)=={'units','configuration','rows','pid1','startup','originals','backup','extraDurable','unitFilesActual','runtime','native'})
require({k:v for k,v in baseline.items()if k!='native'}==expected)
for unit,old in states.items():
 require(dict(l.split('=',1)for l in command(['systemctl','show',unit,'--property='+','.join(sorted(old))]).decode().splitlines())==old)
 require(complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit)==cfg[unit])
require(tree(Path('/run/systemd/system'))==runtime and tree(Path('/run/schubert-nk/startup'))==startup and tree(Path('/run/schubert-nk/pt-coverage'))==native)
save.mkdir(mode=0o700);encoded=json.dumps(baseline,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for directory in [save,base]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''


def payload():
    raw=stopped.payload()
    raw=raw[:raw.index('save.mkdir(mode=0o700)')]
    raw=raw.replace("save=base/'pg3556-current-stopped-readonly-v2'","save=base/'"+SLOT+"'")
    configuration=(W/'pg3520-outbox-owned-stop-tools-v2/pg3520_configuration_capture.py').read_text()
    journal=(W/'pg3520-outbox-owned-stop-tools-v2/pg3520_stable_journal.py').read_text()
    functions=[]
    for text,names in [(configuration,{'configuration_value','complete_configuration'}),(journal,{'pairs','project'})]:
        functions.extend(ast.get_source_segment(text,n)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name in names)
    # The first seven-field read already authenticates all10 stopped units.
    # A separate fresh ten-Ref scope covers the actual eighteen/config32/journal
    # and independently re-read durable/native return, not expected-value copying.
    start=raw.index('units={}')
    prefix=raw[:start]+'\nimport dbus\n'+'\n'.join(functions)+'\n'
    middle=raw[start:]+EXTRA
    scope="bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]\ntry:\n for unit in expected['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)\n"
    raw=prefix+scope+'\n'.join(' '+line if line else line for line in middle.splitlines())+'\nfinally:\n for unit in reversed(refs):manager.UnrefUnit(unit)\n bus.close()\n'
    raw+="print(json.dumps({'actualExit':0,'privateBeforeSha256':hashlib.sha256(encoded).hexdigest(),'snapshotKeys':11,'source':data['source']['commit'],'all10Units18Configuration32AndOriginalJournalUnchanged':True,'all24And229DurableAndNative28ActualRead':True,'runtimeOnlyOriginalEmptyParent':set(runtime)=={'/run/systemd/system','/run/systemd/system/schubert-nk-morning-controller.service.d'},'newTenRefsReturnedNormally':True,'vmUnitDatabaseWriteOrAdmissionActions':0,'formalAccepted':False}))\n"
    if check(raw,'<current independent full11 baseline>'):raise ValueError('complete current11 globals required')
    compile(raw,'<current actual11 baseline>','exec');return raw


def main():
    fn=stopped.main
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_full11_baseline')()


if __name__=='__main__':raise SystemExit(main())
