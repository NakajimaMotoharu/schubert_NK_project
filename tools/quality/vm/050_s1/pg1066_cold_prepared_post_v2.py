"""New-only post observation with full Unit Ref lifetime and exact completion receipt."""
from pg1065_cold_prepared_post import GUEST as previous
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W
import hashlib
import json


def payload():
    frozen=json.loads((W/'pg1063-cold-preparation-frozen-v2.safe.json').read_bytes())
    child=W/'pg1062-cold-tools-v1/pg1062_cold_refs.py'
    if frozen['actualExit']!=0 or hashlib.sha256(child.read_bytes()).hexdigest()!=frozen['fileHashes'][child.name]:
        raise ValueError('frozen prepared source required')
    actual=json.loads((W/'pg1064-prepare-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or not actual['fullColdPreparationAccepted']:
        raise ValueError('normal actual preparation required')
    return 'SOURCE_SHA='+repr(frozen['fileHashes'][child.name])+'\n'+previous.replace('PG1065-cold-prepared-post-v1','PG1066-cold-prepared-post-v2')


if __name__=='__main__':
    dispatch('PG1066-cold-prepared-post-v2','pg1066-cold-prepared-post-v2',payload())
