"""Fresh failed0ea / no-DONE / sole Artemis capture; no operation authority or normal receipt."""
import ast
import inspect
from pyflakes.api import check
import pg4052_failed_current_capture as base
import pg4080_failed_ordinary_full_capture as detailed
import pg5644_current_admission_image as admission
from pg4060_original_profile_dual_stack import once

SLOT='pg5712-failed-cohort-full-capture-v1'


def payload(binding):
    raw=base.payload();raw=raw[:raw.index('import dbus\nbus=')]
    for old,new in((base.SLOT,SLOT),(base.SOURCE,admission.SOURCE),(base.BOM,admission.BOM),
        ('PG3976','PG5598'),('pg3976-manifest.sig','pg5598-manifest.sig'),
        ('pg4008-literal-invariant-publication-independent-post-v1','pg5630-current-publication-independent-post-v1'),
        ('33b24b767326879adff27c1ee38aaa08102e347d04d631947047ef667f3352c6',admission.PUBLICATION),
        ('820851b8291a4c958bb34f6c48430ca3',binding['invocation'])):
        if old not in raw:raise ValueError('one required current-instance binding missing')
        raw=raw.replace(old,new)
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='expected_inv'for t in n.targets))
    raw=once(raw,ast.get_source_segment(raw,node),"expected_inv={'artemis.service':'696929e56d38402caeb0e36bfabf854e'}")
    raw=once(raw,"m['Result']=='timeout' and m['ExecMainStatus']=='143'","m['Result']=='exit-code' and m['ExecMainStatus']=='30'")
    raw=once(raw," return result,actors", " require(m['ExecMainStartTimestampMonotonic']=="+repr(str(binding['start']))+" and m['ExecMainExitTimestampMonotonic']=='419090570752')\n require(set(actors)=={'artemis.service'} and actors['artemis.service']['pid']==967597 and actors['artemis.service']['ticks']==41807207 and result['artemis.service']['ExecMainStartTimestampMonotonic']=='418072075417')\n return result,actors")
    body=detailed.BODY
    body=once(body,"require(current.resolve(strict=True)==root and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)",
      "require(current.resolve(strict=True)==root and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)\nrequire(not Path('/proc/"+str(binding['rootPid'])+"').exists()and not Path('/var/lib/schubert-nk/maintenance/attempts/"+binding['activation']+".done').exists())\nrequire(first['detailedActors']==second['detailedActors']and set(second['actors'])=={'artemis.service'} and not second['database']['peers'])")
    body=once(body,"'ordinaryIdentityAllFourVerified':True", "'soleCurrentArtemisIdentityVerified':True,'failedRoot30StillFailed':True,'doneAbsent':True")
    result=raw+'\n'+detailed.contracts()+'\nACTOR_POLICY='+repr(inspect.getsource(detailed.policy))+'\n'+body
    if check(result,'<current failed0ea sole-Artemis capture>'):raise ValueError('complete standalone reader must be static0 before SSH')
    compile(result,'<current failed-cohort capture>','exec')
    return result


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(admission.live()),240))
