"""Public C07 start/exit dependency map; never execute a target or replay PT."""
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG6998-c07-map-v1'
PMO = ROOT/'documents/400_PGPT/470_PMO'
SS = 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
UI = 'documents/200_UI/250_運用・非機能/252_ログ・監視・障害復旧設計.md'
RD = 'documents/100_RD/170_運用・保守要件/171_運用・監視要件.md'
PRODUCTION = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
NAMES = (
    'ApiNonSecretConfig.java', 'WebNonSecretConfig.java', 'ApiManagementServer.java',
    'WebManagementServer.java', 'ArtemisQueuePressureClient.java', 'common.yml.template')
TESTS = (
    'ApiNonSecretConfigTest.java', 'WebNonSecretConfigTest.java',
    'ApiManagementServerTest.java', 'WebManagementServerTest.java',
    'ArtemisQueuePressureClientTest.java')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_owner(logical, physical, digest):
    if physical['sha256'] != digest or any(
        logical[k] != physical[k] for k in ('path', 'owner', 'costOwner')):
        raise ValueError('current physical hash and historical owner must agree')
    return logical['owner'], logical['costOwner']


def main():
    # Only versioned, public, regular source/design bytes; no runtime or private paths.
    inventory = json.loads((PMO/'485_WBS網羅性・受入対応.json').read_bytes())
    owned = {a['path']:a for a in inventory['artifacts']}
    physical = {a['path']:a for a in inventory['currentPhysicalCandidate']['artifacts']}
    paths = [ROOT/p for p in subprocess.check_output(
        ['git','ls-files','src'],cwd=ROOT,text=True).splitlines()]
    artifacts, tests = [], []
    for path in paths:
        name = path.name
        if name not in NAMES + TESTS:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError('public regular source required')
        relative = path.relative_to(ROOT).as_posix()
        if name in NAMES:
            original = subprocess.check_output(['git','show',PRODUCTION+':'+relative],cwd=ROOT)
            if hashlib.sha256(original).hexdigest() != sha(path):
                raise ValueError('mapping is for exact original production bytes')
            item = owned[relative]
            owner, cost_owner = verified_owner(item, physical[relative], sha(path))
            artifacts.append(dict(path=relative,sha256=sha(path),owner=owner,
                                  costOwner=cost_owner,newCostAllocation=0))
        else:
            lines = path.read_text().splitlines()
            ids = [line.strip() for line in lines if 'PT-OPS-' in line or 'PT-WEB-' in line]
            methods = [line.strip() for line in lines if 'void ' in line and '(' in line]
            tests.append(dict(path=relative,sha256=sha(path),declaredTestIdLines=ids,
                              methodDeclarations=methods,executedByThisMap=False))
    if len(artifacts) != 6 or len(tests) != 5:
        raise ValueError('exact six source references/five existing test references required')
    tracked = [p.relative_to(ROOT).as_posix() for p in paths]
    deployment_monitoring = [p for p in tracked if p.startswith('src/deployment/') and
                             any(v in p.lower() for v in ('monitor','prometheus','grafana','alert'))]
    rows = [
      dict(section='2-5',requirements='MON-002/003/004',existing='REQUEST/ACTION logging has separate P018-09 implementation; not audited wholesale here',gap='C07 deployment/rotation configuration and full catalogue linkage not proven',next='Keep logging business code ownership P018-09; do not recharge as C07'),
      dict(section='6',requirements='MON-005/006/009/013',existing='Management ready gauges plus batch Queue-pressure projection only; not SS351 whole metric catalogue',gap='Per-metric exporter/instrumentation/label and cardinality TestID mapping incomplete',next='Independent pure catalogue/label contract implementation may start under P018-09; actual exporter/runtime remains held'),
      dict(section='7',requirements='MON-005/006/008/009',existing='ArtemisQueuePressureClient has finite count/byte policy, existing PT-OPS-MQ-019..021',gap='Other threshold timing, dedup/recovery and deployment alert rules not mapped',next='Pure alert policy and fixed-clock tests permitted; live target operations not permitted'),
      dict(section='8',requirements='MON-010/011/012/013',existing='Common mode knob is C06; Web/API parsers validate the enum; management endpoint ready gauge is SS342-specific',gap='Pure mode-to-detailed-service consistency/retention contract and tests absent from bounded references',next='Implement pure MonitoringModePolicy with exhaustive independent mode/service-state PT under P018-09; do not change existing management/native entry'),
      dict(section='9',requirements='MON-007/013',existing='Retention requirements approved in SS351/UI252',gap='C07 monitoring15d/5GB/config artifacts not registered',next='Record exact policy settings; real storage retention requires later configuration/runtime evidence'),
      dict(section='10',requirements='MON-001..013',existing='Existing configuration and Queue tests are shared references, not whole-C07 acceptance',gap='Mode switch/cardinality/all-alert/end-to-end TestID and execution coverage incomplete',next='Normal pure PT permitted; actual mode/service switch and integration remain HOLD')]
    value = dict(schemaVersion=1,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionSource=PRODUCTION,
      artifacts=artifacts,existingTests=tests,requirementMapping=rows,
      designFiles=[dict(path=p,sha256=sha(ROOT/p)) for p in (RD,UI,SS)],
      boundedDeploymentMonitoringNameMatches=deployment_monitoring,
      boundedSearchIsNotProofOfWholeImplementationAbsence=True,
      startPermitted='public source and pure host fixture code/PT, no external target/resource acquisition',
      exitUnmet=['full catalogue/alert/deployment coverage','actual mode consistency and required451/trace','all individual C07 criteria'],
      nextOwner='WBS-P018-09',nextStage='pure MonitoringModePolicy and independent ordinary PT',
      c07Accepted=False,newOriginal190Accepted=0,formalUpdated=False,effortPercent=None,
      executedTests=0,actualVmActions=0,actualDatabaseActions=0,original4222Repeated=False,
      command='python3 -B tools/quality/pg6998_c07_requirement_map.py',toolSha256=sha(Path(__file__)))
    os.umask(0o077)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0,artifacts=len(artifacts),testReferences=len(tests),
                         requirementGroups=len(rows),accepted=0,manifestSha256=sha(OUT/'manifest.json'))))


if __name__ == '__main__':
    main()
