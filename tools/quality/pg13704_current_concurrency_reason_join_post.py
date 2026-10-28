"""Independent published XML/old-reason five-way binding and typed metadata negatives only."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg13703_current_concurrency_reason_join_recovery as selected

PIN = '637d3ce581ffc589ea0519e77a1f37a5f1946dcf1070f61ebecb3132b99d98a4'
OUT = data.BASE/'PG13704-current-concurrency-reason-join-post-v1'

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def main():
    invocation = capture(__file__);assert not OUT.exists()
    original = data.read_checked(selected.OUT/'manifest.json',PIN);verify(original['invocation'])
    actual = data.read_checked(selected.OUT/'review.json',original['reviewSha256'])['rows']
    assert original['source'] == selected.SOURCE and original['actualExit'] == original['newReasons'] == original['productTestsExecuted'] == 0
    assert original['sourceContexts'] == original['reusedReasons'] == original['rawRetained'] == 5
    measured = data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    xml = (data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml) == measured['reports']['pmd']['sha256']
    catalog = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    for row in actual:
        assert row['id'] in selected.IDS and row['path'] in selected.TARGETS
        target = selected.TARGETS[row['path']];text = (data.ROOT/row['path']).read_text()
        assert row['source'] == selected.SOURCE and row['sourceSha256'] == data.sha(text.encode()) == target['sha256']
        oldname,oldpin,filename,filepin = selected.OLD[row['path']]
        oldm = data.read_checked(data.BASE/oldname/'manifest.json',oldpin);assert oldm['actualExit'] == 0
        oldrows = data.read_checked(data.BASE/oldname/filename,filepin)
        previous, = [v for v in oldrows if v['sourcePath'] == row['path'] and v['rule'] == target['rule'] and all(v[k] == row['attributes'][k] for k in ['beginline','endline','begincolumn','endcolumn'])]
        assert row['priorManifest'] == oldname and row['priorManifestSha256'] == oldpin and row['priorFileSha256'] == filepin
        assert row['priorDecisionSha256'] == data.sha(json.dumps(previous,sort_keys=True).encode()) and row['reason'] == previous['reason']
        nodefile, = [v for v in ET.fromstring(xml) if v.tag.rpartition('}')[2] == 'file' and v.get('name').endswith('/'+row['path'])]
        node, = [v for v in nodefile if v.attrib == row['attributes']]
        identity, = [v for v in catalog if v['id'] == row['id']]
        assert identity['path'] == row['path'] and identity['attributes'] == node.attrib and identity['rowSha256'] == row['originalRowSha256']
        a = row['attributes'];lines = text.splitlines(keepends=True)
        start = sum(len(v) for v in lines[:int(a['beginline'])-1])+int(a['begincolumn'])-1
        end = sum(len(v) for v in lines[:int(a['endline'])-1])+int(a['endcolumn'])-1
        value = text[start:end];assert value == a.get('variable',a.get('method'))
        assert (row['spanStart'],row['spanEndExclusive'],row['spanSha256']) == (start,end,data.sha(value.encode()))
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == target['owner']
        assert row['rawRetained'] is row['currentWholeJoinPending'] is row['reasonReused'] is True
        assert row['newReason'] is row['historicalRuntimeTransferred'] is row['currentRuntimeQualification'] is False and type(row['productTestsExecuted']) is int and row['productTestsExecuted'] == 0
    assert len(actual) == 5 and {r['id'] for r in actual} == selected.IDS
    expected = wire(actual)
    def assess(value):
        if wire(value) != expected:raise ValueError('exact typed five-way binding required')
    negatives = []
    for field,value in [('source','0'*40),('sourceSha256','0'*64),('id','UNKNOWN'),('rule','UNKNOWN'),('spanStart',0),('spanEndExclusive',0),('priorManifestSha256','0'*64),('reason','UNKNOWN'),('canonicalOwner','UNKNOWN'),('rawRetained',False),('rawRetained',0),('newReason',True),('historicalRuntimeTransferred',True)]:
        bad = copy.deepcopy(actual);bad[0][field] = value
        assert wire(bad) != expected
        try:assess(bad)
        except ValueError:negatives.append(field+':'+type(value).__name__)
        else:raise AssertionError('altered static binding accepted')
    bad = copy.deepcopy(actual);bad[-1] = copy.deepcopy(bad[0])
    try:assess(bad)
    except ValueError:negatives.append('duplicate')
    else:raise AssertionError('duplicate accepted')
    assert len(negatives) == 14
    verify(original['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=original['reviewSha256'],sourceContexts=5,newReasons=0,reusedReasons=5,metadataNegativeVectors=14,negativeLabels=negatives,productTestsExecuted=0,oldRuntimeTransferred=False,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
