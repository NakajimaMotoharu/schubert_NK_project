"""Selected changed-tool contracts and public hash-only reproducible evidence manifest."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

R=Path(__file__).resolve().parent
ROOT=R.parents[3]
TESTS=('pg1345_current_bootstrap_sources_test','pg1348_current_bootstrap_sources_test','pg1349_current_bootstrap_dispatch_test','pg1351_bootstrap_failed_owner_proof_test','pg1355_bootstrap_fixed_handoff_test','pg1356_current_bootstrap_sources_test','pg1358_current_bootstrap_dispatch_test','pg1360_bootstrap_failed_pair_proof_test','pg1361_bootstrap_fixed_pair_handoff_test','pg1362_current_bootstrap_sources_test','pg1367_bootstrap_failed_ref_pair_proof_test','pg1368_bootstrap_fixed_ref_handoff_test','pg1369_bootstrap_role_policy_test','pg1371_bootstrap_role_host_test','pg1374_bootstrap_role_sources_test','pg1376_bootstrap_role_preflight_test','pg1380_bootstrap_role_sql_test','pg1381_role_failed_ref_pair_proof_test','pg1382_role_fixed_ref_handoff_test','pg1385_role_contract_test','pg1387_role_dispatch_test','pg1388_role_independent_post_test','pg1389_role_prepared_failed_pair_proof_test','pg1390_prepared_role_fixed_pair_handoff_test','pg1391_prepared_role_independent_baseline_test','pg1392_existing_role_sources_test','pg1395_existing_role_normal_post_test','pg1396_existing_admin_sources_test','pg1400_existing_admin_independent_post_test','pg1401_current_bootstrap_ten_native_test','pg1402_current_admin_native_gap_test')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed evidence source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc)
    log=W/'pg1403-selected-tool-contract-v1.private.log'
    suite=unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    with log.open('x')as f:
        result=unittest.TextTestRunner(stream=f,verbosity=1).run(suite);f.flush();os.fsync(f.fileno())
    actual=0 if result.wasSuccessful()and not result.skipped else 1
    refs=['pg1381-role-failed-ref-pair-v1.safe.json','pg1382-role-fixed-ref-handoff-v1.safe.json','pg1383-role-sql-parse-v1.safe.json','pg1385-frozen-v2.safe.json','pg1386-role-fresh-preflight-v1.safe.json','pg1387-prepare-v1.safe.json','pg1389-role-prepared-failed-pair-v1.safe.json','pg1390-prepared-role-fixed-pair-v1.safe.json','pg1391-prepared-role-independent-baseline-v1.safe.json','pg1393-frozen-v2.safe.json','pg1394-prepare-v1.safe.json','pg1395-existing-role-normal-post-v1.safe.json','pg1396-frozen-v3.safe.json','pg1396-verify-v3.safe.json','pg1396-execute-v3.safe.json','pg1400-existing-admin-independent-post-v1.safe.json','pg1401-current-bootstrap-ten-native-v1/manifest.safe.json','pg1402-current-admin-native-gap-v1/gap.safe.json']
    proofs=[]
    for relative in refs:
        p=W/relative;v=json.loads(p.read_bytes())
        proofs.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'actualExit':v['actualExit'],'run':v.get('run'), 'formalAccepted':False})
    native=json.loads((W/'pg1401-current-bootstrap-ten-native-v1/manifest.safe.json').read_bytes())
    record={'run':'PG1344-1403-current-bootstrap-role-admin','recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'productionSource':SOURCE,'operatorSource':head,'branch':'dev-foundation','actualExit':actual,'selectedToolTestCount':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'productionPtCredit':0,'command':'python3 -B tools/quality/vm/050_s1/pg1403_bootstrap_tool_evidence.py','startedUTC':start.isoformat(),'environment':{'OS':'Ubuntu26.04','JDK':'25.0.4','Python':'3.14.4','PostgreSQL':'18.6','JaCoCo':'0.8.15'},'testSourceHashes':{name:sha(R/(name+'.py'))for name in TESTS},'selectedTestLogSha256':sha(log),'evidenceRefs':proofs,'failureIds':['BUG-'+str(x)for x in range(1081,1092)],'horizontalIds':['YKT-'+str(x)for x in range(850,861)],'ssc':'SSC263','approvedDesignMain':'8ac7fdd1e300cb0478e43880d3c54ce5893dca12','currentNativeStreams':10,'newAdminDumps':2,'incrementalVs1341':native['incrementalVsPG1341'],'remaining':native['remaining'],'classByteMismatch':0,'wholeLeafAcceptedDelta':0,'formalAccepted':False,'itStComplete':False,'rawExported':False,'old143Normalized':False,'oracleBasis':['independent UID-GID/mode/NOFOLLOW finite metadata matrix and held-I/O faults','complete SQL literal and backend matrix, real READ ONLY EXPLAIN','exact owner PID/ticks/argv hash/private bus and sealed originals','actual PID1 normal20 and fixed Unit deadline, terminal/closing same session','independent all24/full32/187/credential-retirement/full resource post','independent same-source JAR CRC/JaCoCo XML counters; exclusions0'],'unaccepted':['whole native/451/CHR/fault matrix','QA051 final L01','remaining PG/PT and handoff']}
    destination=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG1344-1403-current-bootstrap-role-admin';destination.mkdir(mode=0o700)
    with(destination/'manifest.json').open('x')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':actual,'selectedToolTests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'manifest':str(destination/'manifest.json'),'sha256':sha(destination/'manifest.json')}));return actual

if __name__=='__main__':raise SystemExit(main())
