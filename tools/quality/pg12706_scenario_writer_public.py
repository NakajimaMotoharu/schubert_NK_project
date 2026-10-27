"""Public changed-path scan; held names are excluded before any file content access."""
import hashlib
import json
import subprocess
from pg9898_g07_enum_public_delta import ROOT, RULES, HELD

OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12706-scenario-writer-public-v1'
BEFORE = 'a41f9a9b1'
PREFIXES = ('tools/quality/pg127','tools/quality/architecture/ScenarioWriterJunitLauncher.java','tools/quality/architecture/ScenarioWriterArtifactCoverageMeasure.java','tools/quality/architecture/ScenarioWriterArtifactCoverageMeasureV2.java','tools/quality/architecture/TransferVerifierJunitLauncher.java','tools/quality/architecture/TransferVerifierArtifactCoverageMeasure.java','tools/quality/architecture/RunSessionJunitLauncher.java','tools/quality/architecture/RunSessionArtifactCoverageMeasure.java','tools/quality/architecture/MemoryBoundaryJunitLauncher.java','tools/quality/architecture/MemoryBoundaryArtifactCoverageMeasure.java','tools/quality/pg126','tools/quality/architecture/PublicClaimJunitLauncher.java','tools/quality/architecture/PublicClaimArtifactCoverageMeasure.java','tools/quality/architecture/PublicUnitTextJunitLauncher.java','tools/quality/architecture/MonitoringMainJunitLauncher.java','tools/quality/architecture/MonitoringMainArtifactCoverageMeasure.java','tools/quality/architecture/PublicRecordJunitLauncher.java','tools/quality/architecture/PublicRecordArtifactCoverageMeasure.java','tools/quality/pg125','tools/quality/architecture/PureResourceProfileJunitLauncher.java','tools/quality/architecture/PureResourceProfileArtifactCoverageMeasure.java','tools/quality/architecture/EnumCatalogFixtureJunitLauncher.java','tools/quality/architecture/EnumCatalogArtifactCoverageMeasure.java','tools/quality/architecture/ConfigTemplateJunitLauncher.java','tools/quality/architecture/ConfigTemplateArtifactCoverageMeasure.java','tools/quality/f03_saved_history_12424.py','tools/quality/architecture/BatchRuntimeOracleJunitLauncher.java','tools/quality/architecture/BatchRuntimeOracleArtifactCoverageMeasure.java','tools/quality/pg124','tools/quality/architecture/PoolBatchFixtureJunitLauncher.java','tools/quality/architecture/PoolBatchFixtureArtifactCoverageMeasure.java','tools/quality/architecture/PoolCapacityFixtureJunitLauncher.java','tools/quality/architecture/PoolCapacityFixtureArtifactCoverageMeasure.java','tools/quality/architecture/ReadinessDependencyFixtureJunitLauncher.java','tools/quality/architecture/ReadinessDependencyFixtureArtifactCoverageMeasure.java','tools/quality/pg123','tools/quality/architecture/ApiValueFixtureJunitLauncher.java','tools/quality/architecture/ApiValueFixtureArtifactCoverageMeasure.java','tools/quality/architecture/CheckHealthFixtureJunitLauncher.java','tools/quality/architecture/CheckHealthFixtureArtifactCoverageMeasure.java','tools/quality/pg122','tools/quality/architecture/AuditMetricFixtureJunitLauncher.java','tools/quality/architecture/AuditMetricFixtureArtifactCoverageMeasure.java','tools/quality/architecture/LocalAuditFixtureJunitLauncher.java','tools/quality/architecture/LocalAuditFixtureArtifactCoverageMeasure.java','tools/quality/frozen_selected_scope.py','tools/quality/architecture/BatchValueFixtureJunitLauncher.java','tools/quality/architecture/BatchValueArtifactCoverageMeasure.java','tools/quality/pg121','tools/quality/architecture/AuthorizationFixtureJunitLauncher.java','tools/quality/architecture/AuthorizationFixtureArtifactCoverageMeasure.java','tools/quality/architecture/MediaWireFixtureJunitLauncher.java','tools/quality/architecture/MediaWireFixtureArtifactCoverageMeasure.java','tools/quality/architecture/ApiWebScrapeFixtureJunitLauncher.java','tools/quality/architecture/ApiWebScrapeFixtureArtifactCoverageMeasure.java','tools/quality/architecture/WebBusinessWireLineCoverage.java','tools/quality/architecture/WebBusinessRecordBoundaryJunitLauncher.java','tools/quality/architecture/WebBusinessRecordArtifactCoverageMeasure.java','tools/quality/pg120','tools/quality/architecture/WebBusinessWireFixtureJunitLauncher.java','tools/quality/architecture/WebBusinessWireFixtureArtifactCoverageMeasure.java','tools/quality/architecture/JmsProxyFixtureJunitLauncher.java','tools/quality/architecture/JmsProxyFixtureArtifactCoverageMeasure.java','tools/quality/architecture/StorageAttributeFixtureJunitLauncher.java','tools/quality/architecture/StorageAttributeFixtureArtifactCoverageMeasure.java','tools/quality/pg119','tools/quality/architecture/SessionJsonFixtureJunitLauncher.java','tools/quality/architecture/SessionJsonFixtureArtifactCoverageMeasure.java','tools/quality/architecture/WebExporterFixtureJunitLauncher.java','tools/quality/architecture/WebExporterFixtureArtifactCoverageMeasure.java','tools/quality/architecture/MqMediaCollectorFixtureJunitLauncher.java','tools/quality/architecture/MqMediaCollectorFixtureArtifactCoverageMeasure.java','tools/quality/pg118','tools/quality/architecture/JobOutboxValueFixtureJunitLauncher.java','tools/quality/architecture/JobOutboxValueFixtureArtifactCoverageMeasure.java','tools/quality/architecture/JdbcMetricCollectorFixtureJunitLauncher.java','tools/quality/architecture/JdbcMetricCollectorFixtureArtifactCoverageMeasure.java','tools/quality/architecture/MqSuppliedRecorderFixtureJunitLauncher.java','tools/quality/architecture/MqSuppliedRecorderFixtureArtifactCoverageMeasure.java','tools/quality/pg117','tools/quality/architecture/JvmSystemFixtureJunitLauncher.java','tools/quality/architecture/JvmSystemFixtureArtifactCoverageMeasure.java','tools/quality/architecture/StandardCompositionFixtureJunitLauncher.java','tools/quality/architecture/StandardCompositionFixtureArtifactCoverageMeasure.java','tools/quality/architecture/DbPoolBindingFixtureJunitLauncher.java','tools/quality/architecture/DbPoolBindingFixtureArtifactCoverageMeasure.java','documents/','evidence/01_PT/','src/','tools/quality/pg115','tools/quality/pg116','tools/quality/architecture/MetricHttpGuardJunitLauncher.java','tools/quality/architecture/MetricHttpFixtureJunitLauncher.java','tools/quality/architecture/MetricHttpFixtureArtifactCoverageMeasure.java','tools/quality/architecture/GcLiteralFixtureJunitLauncher.java','tools/quality/architecture/GcFakeGuardJunitLauncher.java','tools/quality/architecture/GcFakeGuardArtifactCoverageMeasure.java')


