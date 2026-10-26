"""Independent original finding set and source delta accounting; no analyzer or Product replay."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11028_current_remaining_form_delta import parent_state

OUT=data.BASE/'PG11060-current-api-request-delta-post-v1'
SOURCE='9b255cbe300d1feffeeee076cfa5af318c9b1bb1'


def contract(value,expected):
    if value!=expected:
        raise ValueError('exact original ID set and independently calculated current totals')


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    manifest_path=data.BASE/'PG11058-current-api-request-delta-v1/manifest.json'
    primary=data.read_checked(manifest_path,'369065bbe3bd90508dd403f50190ca1f9785f1d9ada2a86000d29d81af503390')
    delta=data.read_checked(manifest_path.parent/'delta.json',primary['deltaSha256'])
    parent=data.read_checked(data.BASE/'PG11028-current-remaining-form-delta-v1/manifest.json','a1b84233e2748889d2e659c3b611d6f8560685f5e7d84edb9a3e2018e9bb6f49')
    earlier=data.read_checked(data.BASE/'PG11028-current-remaining-form-delta-v1/delta.json',parent['deltaSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    contexts=data.read_checked(data.BASE/'PG11054-api-request-context-v1/manifest.json','88ede17e3d71b67ce4f761051ed20f07f4f11a67091a7af4038955da060ec668')
    rows=data.read_checked(data.BASE/'PG11054-api-request-context-v1/contexts.json',contexts['contextsSha256'])
    normal=data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
    prior=data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json','5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    source_inputs=normal['begin']['inputHashes']
    changed={p:h for p,h in source_inputs.items() if p.endswith('.java') and prior['begin']['inputHashes'][p]!=h}
    assert changed==delta['sourceInputDelta'] and len(changed)==4
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in source_inputs.items())
    ids,refs,pending=parent_state()
    old_scope=set(earlier['removedFindingIds'])|{r['id'] for r in earlier['freshRows']}
    ids-=set(earlier['removedFindingIds'])
    refs=(refs-old_scope)|{r['id'] for r in earlier['freshRows']}
    pending=(pending-old_scope)|{r['id'] for r in earlier['freshRows']}
    scope={r['id'] for r in original if r['path'] in changed}
    new_ids={r['id'] for r in delta['freshRows']}
    reviewed={r['id'] for r in rows}
    assert len(scope)==31 and len(new_ids)==17 and reviewed<=new_ids and len(reviewed)==16
    assert new_ids-reviewed=={'PMD-00613'}
    assert scope-new_ids==set(delta['removedFindingIds']) and len(scope-new_ids)==14
    expected=dict(source=SOURCE,currentRaw=len(ids-(scope-new_ids)),refs=len((refs-scope)|reviewed),
        pending=len((pending-scope)|reviewed),noReference=len((ids-(scope-new_ids))-((refs-scope)|reviewed)))
    actual=dict(source=delta['source'],currentRaw=delta['sourceDerivedRaw'],refs=delta['joinedContextWarnings'],
        pending=delta['sourceReboundCurrentWholePending'],noReference=delta['noCurrentReferenceInThisJoin'])
    contract(actual,expected)
    negatives=0
    for key,value in [('source','old'),('currentRaw',9204),('refs',2738),('pending',0),('noReference',0)]:
        bad=copy.deepcopy(actual)
        bad[key]=value
        try:
            contract(bad,expected)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('incorrect count/source accepted')
    tool=data.ROOT/'tools/quality/pg11058_current_api_request_delta.py'
    before=tool.read_text().replace('from pathlib import Path','import json\nfrom pathlib import Path',1)
    assert data.sha(before.encode())==primary['invocation']['entrypointSha256']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(manifest_path.read_bytes()),
        counts=expected,metadataNegativeVectors=negatives,producerLintPassed=False,producerBodyExit=0,
        unusedImportOnlyInverseVerified=True,currentProducerToolSha256=data.sha(tool.read_bytes()),
        sourceCount=1810,sourceChanges=4,mainRaw=1512,testRaw=7678,alreadyCountedCorrections14=True,
        productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
