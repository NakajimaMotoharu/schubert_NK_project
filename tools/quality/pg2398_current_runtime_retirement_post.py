"""Independent finite runtime/config delta plus all original/native/resources after normal retire."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg2380_current_resume_owned_post as previous
from pg2392_current_completed_runtime_retirement_sources import contract_source,SOURCE,TOOLS,SHA,BASE
from pg847_configuration import FIELDS
from pg1223_completed_runtime_contract_test import parse
import pg2062_native_augmented_retirement_post as dialect
import pg1257_fresh_independent_terminal_post as schema

SLOT='pg2398-current-runtime-retirement-post-v1'


def payload(seals):
    raw=previous.payload(seals).replace(previous.TOOLS,TOOLS).replace('pg2374','pg2392').replace('Pg2374','Pg2392').replace(previous.SLOT,SLOT).replace('PG2380-current-resume-owned-post-v1','PG2398-current-runtime-retirement-post-v1')
    raw=raw.replace('allEightOwnedTerminal=true\\n','allTenAlreadyTerminal=true\\n').replace('starts0=true\\noldUnknownNormalized=false','starts0=true\\nruntimeRetiredOnly=true\\noldUnknownNormalized=false')
    marker="require(all((after[k] == before[k] for k in before if k not in ('units', 'configuration'))))"
    if raw.count(marker)!=1:raise ValueError('one finite-delta observer boundary required')
    raw=raw.replace(marker,'# Exact finite runtime/declaration delta checked below.')
    contract=contract_source().replace('from pg847_configuration import FIELDS','FIELDS='+repr(FIELDS))
    guard=inspect.getsource(parse).replace('def parse(s):','def exec_record(s):')+'\n'+inspect.getsource(dialect.prior_equal)+"\nruntime_contract={};exec("+repr(contract)+",runtime_contract)\nrequire(runtime_contract['same_except_runtime'](before,after,exec_record))\nprior_raw=pathlib.Path("+repr(BASE)+").read_bytes()\nrequire(hashlib.sha256(prior_raw).hexdigest()=="+repr(SHA)+" and prior_equal(json.loads(prior_raw),before,after))\n"
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets));marker=ast.get_source_segment(raw,node)
    if marker!='bus = dbus.SystemBus(private=True)':raise ValueError('exact independent bus boundary required')
    raw=raw.replace('\n'+marker+'\n','\n'+guard+marker+'\n',1)
    raw=raw.replace("'normalCurrentOwnedStopScopesSealed': True","'normalCurrentRetirementScopesSealed': True, 'exactRuntimeEntryRetired': True").replace("'ownedExplicitStops': 4","'ownedExplicitStops': 0")
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<current finite independent retirement post>'):raise ValueError('all current post globals required')
    compile(raw,'<current retirement full resource post>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current post source required')
    actual=json.loads((W/'pg2394-retire-v1.safe.json').read_bytes());build=json.loads((W/'pg2393-frozen-v1.safe.json').read_bytes())
    if not(actual['actualExit']==0 and actual['sourceQualified'] and build['actualExit']==0 and build['productionSource']==SOURCE):raise ValueError('actual normal current retirement and full ABI required')
    out=W/SLOT;out.mkdir(mode=0o700);receipt=(W/TOOLS/'pg2392_parent_receipt.py').read_text();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        seal=schema.previous.SEAL.replace('pg642-native-stop-v1','pg2392-native-stop-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=seal.encode(),capture_output=True,timeout=20);(out/'seal-stderr.private.log').write_bytes(r.stderr)
        if r.returncode:raise ValueError('actual complete four retirement seals required')
        seals=json.loads(r.stdout)
        if set(seals)!=set(schema.previous.SEALS):raise ValueError('fixed four retirement seals required')
        raw='HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+payload(seals);(out/'payload.private.py').write_text(raw)
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);v={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:v.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps({k:x for k,x in v.items()if k not in ['proofHashes','toolHashes']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
