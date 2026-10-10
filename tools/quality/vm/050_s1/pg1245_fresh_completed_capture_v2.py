"""BUG1066: fixed full32 typed empty-property capture; new-only slot."""
import hashlib
import inspect
import json
from pathlib import Path
import pg1222_completed_retirement_preflight as transport
from pg1244_fresh_completed_capture import payload as previous

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')

def configuration_source():
    build=json.loads((W/'pg1217-frozen-v1.safe.json').read_bytes())
    name='pg1216_configuration_capture.py'
    raw=(W/'pg1216-native-tools-v1'/name).read_bytes()
    if build['actualExit']!=0 or hashlib.sha256(raw).hexdigest()!=build['fileHashes'][name]:
        raise ValueError('qualified full32 actual configuration source required')
    compile(raw,'<qualified actual full32 configuration capture>','exec')
    return raw.decode()

def payload():
    s=previous().replace('fresh-completed-capture-v1','fresh-completed-capture-v2')
    old='configuration={u:show(u,cfg.FIELDS)for u in units}'
    if s.count(old)!=1:
        raise ValueError('fixed full32 actual capture insertion required')
    s='CONFIG_CAPTURE='+repr(configuration_source())+'\n'+s
    s=s.replace("cfg=types.ModuleType('independent_configuration');exec(CONFIG_ORACLE,cfg.__dict__)","cfg=types.ModuleType('independent_configuration');exec(CONFIG_ORACLE,cfg.__dict__)\nconfig_capture=types.ModuleType('qualified_full32');exec(CONFIG_CAPTURE,config_capture.__dict__)")
    s=s.replace(old,"configuration={u:config_capture.complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(cfg.FIELDS))]).decode(),u)for u in units}")
    compile(s,'<full new-day typed-empty capture>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1245-fresh-completed-capture-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only corrected full32 capture>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
