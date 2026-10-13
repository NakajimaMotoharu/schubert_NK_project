"""Independent all-resource post after current Ref/Java handoff; no prepare replay."""
import json
import types
import pg2280_current_signed_owned_post as current
from pg1446_current_cold_stage import W

SLOT='pg2313-current-resume-recovery-post-v1'


def payload(seals):
    raw=current.payload(seals).replace(current.SLOT,SLOT).replace('PG2281-current-signed-owned-post-v2','PG2313-current-resume-recovery-post-v1')
    marker="save = base / '"+SLOT+"'"
    extra="""require(not pathlib.Path('/proc/96640').exists()and not pathlib.Path('/proc/96671').exists()and not pathlib.Path('/proc/96669').exists())
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists())
failed=base/'pg2308-current-completed-resume-preparation-v1'
require({p.name for p in failed.iterdir()}=={'refs-prepare.private.log'})
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='09640d25fa96fd2599a0a3e3e52bbb20331501bf245c51a762dab611d3a8ac5a')
result.update(currentFailedPreparationPairGone=True,runtimeWriteReload0=True,oldPreparationExit143NotNormalized=True)
"""
    if raw.count(marker)!=1:raise ValueError('one independent new recovery post save required')
    raw=raw.replace(marker,extra+marker)
    compile(raw,'<independent current resume recovery whole post>','exec')
    return raw


def main():
    recovered=json.loads((W/'pg2311-current-resume-pair-handoff-v1/manifest.safe.json').read_bytes())
    if recovered['actualExit']!=0 or len(recovered['stages'])!=2 or recovered['stages'][-1].get('ownedActorsDBAdvisoryFlockAndBusGone')is not True:
        raise ValueError('actual owned current pair gone required')
    entry=current.entry()
    fn=types.FunctionType(entry.__code__,{**entry.__globals__,'SLOT':SLOT,'payload':payload},'current_resume_recovery_post')
    return fn()


if __name__=='__main__':raise SystemExit(main())
