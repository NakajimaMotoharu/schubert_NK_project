"""Finite once-only publication, using normal M/A/DB/Ref contract; never a Root start."""
import inspect
import pg3454_current_outbox_publication_dispatch as template
import pg3784_hygiene_ro_dispatch as previous
import pg3788_hygiene_publication_sources as role
from pg3790_hygiene_publication_compile import TARGET, generated

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg3792-hygiene-publication-stage-v1'
STAGE=role.bind(template.stage(template.role.ro.role.BOM).replace(template.REMOTE,REMOTE))


def qualify_fixed(fixed):
    names=fixed.get('fileHashes',{})
    required={role.CLASS+'.class',role.CLASS+'.java','Pg3788TransitionTest.class','Pg3788TransitionTest.java','pg3788_ordinary_publication_contract.py','pg3788_native_refs.py'}
    if fixed.get('actualExit')!=0 or fixed.get('candidateSource')!=role.SOURCE or fixed.get('productionSource')!=role.CURRENT or fixed.get('candidateManifestSha256')!=role.BOM or not required.issubset(names)or any(n.startswith('Pg3780')or n.startswith('pg3780_')for n in names):raise ValueError('actual publication ABI tool-kind/target receipt required')


def source():
    raw=inspect.getsource(previous.main).replace('pg3784','pg3792').replace('Pg3780','Pg3788').replace('prepare-ro','activate')
    raw=raw.replace('pg3782-frozen-v1.safe.json','pg3790-frozen-v1.safe.json')
    marker="fixed=json.loads((W/'pg3790-frozen-v1.safe.json').read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one actual publication ABI receipt boundary')
    raw=raw.replace(marker,marker+'\n    qualify_fixed(fixed)')
    raw=raw.replace("'Pg3788InputBoundaryTest',role.CLASS","'Pg3788InputBoundaryTest','Pg3788TransitionTest',role.CLASS")
    raw=raw.replace("'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False","'finiteCodeOnlyPublication':True,'currentApprovalEpochChanged':(False if action=='stage' else True if result.returncode==0 else None)")
    return raw


def main():
    namespace={**previous.__dict__,'role':role,'TARGET':TARGET,'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}
    exec(compile(source(),'<new-only finite publication dispatcher>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
