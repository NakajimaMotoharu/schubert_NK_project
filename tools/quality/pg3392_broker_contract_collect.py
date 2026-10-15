"""Bind one physical Broker configuration to actual original3372 XML and independent schema/policy."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

import lan_server
from pg3390_broker_config_oracle import self_check

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
PUBLIC = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3392-broker-config-contract'
PRIVATE = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg3390-broker-schema-v1')
CONFIG = 'src/deployment/artemis/etc/broker.xml'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ArtemisBrokerConfigurationTest.java'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077); PUBLIC.mkdir()
    remote = """python3 - <<'REMOTE'
from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib
p=Path('/home/mini/schubert-nk-pgpt/runs/PG3372-six-v1')
x=p/'api/surefire-reports/TEST-dev.codex.schubert.nk.api.messaging.config.ArtemisBrokerConfigurationTest.xml'
r=E.parse(x).getroot();props={a.get('name'):a.get('value') for a in r.findall('./properties/property')}
b=Path(props['broker.template']);v=json.loads((p/'begin.safe.json').read_bytes());f=json.loads((p/'manifest.safe.json').read_bytes())
assert f['actualExit']==f['mavenExit']==0 and f['tests']==3706
jar=Path('/home/mini/schubert-nk-pgpt/m2/repository/org/apache/artemis/artemis-server/2.56.0/artemis-server-2.56.0.jar')
print(json.dumps({'xmlSha256':hashlib.sha256(x.read_bytes()).hexdigest(),'tests':int(r.get('tests')),'failures':int(r.get('failures')),'errors':int(r.get('errors')),'skipped':int(r.get('skipped')),'cases':[{'class':a.get('classname'),'name':a.get('name'),'nonSuccessElements':[e.tag for e in a if e.tag in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']]}for a in r.findall('testcase')],'brokerInputSha256':v['inputs']['src/deployment/artemis/etc/broker.xml'],'brokerActualSha256':hashlib.sha256(b.read_bytes()).hexdigest(),'testSourceSha256':v['inputs']['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/ArtemisBrokerConfigurationTest.java'],'artemisServerJarSha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'javaVersion':props['java.version'],'os':props['os.name']+' '+props['os.version'],'wholeManifestSha256':hashlib.sha256((p/'manifest.safe.json').read_bytes()).hexdigest()}))
REMOTE"""
    rc, raw = lan_server.run(remote, timeout=30); assert rc == 0
    original = json.loads(raw.strip())
    assert original['tests'] == len(original['cases']) == 4
    assert original['failures'] == original['errors'] == original['skipped'] == 0
    assert all(not c['nonSuccessElements'] for c in original['cases'])
    assert original['brokerInputSha256'] == original['brokerActualSha256'] == digest(ROOT / CONFIG)
    assert original['testSourceSha256'] == digest(ROOT / TEST)
    assert hashlib.sha256(subprocess.check_output(['git', 'show', SOURCE + ':' + CONFIG], cwd=ROOT)).hexdigest() == digest(ROOT / CONFIG)
    jar = Path('/home/mini/codex/project1/work/toolchain/m2/repository/org/apache/artemis/artemis-server/2.56.0/artemis-server-2.56.0.jar')
    assert digest(jar) == original['artemisServerJarSha256']
    with zipfile.ZipFile(jar) as z:
        for name in ['artemis-configuration.xsd', 'xml.xsd']:
            assert hashlib.sha256(z.read('schema/' + name)).hexdigest() == digest(PRIVATE / name)
    expected = ('REJECTED unknown-element\nREJECTED journal-type\nREJECTED max-disk-usage\nREJECTED persistence-enabled\n'
                'PASS original-before-and-after; independent-negative4; broker-start0\n')
    assert (PRIVATE / 'run.private.log').read_text() == expected
    assert (PRIVATE / 'compile.private.log').read_bytes() == b''
    schemas = {n: digest(PRIVATE / n) for n in ['artemis-configuration.xsd', 'xml.xsd']}
    docs = ['documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md',
            'documents/100_RD/130_インターフェース要件/131_MQインターフェース要件.md']
    for path in docs:
        assert subprocess.check_output(['git', 'show', 'origin/main:' + path], cwd=ROOT) == (ROOT / path).read_bytes()
    value = {'actualExit': 0, 'run': 'PG3392-broker-config-contract', 'productionSource': SOURCE,
             'ownedArtifact': CONFIG, 'artifactSha256': digest(ROOT / CONFIG), 'wholeActualOriginal': original,
             'schemaCanary': {'compileExit': 0, 'actualExit': 0, 'originalAcceptedBeforeAndAfter': True,
                             'independentInvalidFourRejected': True, 'officialSchemaSha256': schemas,
                             'sourceSha256': digest(ROOT / 'tools/quality/vm/050_s1/ArtemisConfigurationSchemaCanary.java'),
                             'runLogSha256': digest(PRIVATE / 'run.private.log')},
             'independentPolicy': self_check(ROOT / CONFIG),
             'documentSha256': {p: digest(ROOT / p) for p in docs},
             'requirementIds': ['MQ-011', 'MQ-012', 'MQ-013'],
             'coverageApplicability': 'NON_JAVA_CONFIGURATION_ARTIFACT; Java counters not excluded or changed',
             'C04Accepted': False, 'formalUpdated': False, 'effortCompletionRate': None,
             'runtimeBrokerStarted': False, 'vmActions': 0, 'newProductionPtCredit': 0,
             'scopeBoundary': 'Physical Broker template only. MQ011 application BytesMessage guards, client connection credentials/timeouts, console/Unit and runtime readiness remain separate owners; not whole MQ requirement acceptance.',
             'remaining': ['Explicit C04 individual review/strict audit and requirement-scope ownership joins not yet complete']}
    with (PUBLIC / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    print(json.dumps({'actualExit': 0, 'manifestSha256': digest(PUBLIC / 'manifest.json'),
                      'existingCasesReferenced': 4, 'newJUnitCredit': 0, 'schemaNegative': 4, 'policyNegative': 3}))


if __name__ == '__main__':
    main()
