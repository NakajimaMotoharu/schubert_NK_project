"""Independent source/diagnostic-purpose binding; do not load or execute Product classes."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13149-systemd-source-context-post-v1'
MAIN = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java'
SHA = 'c931c6ee998ba8e9b1e982d569f7f5ca79f083a0c2cfb36600e5862134518cc9'

def validate_rows(rows,lines,original):
    assert len(rows) == len({r['id'] for r in rows}) == 14
    assert Counter(r['purposeCategory'] for r in rows) == dict(CURRENT_THREAD_IDENTITY_OBSERVATION=2,NATIVE_BOUNDARY_EXCEPTION_SYNTAX=11,BOUNDED_DECODE_CURSOR=1)
    for row in rows:
        assert row['path'] == MAIN and row['sourceSha256'] == SHA and row['source'] == '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3'
        assert row['sourceSnippet'] == lines[row['currentLine']-1].strip()
        assert row['originalSourceSha256'] == original[row['id']]['inputSha256']
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P018-03'
        assert row['actualViolation'] is None and row['manualPurposeReviewComplete'] is True
        assert row['dynamicExecutionQualificationInferred'] is False and row['ptExecutionExempt'] is False

def main():
    invocation = capture(__file__);assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13148-systemd-source-context-v1/manifest.json','4c4d139f02de58aa29294e4022ba8c710f3d0117349c86778841183dfd8ac7f2')
    review = data.read_checked(data.BASE/'PG13148-systemd-source-context-v1/review.json',m['reviewSha256'])
    raw = (data.ROOT/MAIN).read_bytes();assert data.sha(raw) == SHA
    original = {r['id']:r for r in json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())}
    lines = raw.decode().splitlines();validate_rows(review['rows'],lines,original)
    assert m['actualExit'] == m['productTestsExecuted'] == review['productTestsExecuted'] == review['sourceChanges'] == review['newAccepted'] == 0
    assert m['reviewedRows'] == 14 and m['newPurposeReferences'] == 12 and m['metadataNegativeVectors'] == 10
    assert [review[k] for k in ['sourceDerivedRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin']] == [8459,966,3271,975,5188]
    assert review['actualViolationCount'] is None and review['dynamicCorrectnessUnknown'] is True and review['ptExecutionExempt'] is False
    assert data.sha((data.BASE/'PG13132-main-literal-preflight-v1/pmd.xml').read_bytes()) == review['currentPmdXmlSha256']
    verify(m['invocation']);labels = []
    for label,key,value in [('owner','canonicalOwner','WBS-F03'),('source','sourceSha256','0'*64),('line','currentLine',review['rows'][0]['currentLine']+1),('execution-exemption','ptExecutionExempt',True)]:
        bad = copy.deepcopy(review['rows']);bad[0][key] = value
        assert json.dumps(bad,sort_keys=True) != json.dumps(review['rows'],sort_keys=True)
        try:validate_rows(bad,lines,original)
        except (AssertionError,IndexError):labels.append(label)
        else:raise AssertionError('false reviewed row accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        reviewedManifestSha256='4c4d139f02de58aa29294e4022ba8c710f3d0117349c86778841183dfd8ac7f2',reviewSha256=m['reviewSha256'],
        independentlyVerifiedRows=14,newPurposeReferences=12,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        sourceAndPreviousToolInputsUnchanged=True,productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
