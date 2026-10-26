"""Independent raw-line/source review metadata post, no target/runtime execution."""
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
OUT = data.BASE/'PG10500-fixture-volatile-context-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10498-fixture-volatile-context-v1/manifest.json',
        'd87371a698087db02fc61bce2a27dfbd48dfa00a1d7e2344d7434113e85f5ca5')
    rows = data.read_checked(data.BASE/'PG10498-fixture-volatile-context-v1/contexts.json',primary['contextsSha256'])
    static = data.read_checked(data.BASE/'PG10478-disjoint-six-literal-static-v1/manifest.json',
        '1cae3c256e3442adace66f78b521f981b119754d1edfeaef03ac0c2a4f73e4bc')
    assert primary['actualExit'] == 0 and primary['source'] == SOURCE
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    findings = [r for r in static['reports']['pmd']['details'] if r['rule'] == 'AvoidUsingVolatile']
    assert len(rows) == 3 and len(findings) == 10
    all_fields,all_writes = 0,0
    for row in rows:
        p = row['path']
        text = (data.ROOT/p).read_text()
        assert data.sha(text.encode()) == row['sha256'] == primary['sourceHashes'][p] == static['sourceHashes'][p]
        c = row['context']
        current = [r for r in findings if r['class'].split('.')[0] == Path(p).stem]
        assert sorted(r['variable'] for r in current) == c['controlFields']
        assert c['localFixturePerWritingMethod'] and c['fixtureMethodControlWritesBeyondInitializers'] == 0
        assert c['concurrentControlWrites'] == c['readModifyWriteControls'] == 0
        for r in current:
            line = text.splitlines()[int(r['beginline'])-1].strip()
            assert line.startswith('volatile ') and re.search(r'\b'+r['variable']+r'\s*=',line)
        start = text.index('void '+c['concurrentMethod']+'(')
        next_test = text.find('@Test',start)
        assert next_test > start
        body = text[start:next_test]
        assert 'new Fixture()' in body and 'Executors.newFixedThreadPool(8)' in body
        assert re.search(r'\.get\(10,\s*TimeUnit.SECONDS\)',body)
        assert not re.search(r'\b\w+\.(?:count|code|responder|failureStage)\s*(?:=(?!=)|\+\+|--|[+\-*/]=)',body)
        actual_writes = list(re.finditer(r'\bf\.(count|code|responder|failureStage)\s*=(?!=)',text))
        assert len(actual_writes) == len(c['writes'])
        for match,record in zip(actual_writes,c['writes']):
            line_number = text.count('\n',0,match.start())+1
            assert record['line'] == line_number and record['field'] == match[1]
            assert record['sourceLine'] == text.splitlines()[line_number-1].strip()
            annotation = text.rfind('@Test',0,match.start())
            assert annotation >= 0
            declaration = re.search(r'void\s+(\w+)\s*\(',text[annotation:match.start()])
            assert declaration and declaration[1] == record['method'] != c['concurrentMethod']
        all_fields += len(current)
        all_writes += len(actual_writes)
    assert all_fields == 10 and primary['currentPending'] == primary['currentContextuallyApplicableFindings'] == 0
    assert primary['originalRawFindings'] == 26 and primary['previousPending'] == 10
    assert primary['staticClassificationOnly'] and primary['productTestsExecuted'] == primary['targetCompilation'] == primary['targetClassLoading'] == primary['externalActions'] == 0
    assert primary['originalDynamicPtStatus'] == 'NOT_EXECUTED_HOLD' and not primary['wholeF03Accepted']
    assert len(primary['metadataNegativeVectors']) == 5
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256='d87371a698087db02fc61bce2a27dfbd48dfa00a1d7e2344d7434113e85f5ca5',
        sourceHashes=primary['sourceHashes'],fixtureControls=all_fields,outerSetupAssignments=all_writes,
        allRawVolatileFindingsBound=True,independentRawLineAndPhaseComparison=True,
        originalRawFindings=26,contextuallyApplicableFindings=0,pendingApplicability=0,
        classificationIsNarrowStaticContextOnly=True,originalDynamicPtStatus='NOT_EXECUTED_HOLD',
        rawReportRewritten=False,suppressionsAdded=False,wholeF03Accepted=False,
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        bug1837NamingIssueStillOpen=True,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
