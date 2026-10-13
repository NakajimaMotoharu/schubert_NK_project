"""Independent exact runtime/config delta plus all closed resources and immutable original/native data."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2040_fresh_normal_warning_terminal_post import payload as previous,SEAL,SEALS
from pg2050_fresh_completed_runtime_retirement_sources import contract_source,SOURCE,TOOLS,SHA
from pg847_configuration import FIELDS
from pg1223_completed_runtime_contract_test import parse

SLOT='pg2060-fresh-runtime-retirement-independent-post-v1'


def payload(seals):
    raw=previous(seals).replace('pg2030-native-stop-v1','pg2050-native-stop-v1').replace('pg2030-fresh-normal-warning-owned-stop-tools-v1',TOOLS).replace('pg2040-fresh-normal-warning-terminal-post-v1',SLOT).replace('PG2040-fresh-normal-warning-terminal-post-v1','PG2060-fresh-runtime-retirement-independent-post-v1')
    raw=raw.replace('allEightOwnedTerminal=true\\n','allTenAlreadyTerminal=true\\n').replace('starts0=true\\noldUnknownNormalized=false','starts0=true\\nruntimeRetiredOnly=true\\noldUnknownNormalized=false')
    marker="require(all((after[k] == before[k] for k in before if k not in ('units', 'configuration'))))"
    if raw.count(marker)!=1:raise ValueError('one exact finite delta boundary required')
    raw=raw.replace(marker,'# Exact finite delta validation follows the complete declaration parser below.')
    contract=contract_source().replace('from pg847_configuration import FIELDS','FIELDS='+repr(FIELDS))
    check=inspect.getsource(parse).replace('def parse(s):','def exec_record(s):')+"\nruntime_contract={};exec("+repr(contract)+",runtime_contract)\nrequire(runtime_contract['same_except_runtime'](before,after,exec_record))\nprior_raw=(base/'pg2030-native-stop-v1/after.private.json').read_bytes()\nrequire(hashlib.sha256(prior_raw).hexdigest()=='"+SHA+"'and json.loads(prior_raw)==before)\n"
    marker='bus = dbus.SystemBus(private=True)'
    # The top-level observer bus is distinct from complete_configuration's private local bus.
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets))
    actual=ast.get_source_segment(raw,node)
    if actual!=marker:raise ValueError('one normal metadata bus boundary required')
    raw=raw.replace('\n'+marker+'\n','\n'+check+marker+'\n',1)
    raw=raw.replace("'normalCurrentOwnedStopScopesSealed': True","'normalCurrentRetirementScopesSealed': True, 'exactRuntimeEntryRetired': True").replace("'ownedExplicitStops': 4", "'ownedExplicitStops': 0")
    from pyflakes.api import check as static_check
    if static_check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<actual whole independent finite runtime post>'):raise ValueError('all retirement post globals required')
    compile(raw,'<exact runtime retirement all stopped post>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed independent retirement post required')
    actual=json.loads((W/'pg2056-retire-v1.safe.json').read_bytes());build=json.loads((W/'pg2051-frozen-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or build['actualExit']!=0 or build['productionSource']!=SOURCE:raise ValueError('actual current normal runtime retirement required')
    out=W/SLOT;out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt=(W/TOOLS/'pg2050_parent_receipt.py').read_text()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=SEAL.replace('pg642-native-stop-v1','pg2050-native-stop-v1').encode(),capture_output=True,timeout=20);(out/'seal-stderr.private.log').write_bytes(r.stderr)
        if r.returncode:raise ValueError('complete current retirement seals required')
        seals=json.loads(r.stdout)
        if set(seals)!=set(SEALS):raise ValueError('fixed4 current retirement seals required')
        raw='HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+payload(seals);(out/'payload.private.py').write_text(raw)
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['proofHashes','toolHashes']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
