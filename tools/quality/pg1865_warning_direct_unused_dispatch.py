"""Actual direct two-source namespace; no obsolete candidate admission delegation."""
import json
import re
import sys
import pg1295_completed_unused_stage_dispatch as base
from pg1862_warning_actual_graph_dispatch import source as previous_source,STAGE as OLD_STAGE,TARGET,GUEST,REMOTE
from pg1860_warning_actual_graph_sources import sources
from pg1844_warning_unit_full_six import CANDIDATE,OLD
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import W,P

STAGE=OLD_STAGE.replace('pg1862-fixed-stage-v1','pg1865-fixed-stage-v1')


def source():return previous_source().replace("'pg1862-'+action+'-v2'","'pg1865-'+action+'-v1'").replace('pg1862-stage-v2.exit','pg1865-stage-v1.exit').replace('pg1862-fixed-stage-v1','pg1865-fixed-stage-v1')


def runtime_namespace(candidate,before):
    if type(candidate)is not dict or type(before)is not dict or type(candidate.get('actualExit'))is not int or candidate['actualExit']!=0 or candidate.get('candidateSource')!=CANDIDATE or candidate.get('signatureVerified')is not True:raise ValueError('actual independently signed new candidate required')
    receipt=before.get('genuineCompletion')
    if type(before.get('actualExit'))is not int or before['actualExit']!=0 or before.get('productionSource')!=OLD or before.get('allClientAdvisoryFlock0')is not True or type(receipt)is not dict or receipt.get('managerFailureRetained')is not True:raise ValueError('actual separately qualified old current required')
    digest=candidate.get('manifestSha256');original=before.get('privateBeforeSha256')
    if any(type(v)is not str or re.fullmatch('[0-9a-f]{64}',v)is None for v in [digest,original]):raise ValueError('exact actual old/new hashes required')
    return {**base.__dict__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'SOURCE':CANDIDATE,'DIGEST':digest,'BASELINE_SHA':original,'sources':lambda bom:sources(bom,original)}


def main():
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('direct immutable stage/place only')
    candidate=json.loads((W/'pg1846-candidate-build-v1.safe.json').read_bytes());before=json.loads((W/'pg1849-warning-completed-current-before-v1/manifest.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before)
    exec(compile(source(),'<actual direct old/new admission and fixed operation>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
