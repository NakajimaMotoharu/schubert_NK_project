"""Exact current normal old/new immutable stage/place entry, no historical failed-parent fallback."""
import json
import sys
import pg1295_completed_unused_stage_dispatch as base
from pg1865_warning_direct_unused_dispatch import source as previous_source,STAGE as previous_stage
from pg2132_current_normal_unused_sources import sources,TOOLS,BEFORE,CURRENT,bind,production,REMOTE
from pg2133_current_normal_unused_compile import TARGET
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous_stage).replace('pg1865-fixed-stage-v1','pg2134-fixed-stage-v1')

def source():
    raw=bind(previous_source()).replace('pg1865','pg2134').replace('pg1861-frozen-v1','pg2133-frozen-v1')
    compile(raw,'<current normal immutable stage/place body>','exec');return raw

def runtime_namespace(candidate,before):
    if type(candidate)is not dict or type(before)is not dict or type(candidate.get('actualExit'))is not int or candidate['actualExit']!=0 or candidate.get('candidateSource')!=production()or candidate.get('signatureVerified')is not True or candidate.get('candidateNotDeployed')is not True:
        raise ValueError('independently qualified signed unused candidate required')
    normal=before.get('genuineCompletion')
    if type(normal)is not dict or type(before.get('actualExit'))is not int or before['actualExit']!=0 or before.get('productionSource')!=CURRENT or before.get('privateBeforeSha256')!=BEFORE or before.get('allClientAdvisoryFlock0')is not True or before.get('allTenUnitsKernelEmpty')is not True or normal.get('genuinePid1StartDone')is not True or normal.get('normalUnit0or10')is not True or normal.get('currentManagerGc')is not True:
        raise ValueError('actual qualified normal-completed installed current required')
    return {**base.__dict__,'__file__':__file__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'SOURCE':production(),'DIGEST':candidate['manifestSha256'],'BASELINE_SHA':BEFORE,'sources':sources}

def main():
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('immutable stage/place only')
    candidate=json.loads((W/'pg2126-candidate-build-v1.safe.json').read_bytes())
    before=json.loads((W/'pg2130-current-normal-before-v1/manifest.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before)
    exec(compile(source(),'<direct current old/new actual entry>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()

if __name__=='__main__':raise SystemExit(main())
