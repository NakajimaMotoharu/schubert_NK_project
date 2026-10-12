"""Separate WARNING-original whole terminal post; parent failure stays failure."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1776_warning_stop_independent_post import payload as previous_payload
from pg1220_current_full32_terminal_post import SEAL,SEALS
from pg1833_readonly_parent_state_sources import SOURCE,TOOLS
from pg1808_warning_identity_bound_sources import UUID

SLOT='pg1838-warning-terminal-independent-post-v1'


def payload(seals):
    original=previous_payload(seals)
    raw=original.replace('pg1772','pg1833').replace('Pg1772','Pg1833').replace('PG1772','PG1833')
    raw=raw.replace('pg1776-warning-terminal-post-v1',SLOT).replace('PG1776-warning-terminal-post-v1','PG1838-warning-terminal-independent-post-v1')
    old=b'genuineParentDone=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n'
    new=b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n'
    tree=ast.parse(raw);matches=[n for n in ast.walk(tree)if isinstance(n,ast.Constant)and n.value==old]
    if len(matches)!=1:raise ValueError('one exact normal WARNING stop completion seal required')
    class Completion(ast.NodeTransformer):
        def visit_Constant(self,node):return ast.copy_location(ast.Constant(new),node)if node.value==old else node
    tree=Completion().visit(tree);ast.fix_missing_locations(tree);raw=ast.unparse(tree)+'\n'
    if UUID.findall(original)!=UUID.findall(raw):raise ValueError('all actual UUIDs must remain unchanged')
    compile(raw,'<separate currentWARNING terminal post>','exec');return raw


def main():
    stop=json.loads((W/'pg1835-stop-v1.safe.json').read_bytes());build=json.loads((W/'pg1834-frozen-v1.safe.json').read_bytes())
    if stop['actualExit']!=0 or stop['sourceQualified']is not True or build['actualExit']!=0 or build['productionSource']!=SOURCE:raise ValueError('actual fixed source normal stop and ABI required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt=(W/TOOLS/'pg1833_parent_receipt.py').read_text()
    if '4148e3e8-f107-431a-ab27-d6e6d1f1772e'not in receipt:raise ValueError('independent receipt Root identity required')
    with management_gate(P/'current-management-critical.lock'):
        seal_code=SEAL.replace('pg642-native-stop-v1','pg1833-native-stop-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=seal_code.encode(),capture_output=True,timeout=20)
        (out/'seal-stderr.private.log').write_bytes(r.stderr)
        if r.returncode:raise ValueError('actual separate stop seals required')
        seals=json.loads(r.stdout)
        if set(seals)!=set(SEALS):raise ValueError('all complete current seals required')
        raw='HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+payload(seals)
        (out/'payload.private.py').write_text(raw)
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'operatorSource':stop['operatorSource'],'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if r.returncode==0:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps({k:v for k,v in result.items()if k not in ['proofHashes','toolHashes']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
