"""Independent current all11 read plus literal-only runtime/config delta after finite prepare."""
import ast
import inspect
import json
import types
from pyflakes.api import check
import pg3556_current_stopped_readonly as stopped
from pg3564_current_browser_resume_sources import SOURCE, BOM, BEFORE, BASELINE, TOOLS, SAVE
from pg1446_current_cold_stage import W
from pg2956_current_resume_independent_post import ORACLE
from pg2978_current_resume_post_exports import EXPORTS
from pg3066_browser_resume_post import existing_parent_metadata

SLOT='pg3570-current-browser-resume-independent-post-v1'


def independent_delta():
    raw=ORACLE.replace('CONFIG_MODULE','pg3564_configuration').replace('pg2950','pg3564')
    raw=raw.replace('from pg3564_configuration import exec_record,config_same',EXPORTS.replace('pg2970','pg3564'))
    start=raw.index("require(0<lower<=upper and set(initial['runtime'])=={root}")
    end=raw.index("require(prepared[root]['sha256']",start)
    raw=raw[:start]+"existing_parent_metadata(initial['runtime'],prepared,root,directory,target,lower,upper,literal)\nrequire(not (fresh/'runtime-parent-created.private.json').exists())\n"+raw[end:]
    # Independent literal oracle, not the mutation writer's dropin method.
    return inspect.getsource(existing_parent_metadata)+'\n'+raw


def payload():
    build=json.loads((W/'pg3566-frozen-v1.safe.json').read_bytes())
    if not(build['actualExit']==0 and build['sourceQualified'] and build['productionSource']==SOURCE and build['candidateManifestSha256']==BOM):
        raise ValueError('actual current six ABI phases required')
    raw=stopped.payload().replace('pg3556-current-stopped-readonly-v2',SLOT)
    marker="expected=json.loads(after_raw);require(len(expected['rows'])==24 and len(expected['units'])==10)"
    delta="""
import sys,ast,pathlib
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/TOOLS_LITERAL')
tools=Path('/var/lib/pgpt-s1-preservation/TOOLS_LITERAL')
pins=json.loads((tools/'payload-sha256.json').read_bytes());require(pins==PIN_LITERAL)
for name,digest in pins.items():
 p=tools/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require({p.relative_to(tools).as_posix()for p in tools.rglob('*')if p.is_file()}==set(pins)|{'payload-sha256.json'})
baseline=Path(BASELINE_LITERAL).read_bytes();require(hashlib.sha256(baseline).hexdigest()==BEFORE_LITERAL)
after=json.loads(baseline);require(len(after)==11 and {k:v for k,v in after.items()if k!='native'}==expected)
require(after['native']==tree(Path('/run/schubert-nk/pt-coverage')))
FRESH=SAVE_LITERAL
RESUME_RUN='e1ee096d-370b-4ab9-915a-7c124207e854'
""".replace('TOOLS_LITERAL',TOOLS).replace('PIN_LITERAL',repr(build['fileHashes'])).replace('BASELINE_LITERAL',repr(BASELINE)).replace('BEFORE_LITERAL',repr(BEFORE)).replace('SAVE_LITERAL',repr(SAVE))
    delta+=independent_delta()+"\nexpected=after\n"
    if raw.count(marker)!=1:raise ValueError('single independently qualified original anchor required')
    raw=raw.replace(marker,marker+'\n'+delta)
    # The stopped reader separately checks all24/229durable/native28/current187,
    # kernel/job/client/advisory/flock0. Add actual18/config32/original journal.
    functions=[]
    for filename,names in [('pg3520_configuration_capture.py',{'configuration_value','complete_configuration'}),('pg3520_stable_journal.py',{'pairs','project'})]:
        text=(W/'pg3520-outbox-owned-stop-tools-v2'/filename).read_text()
        functions.extend(ast.get_source_segment(text,n)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name in names)
    extra="""
def command(args):
 r=subprocess.run(args,capture_output=True,timeout=30);require(r.returncode==0 and len(r.stdout)<=67108864);return r.stdout
FIELDS=set(next(iter(expected['configuration'].values())))
for unit,old in expected['units'].items():
 actual=dict(l.split('=',1)for l in command(['systemctl','show',unit,'--property='+','.join(sorted(old))]).decode().splitlines());require(actual==old)
 actual_cfg=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(expected['configuration'][unit]))]).decode(),unit);require(actual_cfg==expected['configuration'][unit])
for path,item in expected['unitFilesActual'].items():
 p=Path(path);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)
journal_raw=command(['journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=01dd090d1eef4b2ea13afa18cfc00155','-o','json','--no-pager']);require(json.loads(project(journal_raw))==expected['pid1'])
require(tree(Path('/run/systemd/system'))==expected['runtime']and tree(Path('/run/schubert-nk/pt-coverage'))==expected['native'])
"""
    raw=raw.replace('save.mkdir(mode=0o700)','\n'+'\n'.join(functions)+'\n'+extra+'\nsave.mkdir(mode=0o700)',1)
    raw=raw.replace("'afterSha256':AFTER_SHA","'afterSha256':AFTER_SHA,'independentPreparedAfterSha256':hashlib.sha256(fresh_private('after.private.json')).hexdigest(),'initialBaselineSha256':hashlib.sha256(baseline).hexdigest()")
    raw=raw.replace("'formalAccepted':False}))","'formalAccepted':False,'independentResumeOnlyDeltaVerified':True,'all11And18Config32AndOriginalJournalVerified':True,'preparedAfterSha256':hashlib.sha256(fresh_private('after.private.json')).hexdigest()}))")
    # Cover the whole read with ten fresh RefUnit handles; always normal Unref.
    start=raw.index('units={}')
    prefix=raw[:start]+'\nimport dbus\n'
    tail=raw[start:]
    raw=prefix+"bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]\ntry:\n for unit in expected['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)\n"+'\n'.join(' '+l if l else l for l in tail.splitlines())+"\nfinally:\n for unit in reversed(refs):manager.UnrefUnit(unit)\n bus.close()\n"
    if check(raw,'<independent current fresh-resume post>'):raise ValueError('complete final read-only globals required')
    compile(raw,'<independent current literal11 post>','exec');return raw


def main():
    actual=json.loads((W/'pg3568-prepare-resume-v1.safe.json').read_bytes())
    if not(actual['actualExit']==0 and actual['sourceQualified'] and actual['freshResumeRuntimePrepared'] and actual['normalSingleRuntimeReload']):
        raise ValueError('actual completed normal preparation required')
    fn=stopped.main
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_resume_independent_post')()


if __name__=='__main__':raise SystemExit(main())
