"""Independent XML multiplicity and static failure-priority model, never live failure/stop PT."""
from collections import Counter
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg14028_remaining_main_type_priority_contexts as selected

OUT = data.BASE/'PG14030-remaining-main-type-priority-twenty-two-post-v1'
PIN = 'ac8f64cc8ae4758453c9e1e3a63b759246397c393b522728510110a18d75a391'

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def independent_anchor(identity,text):
    if identity in ('PMD-00107','PMD-07193'):needle='catch (SQLException | RuntimeException | Error closing)'
    elif identity in ('PMD-00114','PMD-00188','PMD-00189','PMD-07200'):needle='catch (RuntimeException | Error closing)'
    elif identity in ('PMD-00181','PMD-00182','PMD-00183','PMD-00184'):needle='catch (RuntimeException | Error notification)'
    elif identity=='PMD-00194':needle='catch (Exception | Error closing)'
    elif identity=='PMD-00395':needle='catch (StorageIoException | RuntimeException failure)'
    elif identity=='PMD-02819':needle='catch (RuntimeException | Error cleanup)'
    elif identity.startswith('PMD-030'):needle='catch (IOException | RuntimeException | Error cleanup)'
    else:
        assert identity=='PMD-07336';needle='catch (RuntimeException | Error failure)'
    return text.index(needle)

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    review = data.read_checked(selected.OUT/'review.json',raw['reviewSha256']);actual = review['rows']
    assert raw['source']==selected.SOURCE and raw['actualExit']==raw['productTestsExecuted']==0 and raw['rawRetained']==22
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
        assert text[start:end]==row['typeToken'] and row['typeToken'] in ('Error','IOException','InterruptedException','BatchRepositoryException','StorageIoException')
        assert (row['spanStart'],row['spanEndExclusive'],row['spanSha256'])==(start,end,data.sha(text[start:end].encode()))
        assert row['catchAnchor']==independent_anchor(row['id'],text)
        assert row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True and row['sourceChanged'] is row['nativeRuntimeProven'] is False
        assert type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0
        spans.add((row['path'],start,end));clauses.add((row['path'],row['catchAnchor']))
    assert len(actual)==22 and len(spans)==15 and len(clauses)==11 and sorted(seen.values())==[1]*8+[2]*7
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
    assert source_rejected==41
    # Scope after nested catch must use the enclosing startup/attempt catch.
    nested_negatives=0
    for identity,inner_declaration in [('PMD-00395','catch (StorageIoException cleanupFailure)'),('PMD-07336','catch (RuntimeException | Error closing)')]:
        row=next(r for r in actual if r['id']==identity);text=(data.ROOT/row['path']).read_text()
        outer=independent_anchor(identity,text);inner=text.index(inner_declaration,outer)
        assert outer<inner<row['spanStart'] and row['catchAnchor']==outer
        def enclosing_anchor(value):
            if type(value) is not int or value!=outer:raise ValueError('specific enclosing catch, not lexical predecessor after nested block')
        for bad in (inner,outer+1):
            try:enclosing_anchor(bad)
            except ValueError:nested_negatives+=1
            else:raise AssertionError('nested cleanup incorrectly treated as enclosing scope')
    assert nested_negatives==4
    models=[]
    assert review['approvedDesignHashes']==selected.DESIGN
    assert all(data.sha((data.ROOT/p).read_bytes())==sha for p,sha in selected.DESIGN.items())
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=22,uniqueOperandSpans=15,uniqueCatchClauses=11,rawMultiplicityCounts=dict(single=8,double=7),rawRetained=22,
        metadataNegativeVectors=len(labels),labels=labels,nestedCatchScopeNegativeVectors=nested_negatives,sourceOwnershipNegativeVectors=source_rejected,staticPriorityModels=models,modelsAreNotProductTests=True,
        productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
