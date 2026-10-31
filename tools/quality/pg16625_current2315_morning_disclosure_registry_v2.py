"""Attach one qualified disclosure erratum; no new cases, counters or Source proof replacements."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16624-current2315-morning-pure-registry-v1','49aa7ad41e263f4704cef011c8dcd0a91d52c8a591746ab4cf616ba36526f0d2')
PREV_POST=('PG16627-current2315-morning-pure-registry-post-v2','7f72d49a6a8305c973749393577e5b82c15a09b856b2201285a4affadebb64b0')
ERR=('PG16621-morning-public-uuid-disclosure-erratum-v1','1125f9dd89a79a3a2b58d8e045f69d20c7c89d2c968e7a26b81d7ed60e174bad')
KEY='a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424'
OUT=data.BASE/'PG16625-current2315-morning-disclosure-registry-v2'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,e=[read(v) for v in [PREV,PREV_POST,ERR]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,e]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and prior['chainNegativeVectors']==2,'qualified current whole33 metadata')
    require(e['originalPost'][1]==KEY and e['metadataNegativeVectors']==8 and e['effectiveDisclosure']['effectivePublicSyntheticUuidFixture'] is True and e['rawIdentifierValuesRecorded'] is False and e['originalQualificationAndCountersUnchanged'] is True,'qualified finite correction')
    require(KEY not in old['postDisclosureCorrections'],'one correction once')
    result=copy.deepcopy(old)
    result['postDisclosureCorrections'][KEY]=dict(bug='BUG2184',horizontal='YKT1931',manifest=str((data.BASE/ERR[0]/'manifest.json').relative_to(data.ROOT)),sha256=ERR[1],originalPostSha256=KEY,effectiveDisclosure=copy.deepcopy(e['effectiveDisclosure']),originalQualificationAndCountersUnchanged=True)
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),sourceProgramDelta=0,uniqueProductMethodDelta=0,lastUpdateKind='POST_DISCLOSURE_ERRATUM_ONLY_NO_CASE_OR_COUNTER_ADDITION')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','sourceProgramDelta','uniqueProductMethodDelta','lastUpdateKind','postDisclosureCorrections'}
    require(all(result[k]==v for k,v in old.items() if k not in changed) and all(result['postDisclosureCorrections'][k]==v for k,v in old['postDisclosureCorrections'].items()),'every original case/counter/Source proof/history/cost unchanged')
    for v in [old,prior,e]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
