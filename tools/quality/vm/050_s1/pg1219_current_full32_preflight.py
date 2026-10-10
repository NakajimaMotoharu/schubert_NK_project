"""Fresh full32 current equality before stop; all old20/state fields retained."""
import ast
import inspect
import pg1200_current_stop_preflight as previous
import pg1213_configuration_scope_bridge as bridge
import pg1120_current_failed_capture as transport
from pg1198_current_stop_binding import generate
from pg1198_current_stop_binding_test import fixture


def payload():
    s=previous.payload().replace("completed-stop-preflight-v1'","completed-full32-stop-preflight-v1'")
    s=s.replace("completed-current-before-v1/before.private.json').read_bytes()", "full32-stop-owner-handoff-v1/after.private.json').read_bytes()")
    s=s.replace("hashlib.sha256(sealed_raw).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa'", "hashlib.sha256(sealed_raw).hexdigest()=='bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a'")
    node=next(n for n in reversed(ast.parse(s).body)if isinstance(n,ast.Try));i=sum(len(x)for x in s.splitlines(keepends=True)[:node.lineno-1])
    cfg=generate(fixture())['pg1198_configuration_capture.py']
    b=inspect.getsource(bridge).replace('from pg847_configuration import FIELDS as FULL','FULL='+repr(bridge.FULL))
    wrapper='\nbridge=types.ModuleType("exact_scope_bridge");exec('+repr(b)+',bridge.__dict__)\nconfig=types.ModuleType("full_configuration");exec('+repr(cfg)+',config.__dict__)\n'+WRAPPER
    s=s[:i]+wrapper+s[i:];ast.parse(s);return s


WRAPPER=r'''
capture20=capture
def capture():
 v=capture20();configs={};scope={}
 for u in CAPTURE_UNITS:
  value=config.complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(bridge.FULL))]).decode(),u)
  configs[u],scope[u]=bridge.extend(v['configuration'][u],value,v['units'][u])
 v['historicalConfiguration']=v['configuration'];v['configuration']=configs;v['configurationScope']=scope;return v
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1219-current-full32-preflight-v1').replace('PG1120-current-failed-capture-v1','PG1219-current-full32-preflight-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<actual current full32 preflight>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
