"""Current-source original LegacyReceipt1 and StopPolicy7, fake Process only; no external command."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS={
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle",
    "sha256": "d2686fed8d6c620411de1b92ed4a7bf19507e9f37f18d65b753208b3631de68a"
  },
  "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy",
    "sha256": "b4b7fc677bbe515cd048ba73e673afdd9a24fc0174d97694ed1035c74a9de0ef"
  },
  "dev/codex/schubert/nk/batch/platform/MaintenanceUnit": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/MaintenanceUnit",
    "sha256": "e764ee58aacff2e95fbc30f9102fe40295a25ac0b41df0aaa3ef03a625e34733"
  },
  "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe",
    "sha256": "cfd6a67fba5f487f3e3f5195ca9a308c1c9ad447a295fe22b8ed230ae8cac9a0"
  },
  "dev/codex/schubert/nk/batch/platform/ProcessResourceScope": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/ProcessResourceScope",
    "sha256": "6ea511aa08b6182d29cc67da0b7d6ea77112a612ff31c57bee36306042bf2313"
  },
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource": {
    "module": "batch",
    "name": "dev/codex/schubert/nk/batch/platform/SystemctlStateSource",
    "sha256": "a1cec7d9ec384cf8f4a69c50b7f295433f528446567de2d66504cfd710bf5e23"
  }
}
CLOSURES={
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle": [
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$1",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$2",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$3",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$BackupCompletion",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$BackupResult",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Completion",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Gate",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Handoff",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ObservedCompletion",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ObservedWork",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Outcome",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ParentProof",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Receipt",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Retain",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Start",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$StartAttempt",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Started",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Stop",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$StopAttempt",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Terminal",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Unresolved",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Wait",
    "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle"
  ],
  "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy": [
    "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy$NativeSource",
    "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy$Source",
    "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy"
  ],
  "dev/codex/schubert/nk/batch/platform/MaintenanceUnit": [
    "dev/codex/schubert/nk/batch/platform/MaintenanceUnit"
  ],
  "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe": [
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader$Start",
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader",
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$QueryProcess",
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$Reader",
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$SafeStream",
    "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe"
  ],
  "dev/codex/schubert/nk/batch/platform/ProcessResourceScope": [
    "dev/codex/schubert/nk/batch/platform/ProcessResourceScope$OwnedQuery",
    "dev/codex/schubert/nk/batch/platform/ProcessResourceScope$QueryWork",
    "dev/codex/schubert/nk/batch/platform/ProcessResourceScope"
  ],
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource": [
    "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess",
    "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$Start",
    "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$StdIo",
    "dev/codex/schubert/nk/batch/platform/SystemctlStateSource"
  ]
}
METADATA=set([
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$BackupCompletion",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$BackupResult",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Completion",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Gate",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Handoff",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ObservedCompletion",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ObservedWork",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$ParentProof",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Retain",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Start",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$StartAttempt",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Stop",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$StopAttempt",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Terminal",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Wait",
  "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy$Source",
  "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader$Start",
  "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$Reader",
  "dev/codex/schubert/nk/batch/platform/ProcessResourceScope$OwnedQuery",
  "dev/codex/schubert/nk/batch/platform/ProcessResourceScope$QueryWork",
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$Start"
])
UNEXECUTED=set([
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$1",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$2",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$3",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Started",
  "dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Unresolved",
  "dev/codex/schubert/nk/batch/platform/InspectorUnitProbe",
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource",
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$StdIo",
  "dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess"
])
ROOT=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform'
TESTS={name:ROOT/(name+'.java') for name in ['LegacyReceiptValueTest','MaintenanceUnitStopPolicyTest']}
COUNTS={'LegacyReceiptValueTest':1,'MaintenanceUnitStopPolicyTest':7}
COMPILE_ONLY={'InspectorUnitProbeFixture':ROOT/'InspectorUnitProbeFixture.java','InspectorUnitSnapshotTest':ROOT/'InspectorUnitSnapshotTest.java'}
TEST_PINS={
  "LegacyReceiptValueTest": "7be453b987c5e50dca3d2697115087dbb52b85b1f4d761239dcba38428da09f8",
  "MaintenanceUnitStopPolicyTest": "b9804b33eb028770bac620fabe176883ad8a627aa92fdc0f2282264ae43114f4",
  "InspectorUnitProbeFixture": "75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b",
  "InspectorUnitSnapshotTest": "edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63"
}
FIXTURES={}
SESSION='PG16398-LEGACY-POLICY-ORIGINAL-EIGHT'
REPORTER=data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16398-legacy-policy-original-eight-pt-v1';run.OUT=data.BASE/'PG16398-legacy-policy-original-eight-pt-v1'
    run.HELPER=data.ROOT/'tools/quality/architecture/LegacyPolicyEightJunitLauncher.java'
    run.NEW_TEST=TESTS['LegacyReceiptValueTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.FIXTURES,run.COUNTS=FIXTURES,COUNTS;run.EXTRA_TEST_SOURCES=(REPORTER,*COMPILE_ONLY.values());run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16334-current2174-observation-registry-v1/manifest.json','4692639392b626eaecd51bf435d54399ada80d7ba95b680e839b378484806215')
    assert normal['source']==previous['source']==SOURCE
    for name,path in {**TESTS,**COMPILE_ONLY}.items():
        relative=str(path.relative_to(data.ROOT))
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==TEST_PINS[name]
    for name,path in TESTS.items():
        text=path.read_text()
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in previous['suiteNames']
        assert not any(v in text for v in ['@Before','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','java.sql','LinuxDirectoryCalls','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    legacy=TESTS['LegacyReceiptValueTest'].read_text()
    assert re.search(r'MorningBackupUnitCycle\.(?!(?:Receipt|Outcome)\b)',legacy) is None
    policy=TESTS['MaintenanceUnitStopPolicyTest'].read_text()
    assert policy.count('MaintenanceUnitStopPolicy.create()')==1 and 'new InspectorUnitProbe.NativeReader(' in policy and 'return child;' in policy
    assert len(MAIN_UNITS)==len(CLOSURES)==6 and sum(map(len,CLOSURES.values()))==40 and len(METADATA)==21 and len(UNEXECUTED)==10
    assert not METADATA&UNEXECUTED
    for name,row in MAIN_UNITS.items():
        path=source_path(row)
        assert normal['begin']['inputHashes'][path]==run.host.sha(data.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==row['sha256']
        assert name not in previous['fullSourceUnits']
        with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
            assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    run.step=environmental_step;run.main()
