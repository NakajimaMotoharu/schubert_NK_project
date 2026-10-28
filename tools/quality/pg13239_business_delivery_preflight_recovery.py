"""Preserve all current raw warnings; explain new2 using an independent original-source static comparison."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, prior_normal, inverse, negative, out
from f03_literal_batch_diagnostic_v3 import signature
import pg13237_business_delivery_literal_config as cfg

OUT = data.BASE/'PG13239-business-delivery-preflight-recovery-v1'

def supplemental(comparison,original):
    assert comparison['originalHasSameTwo'] is True and comparison['productTestsExecuted'] == 0 and not comparison['targetRuntimeInvoked']
    source = next(row for row in original['sources'] if row['path'].endswith('/LoginInboxServiceTest.java'))
    rows = sorted(comparison['originalUnderCurrentConditions'],key=lambda r:r['attributes']['method'])
    assert len(rows) == 2
    return [dict(id='PMD-NEW-PG13240-'+str(i+1).zfill(3),path=source['path'],originalSourceSha256=source['sha256'],attributes=row['attributes'],message=row['message'],
        purpose='Existing Test eagerly obtains Connection, supplies it through DataSource callback to JdbcSyncRequestProcessor, then asserts closed; processor owns returned JDBC with try-with-resources',
        status='STATIC_SOURCE_PURPOSE_REVIEWED_DYNAMIC_AND_PRE_HANDOFF_HOLD',manualPurposeReviewComplete=True,actualViolation=None,ptExecutionExempt=False,
        baselineObservationNewlyRecorded=True,newSourceDefectInferred=False,canonicalOwner='WBS-P007-04',canonicalCostOwner='WBS-P007-04') for i,row in enumerate(rows)]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    failed = data.ROOT.parent/'pgpt-runs/PG379'/out(cfg,cfg.PREFLIGHT_NUMBER).name.lower()
    begin = json.loads((failed/'begin.safe.json').read_bytes());observed = json.loads((failed/'observed.safe.json').read_bytes())
    original = original_value(cfg);normal = prior_normal(cfg)
    comparison = data.read_checked(data.BASE/'PG13241-login-original-static-delta-v1/manifest.json','706fe062f667570d28fdd0b62844ac76cedab545c83864029c8988288e9f66fd')
    extra = supplemental(comparison,original);hashes = begin['candidateSourceHashes'];inverses = {};negatives = {};expected = {};removed = []
    for row in original['sources']:
        path = row['path'];text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path]
        inverses[path] = inverse(row['text'],text,row['mapping']);negatives[path] = negative(row['text'],text,row['mapping'])
        selected = {r['id'] for r in row['mapping']};removed += sorted(selected)
        expected[path] = Counter(signature(r['attributes'],r['message']) for r in row['findings'] if r['id'] not in selected)
    assert len(removed) == 137 and sum(negatives.values()) == 161
    assert {p for p,sha in normal['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == set(cfg.PATHS)
    for row in extra:expected[row['path']][signature(row['attributes'],row['message'])] += 1
    actual = {p:Counter() for p in cfg.PATHS}
    for row in observed['retainedRawFindings']:actual[row['path']][signature(row['attributes'],row['message'])] += 1
    assert actual == expected
    stages = {}
    for name,code in [('pmd',4),('checkstyle',0)]:
        stage = json.loads((failed/(name+'-exit.safe.json')).read_bytes());assert stage['actualExit'] == code and not stage['timedOut']
        for suffix in ['stdout','stderr']:assert data.sha((failed/(name+'.'+suffix)).read_bytes()) == stage[suffix+'Sha256']
        assert data.sha((failed/(name+'.xml')).read_bytes()) == observed['reports'][name];stages[name] = stage
    assert not [x for x in ET.parse(failed/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**begin['toolAndRuleHashes'],**begin['dependencyHashes']}.items())
    assert inverses == begin['originalTokenInverses'] and negatives == begin['negativeVectors']
    processor = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java'
    processor_raw = (data.ROOT/processor).read_bytes();assert data.sha(processor_raw) == normal['begin']['inputHashes'][processor]
    assert 'try (Connection connection =' in processor_raw.decode() and 'database.getConnection()' in processor_raw.decode()
    verify(invocation);OUT.mkdir()
    for name in observed['reports']:
        with (OUT/(name+'.xml')).open('xb') as stream:stream.write((failed/(name+'.xml')).read_bytes())
    data.write(OUT/'additional-findings.json',dict(source=cfg.BASE_SOURCE,findings=extra,sourceCodeChanged=False,
        independentOriginalComparisonSha256='706fe062f667570d28fdd0b62844ac76cedab545c83864029c8988288e9f66fd',processorSourceSha256=data.sha(processor_raw),
        originalGlobalOmissionCause='UNRESOLVED_ANALYSIS_CONTEXT_DIFFERENCE_NOT_LITERAL_REFACTOR_REGRESSION',dynamicCorrectnessProven=False,preHandoffFailureCleanupProven=False))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=cfg.BASE_SOURCE,invocation=invocation,candidateSourceHashes=hashes,
        originalTokenInverses=inverses,negativeVectors=negatives,removedFindingIds=removed,retainedRawFindings=observed['retainedRawFindings'],rawStatic=len(observed['retainedRawFindings']),rawStaticGateExit=1,
        additionalFindings=extra,additionalFindingsSha256=data.sha((OUT/'additional-findings.json').read_bytes()),originalStartAccountingPreserved=dict(sourceDerivedRaw=8143,testRaw=6641,totalPriorCorrections=1282),
        originalGuardActualExit=1,originalStaticStages=stages,reports=observed['reports'],toolAndRuleHashes=begin['toolAndRuleHashes'],dependencyHashes=begin['dependencyHashes'],
        original137RemovalsNotNet135=True,originalCurrentStaticReexecuted=False,businessOrPtOracleChanged=False,
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(json.dumps(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),rawStatic=len(observed['retainedRawFindings']),originalRemoved=137,additionalObserved=2)))

if __name__ == '__main__':main()
