"""Independent nine-field source/XML/token binding; metadata checks, not Product PT."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
import pg13714_main_nine_volatile_contexts as selected

PIN = 'd452722d17ee6449bba56233503d5311629cea47911b904e7fe33259ae74d1dc'
OUT = data.BASE/'PG13716-main-nine-volatile-post-v1'

def wire(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'))

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    actual = data.read_checked(selected.OUT/'review.json',raw['reviewSha256'])['rows']
    assert raw['source'] == selected.SOURCE and raw['actualExit'] == raw['productTestsExecuted'] == 0 and raw['sourceContexts'] == raw['rawRetained'] == 9
    measured = data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    xml = (data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml) == measured['reports']['pmd']['sha256']
    catalog = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    for row in actual:
        pin,owner,fields = selected.TARGETS[row['path']];field = row['field'];identity,count = fields[field]
        text = (data.ROOT/row['path']).read_text();assert data.sha(text.encode()) == row['sourceSha256'] == pin
        assert row['id'] == identity and row['source'] == selected.SOURCE and row['rule'] == 'AvoidUsingVolatile'
        nodefile, = [v for v in ET.fromstring(xml) if v.tag.rpartition('}')[2] == 'file' and v.get('name').endswith('/'+row['path'])]
        node, = [v for v in nodefile if v.attrib == row['attributes']]
        old, = [v for v in catalog if v['id'] == identity]
        assert old['path'] == row['path'] and old['attributes'] == node.attrib and old['rowSha256'] == row['originalRowSha256']
        a = node.attrib;lines = text.splitlines(keepends=True)
        start = sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        end = sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        assert text[start:end] == field and (row['spanStart'],row['spanEndExclusive'],row['spanSha256']) == (start,end,data.sha(field.encode()))
        points = [m.start() for m in LEX.finditer(text) if m.group() == field]
        assert row['fieldTokenOffsets'] == points and row['fieldTokenCount'] == count == len(points)
        assert all(text[p:p+len(field)] == field for p in points) and start in points
        assert row['reason'] == selected.REASONS[identity] and row['canonicalOwner'] == row['canonicalCostOwner'] == owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True
        assert row['compoundAtomicityProven'] is row['nativeRuntimeProven'] is False and type(row['productTestsExecuted']) is int and row['productTestsExecuted'] == 0
    assert len(actual) == 9 and {r['id'] for r in actual} == selected.IDS
    expected = wire(actual)
    def assess(value):
        if wire(value) != expected:raise ValueError('exact typed nine-row public-source contract required')
    labels = []
    for key,value in [('id','UNKNOWN'),('source','0'*40),('sourceSha256','0'*64),('field','UNKNOWN'),('spanEndExclusive',0),('fieldTokenOffsets',[]),('fieldTokenCount',0),('reason',''),('canonicalCostOwner','UNKNOWN'),('rawRetained',False),('rawRetained',0),('compoundAtomicityProven',True),('nativeRuntimeProven',True),('productTestsExecuted',False)]:
        bad = copy.deepcopy(actual);bad[0][key] = value;assert wire(bad) != expected
        try:assess(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered static reason accepted')
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=9,metadataNegativeVectors=len(labels),labels=labels,rawRetained=9,productTestsExecuted=0,coverage=None,compoundAtomicityProven=False,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
