"""Independent exact resume-only delta plus current full11/40 native resource post."""
import inspect
import json
from pyflakes.api import check
import pg3842_current_full11_native_baseline as baseline
import pg3844_current_resume_sources as role
import pg3570_current_browser_resume_post as previous
from pg1446_current_cold_stage import W

SLOT='pg3850-current-resume-independent-post-v1'


def payload():
    fixed=json.loads((W/'pg3846-frozen-v1.safe.json').read_bytes())
    if not(fixed['actualExit']==0 and fixed['sourceQualified'] and fixed['productionSource']==role.SOURCE and fixed['candidateManifestSha256']==role.BOM):
        raise ValueError('actual current six-phase immutable ABI required')
    raw=baseline.payload().replace(baseline.SLOT,SLOT)
    marker="require(native_now==tree(Path('/run/schubert-nk/pt-coverage'))and len(expected['rows'])==24 and len(expected['units'])==10)"
    if raw.count(marker)!=1:raise ValueError('single strict full11 baseline boundary')
    delta="""
import sys,ast,pathlib,re
tools=Path(TOOLS_LITERAL);sys.path.insert(0,str(tools))
pins=json.loads((tools/'payload-sha256.json').read_bytes());require(pins==PIN_LITERAL)
for name,digest in pins.items():
 p=tools/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require({p.relative_to(tools).as_posix()for p in tools.rglob('*')if p.is_file()}==set(pins)|{'payload-sha256.json'})
baseline_raw=Path(BASELINE_LITERAL).read_bytes();require(hashlib.sha256(baseline_raw).hexdigest()==BEFORE_LITERAL)
after=json.loads(baseline_raw);require(after==expected and len(after)==11)
FRESH=SAVE_LITERAL
RESUME_RUN=RUN_LITERAL
""".replace('TOOLS_LITERAL',repr('/var/lib/pgpt-s1-preservation/'+role.TOOLS)).replace('PIN_LITERAL',repr(fixed['fileHashes'])).replace('BASELINE_LITERAL',repr(role.BASELINE)).replace('BEFORE_LITERAL',repr(role.BEFORE)).replace('SAVE_LITERAL',repr(role.SAVE)).replace('RUN_LITERAL',repr(role.RUN))
    delta+=role.bind(previous.independent_delta())+'\nexpected=after\n'
    raw=raw.replace(marker,marker+'\n'+delta)
    # The independent literal delta above proves exactly the one new drop-in;
    # subsequent fresh complete read must equal that independently derived tree.
    old=" require(set(runtime)=={'/run/systemd/system','/run/systemd/system/schubert-nk-morning-controller.service.d'})"
    if raw.count(old)!=1:raise ValueError('one old empty-runtime check')
    raw=raw.replace(old," require(runtime==expected['runtime'])")
    raw=raw.replace("'runtimeOnlyOriginalEmptyParent':True","'independentResumeOnlyDeltaVerified':True,'all11And18Config32AndOriginalJournalVerified':True,'preparedAfterSha256':hashlib.sha256(fresh_private('after.private.json')).hexdigest(),'initialBaselineSha256':hashlib.sha256(baseline_raw).hexdigest()")
    raw=raw.replace("'vmConfigurationOrStartStopActions':0","'vmConfigurationOrStartStopActions':0,'normalSingleRuntimeReloadIndependentlyVerified':True")
    if check(raw,'<current exact resume-only independent full post>'):raise ValueError('whole independent post namespace')
    compile(raw,'<strict current prepared full11 independent observation>','exec')
    return raw


def main():
    actual=json.loads((W/'pg3848-prepare-resume-v1.safe.json').read_bytes())
    if not(actual['actualExit']==0 and actual['sourceQualified'] and actual['candidateSource']==role.SOURCE and actual['freshResumeRuntimePrepared'] and actual['normalSingleRuntimeReload']):
        raise ValueError('actual finite current preparation required')
    transport=baseline.previous.previous
    namespace={**transport.__dict__,'CURRENT':role.SOURCE,'BOM':role.BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(transport.main),'<new current read-only post transport>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
