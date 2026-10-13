"""Separate exact normal-WARNING stop marker and full stopped current resources/rows/native post."""
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1838_warning_terminal_independent_post import payload as previous
from pg1220_current_full32_terminal_post import SEAL,SEALS
from pg2030_fresh_normal_warning_owned_stop_sources import context,old_context,SOURCE,BOM,TOOLS

SLOT='pg2040-fresh-normal-warning-terminal-post-v1'


def payload(seals):
    before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=old_context()
    raw=previous(seals)
    pairs=[('pg1833','pg2030'),('Pg1833','Pg2030'),('PG1833','PG2030'),('pg2030-warning-owned-stop-tools-v1',TOOLS),(old_before,before),(old_utc,utc),('pg1770-next-day-full-warning-seal-v1','pg2025-fresh-resume-full-live-seal-v1'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',SOURCE),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',BOM),('PG1638','PG1846'),('pg1638','pg1846'),('b5a12ee25dc44ec49b08f5d084b4052f','1eb0d77ce4704e7481ecc07beddcdf0c'),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','e31b627c-c0e2-4120-bd64-c0777479e800'),('pg1838-warning-terminal-independent-post-v1',SLOT),('PG1838-warning-terminal-independent-post-v1','PG2040-fresh-normal-warning-terminal-post-v1')]
    numbers={'81404764713':'106318294326','83204764713':'108118294326','127250':'187092','389748':'503613',str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,identity in old_owned.items():pairs.append((identity[1],owned[unit][1]));numbers[identity[0]]=owned[unit][0]
    for old,new in pairs:raw=raw.replace(old,new)
    for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
    old=b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n'
    new=b'genuineParentDone=true\nnormalUnit0or10=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n'
    tree=ast.parse(raw);found=[n for n in ast.walk(tree)if isinstance(n,ast.Constant)and n.value==old]
    if len(found)!=1:raise ValueError('one exact independent normal source completion marker required')
    class Completion(ast.NodeTransformer):
        def visit_Constant(self,node):return ast.copy_location(ast.Constant(new),node)if node.value==old else node
    tree=Completion().visit(tree);ast.fix_missing_locations(tree);raw=ast.unparse(tree)+'\n'
    old="exec(compile(ast.Module(body=constants + nodes, type_ignores=[]), '<sealed terminal metadata>', 'exec'), globals())"
    new="""metadata_scope={'os':os,'pathlib':pathlib,'stat':stat,'subprocess':subprocess,'json':json,'hashlib':hashlib,'re':re,'sys':sys,'time':time,'require':require}
exec(compile(ast.Module(body=constants + nodes, type_ignores=[]), '<sealed terminal metadata>', 'exec'), metadata_scope)
command,metadata,strict,show,tree,configuration_fields,kernel=(metadata_scope[n]for n in ['command','metadata','strict','show','tree','configuration_fields','kernel'])
UNITS,FIELDS=metadata_scope['UNITS'],metadata_scope['FIELDS']"""
    if raw.count(old)!=1:raise ValueError('one explicit measured metadata namespace required')
    raw=raw.replace(old,new)
    raw=raw.replace("'normalCurrentOwnedStopScopesSealed': True","'normalCurrentOwnedStopScopesSealed': True, 'currentNormalWarningParentProof': True")
    from pyflakes.api import check
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<actual independent current normal terminal post>'):raise ValueError('all post globals required')
    compile(raw,'<exact new current stopped full post>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed terminal post source required')
    stop=json.loads((W/'pg2038-stop-v1.safe.json').read_bytes());build=json.loads((W/'pg2031-frozen-v1.safe.json').read_bytes())
    if stop['actualExit']!=0 or stop['sourceQualified']is not True or build['actualExit']!=0 or build['productionSource']!=SOURCE:raise ValueError('actual current normal stop and frozen ABI required')
    out=W/SLOT;out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt=(W/TOOLS/'pg2030_parent_receipt.py').read_text()
    with management_gate(P/'current-management-critical.lock'):
        seal=SEAL.replace('pg642-native-stop-v1','pg2030-native-stop-v1')
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=seal.encode(),capture_output=True,timeout=20);(out/'seal-stderr.private.log').write_bytes(r.stderr)
        if r.returncode:raise ValueError('actual current stop seals required')
        seals=json.loads(r.stdout)
        if set(seals)!=set(SEALS):raise ValueError('complete stop seal set required')
        raw='HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+payload(seals);(out/'payload.private.py').write_text(raw)
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'stopOperatorSource':stop['operatorSource'],'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['toolHashes','proofHashes']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
