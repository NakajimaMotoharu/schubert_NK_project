"""Capture actual new-day Root generations; observations are not stop/permit authority."""
import hashlib
import inspect
import json
from pg1700_new_source_live_binding import prior,body as old_body,SOURCE,DIGEST
from pg1446_current_cold_stage import W

def captured_parent(start,before,payload_sha):
    if type(start)is not dict or type(before)is not dict or type(start.get('actualExit'))is not int or start['actualExit']!=0 or type(before.get('actualExit'))is not int or before['actualExit']!=0:
        raise ValueError('actual successful start/before required')
    before=before.get('guest')
    if type(before)is not dict or type(before.get('actualExit'))is not int or before['actualExit']!=0 or before.get('productionSource')!=SOURCE or before.get('whole24Full32Signed187AndResourcesUnchanged')is not True or type(before.get('todayBatchRows'))is not int or before['todayBatchRows']!=0 or before.get('investigationBusinessDay')!='2026-10-13' or before.get('startAuthority')is not False:
        raise ValueError('fresh whole current-day before required')
    if type(payload_sha)is not str or len(payload_sha)!=64 or any(c not in '0123456789abcdef'for c in payload_sha)or start.get('payloadSha256')!=payload_sha:
        raise ValueError('fixed once operator byte required')
    p=start.get('guest')
    if type(p)is not dict or type(p.get('clientExit'))is not int or p['clientExit']!=0 or p.get('ordinaryNoargs')is not True or p.get('oldCompletedRunNotResumed')is not True or p.get('originalBudgetSeconds')!=1800:
        raise ValueError('ordinary one-start receipt required')
    expected={k:p.get(k)for k in ('MainPID','InvocationID','Job','ExecMainStartTimestampMonotonic')}
    for k in ('MainPID','Job','ExecMainStartTimestampMonotonic'):
        if type(expected[k])is not str or not expected[k].isdecimal()or not 0<int(expected[k])<=9223372036854775807 or str(int(expected[k]))!=expected[k]:raise ValueError('actual positive generation fields required')
    if int(expected['MainPID'])<2 or int(expected['MainPID'])>2147483647 or type(expected['InvocationID'])is not str or len(expected['InvocationID'])!=32 or set(expected['InvocationID'])=={'0'}or any(c not in '0123456789abcdef'for c in expected['InvocationID']):raise ValueError('actual PID/Invocation required')
    return expected

def body():
    raw=old_body()
    marker="for name,expected in [('runs/'"
    if raw.count(marker)!=1:raise ValueError('one original content guard point required')
    raw=raw.replace(marker,"require(cut.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()=='2026-10-13')\n"+marker)
    return raw

def main():
    start=json.loads((W/'pg1759-next-day-ordinary-once-v1/manifest.safe.json').read_bytes())
    before=json.loads((W/'pg1757-next-business-day-before-v1/manifest.safe.json').read_bytes())
    sha=hashlib.sha256((W/'pg1759-next-day-ordinary-once-v1/payload.private.py').read_bytes()).hexdigest()
    expected=captured_parent(start,before,sha)
    raw=inspect.getsource(prior.main).replace('pg1320-published-ordinary-once-v1.safe.json','pg1759-next-day-ordinary-once-v1/manifest.safe.json').replace('pg1321-live-root-binding-v1','pg1761-next-day-live-binding-v1')
    marker="if start['actualExit']!=0 or start['productionSource']!=SOURCE or not start['externalStartIssuedOnce']:raise ValueError('actual once start required')"
    if raw.count(marker)!=1:raise ValueError('one old flat envelope guard required')
    raw=raw.replace(marker,'expected=EXPECTED_PARENT').replace("repr(start['parent'])",'repr(expected)')
    ns={**prior.__dict__,'BODY':body(),'SOURCE':SOURCE,'DIGEST':DIGEST,'EXPECTED_PARENT':expected}
    exec(compile(raw,'<actual next-day readonly generation transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
