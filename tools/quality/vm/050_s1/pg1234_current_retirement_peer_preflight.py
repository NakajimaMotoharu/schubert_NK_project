"""Fresh actual full current/schema join after fixed owner recovery, no mutation."""
import inspect
import pg1222_completed_retirement_preflight as transport
import pg1229_actual_runtime_schema_preflight_v2 as previous

def payload():
    s=previous.payload().replace('PG1229-runtime-schema-preflight-v2','PG1234-current-retirement-peer-preflight-v1')
    extra="raw=(base/'pg1231-current-retirement-handoff-v1/after.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='4a09d2fab4346eef21b0505fcd656ed65d78520801fcc0736d5c313e5fab0f4d');fixed_post=json.loads(raw)\nrequire(fixed_post['current']==after and fixed_post['native']==native and fixed_post['source']=='d5b00104280028d9ea81b44c1d1c805f3c2861ed' and fixed_post['fixedOldOwnerGone'] and fixed_post['allClientsAdvisoryFlocks0'] and fixed_post['oldNormalClose']is False)\nrequire(not pathlib.Path('/proc/560237').exists()and not pathlib.Path('/proc/560266').exists())\nresult.update(fixedOldRecoveryPostVerified=True,oldNormalClose=False)\n"
    if s.count('print(json.dumps(result))')!=1:raise ValueError('exact current preflight result required')
    s=s.replace('print(json.dumps(result))',extra+'print(json.dumps(result))');compile(s,'<actual current after old owner recovery>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1234-current-retirement-peer-preflight-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<fresh current owner-free preflight transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