def selected(names):
    return set(names)-HELD


def main():
    assert not OUT.exists()
    safe = 'tools/quality/pg10606_fixed_error_public_delta.py'
    assert selected(HELD) == set() and selected([safe,*HELD]) == {safe}
    assert selected([safe,safe,*HELD]) == {safe} and selected([]) == set()
    raw = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,'--'],cwd=ROOT)
    raw += subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT)
    assert raw.endswith(b'\0')
    names = selected(raw.decode().split('\0')[:-1])
    assert not names&HELD
    rows, findings = [], []
    for name in sorted(names):
        assert name.startswith(PREFIXES)
        path = ROOT/name
        assert '/private' not in name and not path.is_symlink() and path.is_file()
        content = path.read_bytes()
        assert b'\0' not in content
        content.decode('utf-8')
        rows.append(dict(path=name,sha256=hashlib.sha256(content).hexdigest()))
        for rule,pattern in RULES.items():
            findings.extend(dict(path=name,rule=rule,line=content[:m.start()].count(b'\n')+1) for m in pattern.finditer(content))
    assert rows
    value = dict(actualExit=1 if findings else 0,before=BEFORE,files=rows,findings=findings,
        scope='EXPLICIT_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_WHOLE_G07',
        heldFilesNotReadByThisInvocation=sorted(HELD),selectionMetadataVectors=4,
        globalHeldFileUnreadAssurance='NOT_PROVEN_AFTER_BROAD_SEARCH',actualSecretCount=None,
        wholeWorktreeCleanClaim=False,productTestsExecuted=0,externalActions=0,formalUpdated=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),
        manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
