"""SSC291 explicit current-instance source literals, never reinterpret old Java bytes as new."""
import json
import re
import pg4088_failed_done_owned_sources as previous
from pg1446_current_cold_stage import W
from pg4260_stable_admission_image import live,SOURCE,BOM as BOM

TOOLS='pg4312-current-failed-owned-tools-v1'
INSPECT='pg4314-current-failed-owned-inspect-v1'


def actors():
    value=json.loads((W/'pg4310-current-actor-projection-v1/manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['source']!=SOURCE or value['result']['BOM']!=BOM or value['result']['referenceSha256']!='63269de90bc6bb554e73bde70dcb44bb8e844424c7b364f6597ed1d08aaaf1fd':raise ValueError('actual pinned current identity projection required')
    return value['result']['actors']


def bind_instance(raw):
    b=live();a=actors()
    pairs={'dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f':b['run'],'2026-10-16T05:44:47.267413Z':b['cutoff'],
           'd9d58371-bf80-49f6-bad9-3d1e0916fb04':b['activation'],'820851b8291a4c958bb34f6c48430ca3':b['invocation'],
           'c9444dbf2e6a43dca0d52ab220d59b1d':a['schubert-nk-api.service']['invocation'],
           'af0eb750d72443739bead6a879a51e13':a['schubert-nk-web.service']['invocation'],
           'a0c7fb91c4da42f09faec0f065a87767':a['caddy.service']['invocation'],
           '9cb091b80682402aaed1d2d1d2d2a5d7':a['artemis.service']['invocation']}
    for old,new in pairs.items():raw=raw.replace(old,new)
    numbers={'696557':b['rootPid'],'12873540':14962226,'758821':a['schubert-nk-api.service']['pid'],
             '13004447':a['schubert-nk-api.service']['ticks'],'759868':a['schubert-nk-web.service']['pid'],'13005817':a['schubert-nk-web.service']['ticks']}
    for old,new in numbers.items():raw=re.sub(r'(?<![A-Za-z0-9_])'+old+r'(?![A-Za-z0-9_])',str(new),raw)
    return raw


def java():return bind_instance(previous.java())


def files():
    values=previous.files();values['RootFailedDoneRecovery.java']=java()
    values['recovery_plan.py']=bind_instance(values['recovery_plan.py'])
    return values
