"""Exact existing zz-pg1980 one-use runtime retirement in current normal-completion full scopes."""
import ast
import inspect
import json
from pathlib import Path
import pg1224_completed_runtime_sources as engine
import pg1223_completed_runtime_contract as contract
from pg2030_fresh_normal_warning_owned_stop_sources import sources as stop_sources,SOURCE
from pg1446_current_cold_stage import W

TOOLS='pg2050-fresh-completed-runtime-retirement-tools-v1'
BASE='/var/lib/pgpt-s1-preservation/pg2030-native-stop-v1/after.private.json'
SHA='c6d5f275a1a756a635655c3c4f6b3da22f4ce5c98b093efabdaab210fa2927ca'


def contract_source():
    raw=inspect.getsource(contract)
    pairs=[('zz-pg1160-once-resume.conf','zz-pg1980-once-resume.conf'),('343a5a1b-d064-47d5-88c2-31c36d7ba7a4','4148e3e8-f107-431a-ab27-d6e6d1f1772e'),('d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0','78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec'),('1,647','1,644'),('os.read(fd,648)','os.read(fd,645)'),('len(data)==647','len(data)==644')]
    for old,new in pairs:
        if old not in raw:raise ValueError('exact current runtime contract field required: '+old)
        raw=raw.replace(old,new)
    compile(raw,'<actual current 644byte runtime retirement contract>','exec');return raw


def sources():
    post=json.loads((W/'pg2040-fresh-normal-warning-terminal-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or post['allClientAdvisoryFlock0']is not True or post['proofHashes']['after.private.json']['sha256']!=SHA:raise ValueError('actual current all stopped before required')
    raw=inspect.getsource(engine.generated)
    assignment=ast.parse(raw).body[0].body[0]
    if not isinstance(assignment,ast.Assign):raise ValueError('one source seed required')
    raw=raw.replace(ast.get_source_segment(raw,assignment),"values={n.replace('2030','2050'):s.replace('Pg2030','Pg2050').replace('pg2030','pg2050').replace('PG2030','PG2050')for n,s in stop_sources().items()}")
    raw=raw.replace('1224','2050').replace('pg1223_completed_runtime_contract','pg2050_completed_runtime_contract')
    old="old='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/full32-stop-owner-handoff-v1/after.private.json'"
    if raw.count(old)!=1:raise ValueError('one exact seed baseline path required')
    raw=raw.replace(old,"old='/var/lib/pgpt-s1-preservation/pg2025-fresh-resume-full-live-seal-v1/before.private.json'").replace('bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a','8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788')
    raw=raw.replace('inspect.getsource(contract)','contract_source()').replace("Path(__file__).with_name('pg847_configuration.py')","Path(engine.__file__).with_name('pg847_configuration.py')")
    ns={**engine.__dict__,'engine':engine,'stop_sources':stop_sources,'BASE':BASE,'SHA':SHA,'contract_source':contract_source,'Path':Path,'ACTION':engine.ACTION.replace('pg1223','pg2050')}
    exec(compile(raw,'<exact current fullscope retirement generator>','exec'),ns);values=ns['generated']()
    helper='pg2050_native_owned_stop.py';marker="[b'Pg2050NativeStop',b'stop',b'']"
    if values[helper].count(marker)!=1:raise ValueError('one actual management argv profile required')
    values[helper]=values[helper].replace(marker,"[b'Pg2050NativeStop',b'retire',b'']")
    name='pg2050_native_refs.py'
    for old,new in [('from pg2050_configuration import FIELDS as CONFIG_FIELDS,same as config_same','from pg2050_configuration import FIELDS as CONFIG_FIELDS'),(";signed_cfg=json.loads(original)['configuration']",''),("require(not changed);directory=pathlib.Path(retirement.ROOT)","require(not changed)")]:
        if values[name].count(old)!=1:raise ValueError('one complete current refs declaration boundary required')
        values[name]=values[name].replace(old,new)
    for name,body in values.items():
        body=body.replace('pg2050-fresh-normal-warning-owned-stop-tools-v1',TOOLS)
        if name.endswith('.py'):
            from pyflakes.api import check
            if check(body,'<actual retirement '+name+'>'):raise ValueError('all runtime source globals required')
            compile(body,'<current fullscope runtime retirement>','exec')
        values[name]=body
    return values
