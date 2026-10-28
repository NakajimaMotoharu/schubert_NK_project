"""Independent XML/current source/ownership binding for six resource contexts, not Product PT."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg13748_main_resource_six_contexts as selected

PIN = '15a135049323d1dc28e7e5cabb178ae95addaa3d896d1d549c2ad135ca5237ff'
OUT = data.BASE/'PG13750-main-resource-six-post-v1'

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    review = data.read_checked(selected.OUT/'review.json',raw['reviewSha256']);actual = review['rows']
    assert raw['source'] == selected.SOURCE and raw['actualExit'] == raw['productTestsExecuted'] == 0 and raw['sourceContexts'] == raw['rawRetained'] == 6
    assert review['dependencySourceHashes'] == selected.DEPENDENCIES
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in review['dependencySourceHashes'].items())
    measured = data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    xml = (data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml) == measured['reports']['pmd']['sha256']
    catalog = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    for row in actual:
        pin,owner,fields = selected.TARGETS[row['path']];variable = row['variable'];identity = fields[variable]
        text = (data.ROOT/row['path']).read_text();assert data.sha(text.encode()) == row['sourceSha256'] == pin
        assert row['id'] == identity and row['source'] == selected.SOURCE and row['rule'] == 'CloseResource'
        nodefile, = [v for v in ET.fromstring(xml) if v.tag.rpartition('}')[2] == 'file' and v.get('name').endswith('/'+row['path'])]
        node, = [v for v in nodefile if v.attrib == row['attributes']]
        old, = [v for v in catalog if v['id'] == identity]
        assert old['path'] == row['path'] and old['attributes'] == node.attrib and old['rowSha256'] == row['originalRowSha256'] and old['inputSha256'] == pin
        a = node.attrib;lines = text.splitlines(keepends=True)
        start = sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        end = sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        assert text[start:end] == variable and (row['spanStart'],row['spanEndExclusive'],row['spanSha256']) == (start,end,data.sha(variable.encode()))
        assert row['reason'] == selected.REASONS[identity] and row['canonicalOwner'] == row['canonicalCostOwner'] == owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True
        assert row['sourceChanged'] is row['nativeRuntimeProven'] is False and type(row['productTestsExecuted']) is int and row['productTestsExecuted'] == 0
    assert len(actual) == 6 and {r['id'] for r in actual} == selected.IDS
    expected = wire(actual)
    def assess(value):
        if wire(value) != expected:raise ValueError('exact typed resource ownership contract required')
    labels = []
    for key,value in [('id','UNKNOWN'),('source','0'*40),('sourceSha256','0'*64),('variable','UNKNOWN'),('spanEndExclusive',0),('spanStart',0),('spanSha256','0'*64),('reason',''),('canonicalCostOwner','UNKNOWN'),('rawRetained',False),('rawRetained',0),('sourceChanged',True),('nativeRuntimeProven',True),('productTestsExecuted',False)]:
        bad = copy.deepcopy(actual);bad[0][key] = value;assert wire(bad) != expected
        try:assess(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered resource context accepted')
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=6,metadataNegativeVectors=len(labels),labels=labels,rawRetained=6,productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
