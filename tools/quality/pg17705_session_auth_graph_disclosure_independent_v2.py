"""Independent closed-delta disclosure correction; reuse completed CRC/oracle proof without replay."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_POST=('PG17702-session-auth-graph-eight-post-v1','fd3c5636081f8d5ffcf3209e783c724bd161f5bfb422c23ee97641b83e377b1b')
OLD_INDEPENDENT=('PG17704-session-auth-graph-eight-independent-v1','e8fe7b47ac49c3a5128d1150e40c837c32693b3ce0d4d34a5b155562429adb16')
POST=('PG17703-session-auth-graph-disclosure-post-v2','9edb754483f74fb5f665cb314a346b4f5f6932240ea1a8b7392d1a1112aea10c')
OUT=data.BASE/'PG17705-session-auth-graph-disclosure-independent-v2'
FIELDS=['publicSyntheticUuidFixture','publicFixedUuidFixtureOnly']
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,q,p=[read(v) for v in [OLD_POST,OLD_INDEPENDENT,POST]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,q,p]) and q['postSha256']==OLD_POST[1] and q['originalRawSha256']==p['originalManifestSha256'],'same actual source/run')
    require((q['semanticNegativeVectors'],q['independentOracleVectors'],len(q['testCrcIdentityClasses']))==(28,8,4),'completed original oracle/CRC qualification, not rerun')
    require(p['disclosureCorrectionOf']==list(OLD_POST) and p['correctedDisclosureFields']==FIELDS and p['originalCoverageProofManifestSha256']==OLD_POST[1] and p['originalSelectedProofRetained'] is True and p['originalTestsAndPassiveReadersReexecuted']==0,'closed correction provenance')
    keys=['disclosureCorrectionOf','correctedDisclosureFields','originalCoverageProofManifestSha256','originalSelectedProofRetained','originalTestsAndPassiveReadersReexecuted','checkedGraphInputHashes','finiteRelatedDisclosureReview']
    expected=copy.deepcopy(old);expected.update(invocation=p['invocation'],**{k:False for k in FIELDS})
    expected.update({k:p[k] for k in keys})
    def contract(v):
        require(v==expected and all(v[k] is False for k in FIELDS),'exact two-field disclosure change, no core qualification changes')
        require(v['correctedDisclosureFields']==FIELDS and v['disclosureCorrectionOf']==list(OLD_POST) and v['originalTestsAndPassiveReadersReexecuted']==0,'exact history and no replay')
    contract(p)
    rows=p['finiteRelatedDisclosureReview'];require(len(rows)==3 and len({v['post'] for v in rows})==3 and all(v['requiresChange'] is False for v in rows),'all finite related profiles non-applicable')
    for row in rows:
        actual=read((row['post'],row['postSha256']));path=data.ROOT/row['originalFixture']
        require(actual['source']==SOURCE and all(actual[k] is True for k in FIELDS) and 'UUID' in path.read_text() and data.sha(path.read_bytes())==row['fixtureSha256'],'real original fixed UUID fixture, not inferred from profile name')
    for path,pin in p['checkedGraphInputHashes'].items():
        require(data.sha((data.ROOT/path).read_bytes())==pin and 'UUID' not in (data.ROOT/path).read_text(),'all six graph inputs UUID-free')
    require(len(p['checkedGraphInputHashes'])==6,'four whole Test and two whole Main')
    labels=[]
    vectors=[('publicSyntheticUuidFixture',True),('publicFixedUuidFixtureOnly',True),('source','old'),('actualExit',1),('totals',{}),('execSha256','0'*64),('originalManifestSha256','0'*64),('xmlHashes',{}),('physicalClasses',{}),('disclosureCorrectionOf',[]),('correctedDisclosureFields',[]),('originalTestsAndPassiveReadersReexecuted',1)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false disclosure accepted '+key)
    result=copy.deepcopy(q);result.update(invocation=invocation,postSha256=POST[1],inheritedIndependentQualification=list(OLD_INDEPENDENT),inheritedOracleAndCrcProofNotReexecuted=True,disclosureOriginalPost=list(OLD_POST),disclosureNegativeVectors=len(labels),disclosureNegativeLabels=labels,finiteRelatedProfilesReviewed=3)
    require(result['originalRawSha256']==q['originalRawSha256'] and result['originalTestSourceHashes']==q['originalTestSourceHashes'] and result['testCrcIdentityClasses']==q['testCrcIdentityClasses'],'same original proof core')
    for v in [old,q,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
