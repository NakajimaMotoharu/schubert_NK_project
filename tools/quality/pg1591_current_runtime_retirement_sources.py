"""Current completed seal -> exact canonical-entry retirement in full owned scopes."""
import ast
import inspect
import json
from pathlib import Path
import pg1224_completed_runtime_sources as prior
import pg1223_completed_runtime_contract as old_contract
from pg1579_current_owned_stop_sources import sources as stop_sources,SOURCE,BEFORE as STOP_BEFORE,GUEST_BEFORE
from pg1446_current_cold_stage import W

CLASS='Pg1591NativeStop'
TOOLS='pg1591-current-runtime-retirement-tools-v1'
BASE='/var/lib/pgpt-s1-preservation/pg1579-native-stop-v1/after.private.json'
SHA='6fe760da139eae3115363192c24fdff981bcdc6f7849016c18c7fe60b6c1fca7'
RUNTIME_SHA='2c20987e1457942dc196a1f591b4cd925bac1da2d689421a6782ba4d3eb31f35'

def contract_source():
    raw=inspect.getsource(old_contract)
    raw=raw.replace('343a5a1b-d064-47d5-88c2-31c36d7ba7a4','15700a87-9117-4f63-a0ff-768dd604d0f1')
    raw=raw.replace('d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0',RUNTIME_SHA)
    compile(raw,'<current typed runtime contract>','exec');return raw

def template():
    raw=inspect.getsource(prior.generated)
    node=ast.parse(raw).body[0].body[0]
    marker=ast.get_source_segment(raw,node)
    if not isinstance(node,ast.Assign):raise ValueError('qualified source generation boundary absent')
    raw=raw.replace(marker,"values={n.replace('1579','1591'):s.replace('Pg1579','Pg1591').replace('PG1579','PG1591').replace('pg1579','pg1591')for n,s in stop_sources().items()}")
    raw=raw.replace('1224','1591').replace('pg1223_completed_runtime_contract','pg1591_completed_runtime_contract')
    raw=raw.replace("old='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/full32-stop-owner-handoff-v1/after.private.json'",'old='+repr(GUEST_BEFORE))
    raw=raw.replace('bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a',STOP_BEFORE)
    raw=raw.replace('inspect.getsource(contract)','contract_source()')
    raw=raw.replace("Path(__file__).with_name('pg847_configuration.py')","Path(prior.__file__).with_name('pg847_configuration.py')")
    compile(raw,'<current completed full scope retirement generation>','exec');return raw

def sources():
    post=json.loads((W/'pg1583-current-terminal-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']or post['proofHashes']['after.private.json']['sha256']!=SHA:raise ValueError('current full normal post required')
    env={**prior.__dict__,'prior':prior,'stop_sources':stop_sources,'BASE':BASE,'SHA':SHA,'contract_source':contract_source,'Path':Path}
    action=prior.ACTION.replace('pg1223','pg1591')
    env['ACTION']=action
    exec(compile(template(),'<current full retirement sources>','exec'),env);values=env['generated']()
    h='pg1591_native_owned_stop.py';marker="[b'Pg1591NativeStop',b'stop',b'']"
    if values[h].count(marker)!=1:raise ValueError('one current retirement owner argv binding required')
    values[h]=values[h].replace(marker,"[b'Pg1591NativeStop',b'retire',b'']")
    refs='pg1591_native_refs.py'
    for old,new in [('from pg1591_configuration import FIELDS as CONFIG_FIELDS,same as config_same','from pg1591_configuration import FIELDS as CONFIG_FIELDS'),(";signed_cfg=json.loads(original)['configuration']",''),("require(not changed);directory=pathlib.Path(retirement.ROOT)","require(not changed)")]:
        if values[refs].count(old)!=1:raise ValueError('exact unused retirement declaration boundary absent')
        values[refs]=values[refs].replace(old,new)
    for name,s in values.items():
        values[name]=s.replace('pg1591-current-owned-stop-tools-v1',TOOLS)
        if name.endswith('.py'):compile(values[name],'<actual current retirement '+name+'>','exec')
        if any(v in values[name]for v in ['Pg1224','Pg1232','cbca8738','702983','PG1292','343a5a1b-d064-47d5-88c2-31c36d7ba7a4']):raise ValueError('old authority survived current retirement generation')
    return values
