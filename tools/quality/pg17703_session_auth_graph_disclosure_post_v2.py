"""Correct two profile disclosure fields only; preserve all completed Product/coverage evidence."""
import copy
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD=('PG17702-session-auth-graph-eight-post-v1','fd3c5636081f8d5ffcf3209e783c724bd161f5bfb422c23ee97641b83e377b1b')
OUT=data.BASE/'PG17703-session-auth-graph-disclosure-post-v2'
FIELDS=['publicSyntheticUuidFixture','publicFixedUuidFixtureOnly']
RELATED=[('PG17642-current-permit-data-six-post-v1','f59b1db5c4b23ed3981bad802ab621b9f90dce497ac030ce73d4a7892b87cfea','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflightTest.java'),('PG17662-root-entry-denial-four-post-v1','733fdc388fe8048c75b75a2a386b6aadce3b071339970bf786351eae051cd508','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceProofTest.java'),('PG17682-public-journal-deadline-nine-post-v1','1aa5ae001a9df7d4db9c140370c5f604b792b0e15d6e7f67359795a5d68707f1','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BrokerJournalEvidenceTest.java')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    old=data.read_checked(data.BASE/OLD[0]/'manifest.json',OLD[1])
    assert old['actualExit']==0 and old['source']==SOURCE and old['totals']=={'LINE':{'missed':0,'covered':35},'METHOD':{'missed':0,'covered':4},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':0,'covered':26}}
    assert all(old[k] is True for k in FIELDS)
    import pg17700_session_auth_graph_eight_pt_v1 as original
    checked={}
    for name,path in original.TESTS.items():
        text=path.read_text();assert 'UUID' not in text
        assert data.sha(path.read_bytes())==original.PINS[name]
        checked[str(path.relative_to(data.ROOT))]=original.PINS[name]
    for row in original.MAIN_UNITS.values():
        path=data.ROOT/original.source_path(row);assert 'UUID' not in path.read_text() and data.sha(path.read_bytes())==row['sha256']
        checked[str(path.relative_to(data.ROOT))]=row['sha256']
    normal=data.read_checked(original.COMPILE/'manifest.safe.json',original.COMPILE_SHA)
    related=[]
    for name,pin,relative in RELATED:
        p=data.read_checked(data.BASE/name/'manifest.json',pin);path=data.ROOT/relative
        assert p['actualExit']==0 and p['source']==SOURCE and all(p[k] is True for k in FIELDS)
        assert 'UUID' in path.read_text() and data.sha(path.read_bytes())==normal['begin']['inputHashes'][relative]
        related.append(dict(post=name,postSha256=pin,originalFixture=relative,fixtureSha256=data.sha(path.read_bytes()),requiresChange=False,reason='ORIGINAL_FIXED_UUID_VALUES_REALLY_PRESENT'))
    result=copy.deepcopy(old);result.update(invocation=invocation,**{k:False for k in FIELDS})
    result.update(disclosureCorrectionOf=list(OLD),correctedDisclosureFields=FIELDS,originalCoverageProofManifestSha256=OLD[1],originalSelectedProofRetained=True,originalTestsAndPassiveReadersReexecuted=0,checkedGraphInputHashes=checked,finiteRelatedDisclosureReview=related)
    unchanged=copy.deepcopy(result)
    for key in ['disclosureCorrectionOf','correctedDisclosureFields','originalCoverageProofManifestSha256','originalSelectedProofRetained','originalTestsAndPassiveReadersReexecuted','checkedGraphInputHashes','finiteRelatedDisclosureReview']:unchanged.pop(key)
    unchanged['invocation']=old['invocation']
    for key in FIELDS:unchanged[key]=old[key]
    assert unchanged==old
    verify(old['invocation'])
    verify(invocation);OUT.mkdir()
    for name,pin in old['xmlHashes'].items():
        source=data.BASE/OLD[0]/name;assert data.sha(source.read_bytes())==pin
        shutil.copyfile(source,OUT/name);assert data.sha((OUT/name).read_bytes())==pin
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
