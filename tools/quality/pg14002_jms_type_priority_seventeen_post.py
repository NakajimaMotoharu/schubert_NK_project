"""Independent XML multiplicity and static failure-priority model, never live failure/stop PT."""
from collections import Counter
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg14000_jms_type_priority_seventeen_contexts as selected

OUT = data.BASE/'PG14002-jms-type-priority-seventeen-post-v1'
PIN = 'db1b067e3924d9cb775c38ab1a2023c43d34c254dd401ed0b602da1ed180b145'

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    review = data.read_checked(selected.OUT/'review.json',raw['reviewSha256']);actual = review['rows']
    assert raw['source']==selected.SOURCE and raw['actualExit']==raw['productTestsExecuted']==0 and raw['rawRetained']==17
    measured = data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    xml = (data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml)==measured['reports']['pmd']['sha256']
    catalog = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    seen = Counter();spans = set();clauses = set()
    for row in actual:
        pin,owner,identities = selected.TARGETS[row['path']]
        old, = [r for r in catalog if r['id']==row['id']];assert row['id'] in identities
        text = (data.ROOT/row['path']).read_text();assert data.sha(text.encode())==row['sourceSha256']==pin==old['inputSha256']
        assert row['source']==selected.SOURCE and row['rule']==selected.RULE and row['reason']==selected.reason(row['path'],row['attributes']['method'])
        nodefile, = [v for v in ET.fromstring(xml) if v.tag.rpartition('}')[2]=='file' and v.get('name').endswith('/'+row['path'])]
        nodes = [v for v in nodefile if v.attrib==row['attributes']]
        assert len(nodes)==row['rawDiagnosticMultiplicity'] and len(nodes) in (1,2) and all(node.attrib==old['attributes'] for node in nodes)
        key = (row['path'],wire(row['attributes']));assert row['occurrenceOrdinal']==seen[key] and type(row['occurrenceOrdinal']) is int;seen[key]+=1
        assert old['rowSha256']==row['originalRowSha256']
        attributes = nodes[0].attrib;lines = text.splitlines(keepends=True)
        start = sum(map(len,lines[:int(attributes['beginline'])-1]))+int(attributes['begincolumn'])-1
        end = sum(map(len,lines[:int(attributes['endline'])-1]))+int(attributes['endcolumn'])-1
        assert text[start:end]==row['typeToken']=='Error'
        assert (row['spanStart'],row['spanEndExclusive'],row['spanSha256'])==(start,end,data.sha(b'Error'))
        assert row['catchAnchor']==text.rfind('catch (',0,start)
        assert row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True and row['sourceChanged'] is row['nativeRuntimeProven'] is False
        assert type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0
        spans.add((row['path'],start,end));clauses.add((row['path'],row['catchAnchor']))
    assert len(actual)==17 and len(spans)==12 and len(clauses)==9 and sorted(seen.values())==[1]*7+[2]*5
    assert {r['id'] for r in actual}==selected.IDS
    expected = wire(actual)
    def assess(value):
        if wire(value)!=expected:raise ValueError('exact typed raw occurrence and priority contract required')
    labels = []
    for key,value in [('id','UNKNOWN'),('source','0'*40),('sourceSha256','0'*64),('catchAnchor',-1),('occurrenceOrdinal',2),('rawDiagnosticMultiplicity',0),('spanStart',0),('spanEndExclusive',0),('spanSha256','0'*64),('reason',''),('canonicalCostOwner','UNKNOWN'),('rawRetained',False),('rawRetained',0),('sourceChanged',True),('nativeRuntimeProven',True),('productTestsExecuted',False)]:
        bad = copy.deepcopy(actual);bad[0][key]=value
        try:assess(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered priority/occurrence accepted')
    source_rejected=0
    for path in selected.TARGETS:
        text=(data.ROOT/path).read_text();selected.source_guards(path,text)
        for phrase in selected.GUARDS[path.rpartition('/')[2]]:
            assert phrase in text
            try:selected.source_guards(path,text.replace(phrase,'REMOVED_EXPECTED_CONTRACT'))
            except (AssertionError,ValueError):source_rejected+=1
            else:raise AssertionError('missing specific owner/priority guard accepted')
    assert source_rejected==47
    # Independent static selection tables, not execution of Product/Throwable methods.
    sender_table={(False,False):'primary',(False,True):'secondary',(True,False):'primary',(True,True):'primary'}
    legacy_close_table={(False,False):'primary',(False,True):'secondary',(True,False):'primary',(True,True):'secondary'}
    models=[]
    for primary_error,secondary_error in sender_table:
        sender='secondary' if secondary_error and not primary_error else 'primary'
        direct_close='secondary' if secondary_error else 'primary'
        assert sender==sender_table[primary_error,secondary_error]
        assert direct_close==legacy_close_table[primary_error,secondary_error]
        models.append(dict(primaryError=primary_error,secondaryError=secondary_error,sender=sender,legacyWebTransactionClose=direct_close))
    assert review['approvedDesignHashes']==selected.DESIGN
    assert all(data.sha((data.ROOT/p).read_bytes())==sha for p,sha in selected.DESIGN.items())
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=17,uniqueOperandSpans=12,uniqueCatchClauses=9,rawMultiplicityCounts=dict(single=7,double=5),rawRetained=17,
        metadataNegativeVectors=len(labels),labels=labels,sourceOwnershipNegativeVectors=source_rejected,staticPriorityModels=models,modelsAreNotProductTests=True,
        productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
