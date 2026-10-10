"""Independent candidate RO receipt and whole old current/state post, readonly."""
import ast
import json
from pg1082_cold_unused_candidate_post import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W


def payload():
    actual=json.loads((W/'pg1086-prepare-ro-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or not actual['fullCandidateRoVerified']:raise ValueError('normal actual RO verification required')
    raw=previous().replace('PG1082-cold-unused-candidate-post-v1','PG1087-cold-candidate-ro-post-v1')
    marker=' for name in reversed(refs):manager.UnrefUnit(name)'
    if raw.count(marker)!=1:raise ValueError('fixed independent RO post scope refused')
    addition=r'''
 ro_receipt=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1084-cold-candidate-ro-v1/complete.private').read_bytes()
 assert ro_receipt==b'allScopesReturnedNormally=true\ncandidateImmutableVerified=true\nepochDbBusinessWrites=0\n'
 ro_flags=subprocess.check_output(['findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG1068','--noheadings','--output','VFS-OPTIONS'],text=True).strip().split(',')
 assert 'ro'in ro_flags and 'rw'not in ro_flags
'''
    raw=raw.replace(marker,addition+marker)
    raw=raw.replace("'unusedCandidateFullPostVerified':True,","'unusedCandidateFullPostVerified':True,'candidateImmutableIndependentPost':True,")
    ast.parse(raw);return raw


if __name__=='__main__':dispatch('PG1087-cold-candidate-ro-post-v1','pg1087-cold-candidate-ro-post-v1',payload())
