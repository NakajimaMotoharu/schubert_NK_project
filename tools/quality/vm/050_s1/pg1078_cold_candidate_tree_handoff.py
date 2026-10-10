"""SSC248 fixed pre-Ref11678/11704 retirement; old completion stays unknown."""
import ast
import hashlib
import json
from pathlib import Path
import re
from pg1077_cold_candidate_tree_preflight import payload as previous,CHILD_ARGV
from pg1060_cold_owned_tree_handoff import HANDOFF as old_handoff
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W


def handoff():
    raw=old_handoff
    raw=re.sub(r'\b5463\b','11678',raw);raw=re.sub(r'\b5489\b','11704',raw)
    raw=raw.replace('1373880','2433710').replace('1373951','2433776')
    raw=raw.replace('8067bb56195ab7f05b1427a9d5cf78f5d71e404000acc5f5f3391c5079e5a1d9',CHILD_ARGV)
    raw=raw.replace('pg1037-cold-prepared-v1/tree-preflight-v4','pg1074-cold-candidate-v1/tree-preflight-v1')
    raw=raw.replace("qualified=json.loads(prior_bytes);CHILD_BUS=qualified.pop('childBusUniqueName')","qualified=json.loads(prior_bytes);assert qualified.pop('childNoBus')is True")
    raw=raw.replace("('snapshot','controls','heldWholeMetadata')","('snapshot','controls','heldWholeMetadata','runtime')")
    raw=raw.replace("'controls':env['controls'](),'heldWholeMetadata'","'controls':env['controls'](),'runtime':env['runtime_namespaces'](),'heldWholeMetadata'")
    lines=raw.splitlines()
    raw='\n'.join(l for l in lines if 'GetConnectionUnixProcessID(CHILD_BUS)'not in l and 'NameHasOwner(CHILD_BUS)'not in l)+'\n'
    # A pre-Ref child has only the two protocol pipes and captured stderr file.
    raw=raw.replace('CHILD_ALREADY_GONE=True','CHILD_ALREADY_GONE=True')
    # Removing the old same-line NameHasOwner assertion also removed this flag.
    raw=raw.replace("  if not pathlib.Path('/proc/11704').exists():\n", "  if not pathlib.Path('/proc/11704').exists():\n   CHILD_ALREADY_GONE=True\n")
    raw=raw.replace(" phase='AFTER_FIXED_TREE_TERM'\n", " phase='AFTER_FIXED_TREE_TERM'\n assert not pathlib.Path('/proc/11704').exists()\n")
    if 'CHILD_BUS'in raw:raise ValueError('pre-Ref bus must not be invented')
    return raw


def payload():
    m=json.loads((W/'pg1077-cold-candidate-tree-preflight-v1/manifest.safe.json').read_bytes())
    if m['actualExit']!=0 or not m['observed']['observerNormalClose']:raise ValueError('fresh whole preflight required')
    prior=m['observed']['beforePrivateSha256']
    raw=previous().replace('PG1077-cold-candidate-tree-preflight-v1','PG1078-cold-candidate-tree-handoff-v1')
    raw=raw.replace("/tree-preflight-v1'", "/tree-preflight-v1/owned-tree-handoff-v1'")
    # SAVE already has the preflight directory; the existing entry assertion must
    # continue to allow exactly that directory and the fixed error log.
    raw=raw.replace('import dbus, time, stat, re','import dbus, time, stat, re, signal, select')
    raw=raw.replace("socket_module = types.ModuleType", "tree_contract=types.ModuleType('tree_contract');exec(TREE_CONTRACT_SOURCE,tree_contract.__dict__)\nsocket_module = types.ModuleType")
    marker='\nheld = []\n'
    if raw.count(marker)!=1:raise ValueError('module held scope refused')
    raw=raw.replace(marker, '\nRESERVATION_ATTEMPTED=False;SIGNAL_ATTEMPTED=False;SIGNAL_COUNT=0;reservation_fd=None;CORE_COUNT=6\nheld = []\n',1)
    raw=raw.replace('allheld = [h.capture() for h in held]','allheld = [h.capture() for h in held[:CORE_COUNT]]')
    start="    phase = 'WHOLE_TWO_READ'";end="    phase = 'OBSERVER_NORMAL_CLOSE'"
    if raw.count(start)!=1 or raw.count(end)!=1:raise ValueError('fixed pre-Ref handoff insertion refused')
    block=handoff();block='\n'.join('   '+l for l in block.splitlines())+'\n'
    raw=raw[:raw.index(start)]+block+raw[raw.index(end):]
    tree=ast.parse(raw)
    tree.body[-1]=ast.parse("print(json.dumps({'run':'PG1078-cold-candidate-tree-handoff-v1','actualExit':0,'source':env['SOURCE'],'boot':env['BOOT'],'oldParentGone':True,'oldChildGone':True,'allOldClientsAdvisoryAndFlocks0':True,'allOriginalsUnchangedTwice':True,'allTenColdFull32':True,'observerNormalClose':True,'oldOperationNormalClose':False,'oldTransportExit':None,'childExitUnknown':True,'childAlreadyGone':CHILD_ALREADY_GONE,'signalsAttempted':SIGNAL_COUNT,'reservationDurable':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'afterPrivateSha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),'formalAccepted':False}))").body[0]
    return 'PRIOR_SHA='+repr(prior)+'\nTREE_CONTRACT_SOURCE='+repr(Path(__file__).with_name('pg1049_cold_tree_contract.py').read_text())+'\n'+ast.unparse(tree)


if __name__=='__main__':dispatch('PG1078-cold-candidate-tree-handoff-v1','pg1078-cold-candidate-tree-handoff-v1',payload())
