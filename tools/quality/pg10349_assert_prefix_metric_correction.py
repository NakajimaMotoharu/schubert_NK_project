"""Preserve old qualified artifacts; correct prefix-token metric meaning, never infer calls/PT."""
from pathlib import Path
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens

OUT = data.BASE/'PG10349-assert-prefix-metric-correction-v1'
SOURCES = [
    ('PG10287-query-wire-oracle-source-post-v2','f6c380e1e7a6971e8b79eaf6da9b5df25b4efdee65c206cf3b91ef4028e29fb3',
        'originalAssertionCounts','PG10284-query-wire-oracle-six-compile-v1',108),
    ('PG10304-query-test-literal-post-v1','f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904',
        'assertionCounts','PG10302-query-test-literal-six-compile-v1',108),
    ('PG10339-result-profile-oracle-post-v2','935e104fcd4e3c8054ca677f2f9097225ff0f179538d7e3ac7a32dda03a87d6f',
        'assertionCounts','PG10336-result-profile-oracle-six-compile-v1',416)]
LABEL = 'ASSERT_PREFIX_TOKEN_OCCURRENCES_NOT_ASSERTION_INVOCATIONS'


def contract(value,reference):
    if value != reference or any(r['actualAssertionInvocationCounts'] is not None or r['metricMeaning'] != LABEL for r in value):
        raise ValueError('measured token occurrences only; no inferred assertion invocation counts')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    rows = []
    for run,digest,key,normal_run,total in SOURCES:
        original = data.read_checked(data.BASE/run/'manifest.json',digest)
        normal = data.read_checked(data.BASE/normal_run/'manifest.json',original['normalManifestSha256'])
        assert original['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
        assert original['source'] == normal['source'] and original['allOriginalAssertionsPreserved']
        root = Path(normal['jars']['api']['path']).parents[3]
        observed = {}
        for path,count in original[key].items():
            raw = (root/path).read_bytes()
            assert data.sha(raw) == original['sourceHashes'][path] == normal['begin']['inputHashes'][path]
            actual = sum(t.startswith('assert') for t in tokens(raw.decode()))
            assert actual == count
            observed[path] = actual
        assert sum(observed.values()) == total
        rows.append(dict(originalManifest=str((data.BASE/run/'manifest.json').relative_to(data.ROOT)),
            originalSha256=digest,source=original['source'],originalMetricKey=key,
            originalReportedValues=original[key],assertPrefixTokenOccurrences=observed,totalTokenOccurrences=total,
            actualAssertionInvocationCounts=None,metricMeaning=LABEL,
            originalFullTokenPreservationProofUnchanged=True,originalAssertionsPreservedBooleanUnchanged=True,
            productPtCountsChanged=False,formalCountsChanged=False,originalArtifactsModified=False))
    contract(rows,rows)
    negatives = []
    for label,edit in (
        ('mislabel',lambda r:r[0].update(metricMeaning='ASSERTION_COUNT')),
        ('invent-call-count',lambda r:r[0].update(actualAssertionInvocationCounts=108)),
        ('wrong-value',lambda r:r[0].update(totalTokenOccurrences=109))):
        mutated = copy.deepcopy(rows)
        edit(mutated)
        try: contract(mutated,rows)
        except ValueError: negatives.append(label)
        else: raise AssertionError('incorrect metric accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,corrections=rows,
        metadataNegativeVectors=negatives,source=None,multiSourceCorrectionNotRuntimeRebinding=True,
        actualAssertionInvocationCounts=None,productTestsExecuted=0,externalActions=0,
        originalArtifactsModified=False,newAccepted=0,formalUpdated=False,effortPercent=None,
        bug='BUG-1821',ykt='YKT-1572'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
