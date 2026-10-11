"""Current769 same-byte14 exec coordinates; no new VM action or exclusions."""
import inspect
import pg1271_current_native_gap as previous
from pg1293_completed_unused_stage_sources import SOURCE

NATIVE_SHA='99ace9ae4497d33c331700ec656502e543de2e64192ba5350b4f1dfa456f4d71'
HOST_SHA='1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b'

def source():
    code=inspect.getsource(previous.main)
    for old,new in [('pg1258-fresh-ten-native-v1','pg1341-published-eight-native-v1'),('pg1018-stream-six-host-v2','pg1279-held-channel-six-host-v1'),
      ("record['qualifiedCurrentNativeSubcampaign']is True and ",''),("record['currentNativeStreams']==10","record['currentNativeStreams']==8"),
      ("len(record['selected'])==10","len(record['selected'])==8"),('len(data)==16','len(data)==14'),('pg1271-current-native-gap-v1','pg1342-published-current-native-gap-v1'),("'currentNativeExecCount':10","'currentNativeExecCount':8")]:
        if old not in code:raise ValueError('exact current native/host gap join required')
        code=code.replace(old,new)
    compile(code,'<actual newsource same-byte coordinates>','exec');return code

def main():
    env=dict(previous.__dict__,SOURCE=SOURCE,NATIVE_SHA=NATIVE_SHA,HOST_SHA=HOST_SHA)
    exec(compile(source(),'<actual same-byte newsource gap>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
