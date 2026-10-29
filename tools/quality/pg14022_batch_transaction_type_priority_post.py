"""Independent XML multiplicity and static failure-priority model, never live failure/stop PT."""
from collections import Counter
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg14021_batch_transaction_type_priority_contexts_v2 as selected

OUT = data.BASE/'PG14022-batch-transaction-type-priority-twenty-eight-post-v1'
PIN = '544d50d47ef9abee500841c698b05dd39cddc973bab634e187d5b0846105a1fd'

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    review = data.read_checked(selected.OUT/'review.json',raw['reviewSha256']);actual = review['rows']
    assert raw['source']==selected.SOURCE and raw['actualExit']==raw['productTestsExecuted']==0 and raw['rawRetained']==28
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
        assert len(nodes)==row['rawDiagnosticMultiplicity']==2 and all(node.attrib==old['attributes'] for node in nodes)
        key = (row['path'],wire(row['attributes']));assert row['occurrenceOrdinal']==seen[key] and type(row['occurrenceOrdinal']) is int;seen[key]+=1
        assert old['rowSha256']==row['originalRowSha256']
        attributes = nodes[0].attrib;lines = text.splitlines(keepends=True)
        start = sum(map(len,lines[:int(attributes['beginline'])-1]))+int(attributes['begincolumn'])-1
        end = sum(map(len,lines[:int(attributes['endline'])-1]))+int(attributes['endcolumn'])-1
        assert text[start:end]==row['typeToken'] and row['typeToken'] in ('Error','RuntimeException','BatchRepositoryException','CleanupStoppedException')
        assert (row['spanStart'],row['spanEndExclusive'],row['spanSha256'])==(start,end,data.sha(text[start:end].encode()))
        assert row['catchAnchor']==text.rfind('catch (',0,start)
        assert row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True and row['sourceChanged'] is row['nativeRuntimeProven'] is False
        assert type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0
        spans.add((row['path'],start,end));clauses.add((row['path'],row['catchAnchor']))
    assert len(actual)==28 and len(spans)==14 and len(clauses)==2 and sorted(seen.values())==[2]*14
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
    assert source_rejected==22
    # Fixed category selection from SS341, never Product/Throwable execution.
    table={('unknown','known'):'primary',('unknown','unknown'):'primary',('known','unknown'):'cleanup',('known','known'):'fixed'}
    models=[]
    for (primary,cleanup),expected_policy in table.items():
        selected_policy='primary' if primary=='unknown' else ('cleanup' if cleanup=='unknown' else 'fixed')
        assert selected_policy==expected_policy
        models.append(dict(primary=primary,cleanup=cleanup,selection=selected_policy))
    expected_anchors=[]
    for path in selected.TARGETS:
        text=(data.ROOT/path).read_text()
        anchor=text.index('catch (SQLException | RuntimeException | Error cleanupFailure)')
        expected_anchors.append((path,anchor))
        assert (path,anchor) in clauses
    def catch_keys(value):
        if sorted(value)!=sorted(expected_anchors) or len(value)!=len(set(value)):raise ValueError('warning-containing cleanup catches only, not all primary catches')
    catch_keys(list(clauses))
    anchor_negatives=0
    for index,(path,anchor) in enumerate(expected_anchors):
        text=(data.ROOT/path).read_text()
        outer=text.index('catch (SQLException | RuntimeException | Error failure)')
        for replacement in [(path,outer),(path,anchor+1)]:
            bad=list(expected_anchors);bad[index]=replacement
            try:catch_keys(bad)
            except ValueError:anchor_negatives+=1
            else:raise AssertionError('outer or off-by-one catch accepted')
    assert anchor_negatives==4
    assert review['approvedDesignHashes']==selected.DESIGN
    assert all(data.sha((data.ROOT/p).read_bytes())==sha for p,sha in selected.DESIGN.items())
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=28,uniqueOperandSpans=14,uniqueCatchClauses=2,rawMultiplicityPerSpan=2,rawRetained=28,
        metadataNegativeVectors=len(labels),labels=labels,warningCatchAnchorNegativeVectors=anchor_negatives,correctedToolBug='BUG2085/YKT1833',sourceOwnershipNegativeVectors=source_rejected,staticPriorityModels=models,modelsAreNotProductTests=True,
        productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
