"""Attach two independently qualified effect errata without changing any case/counter proof."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16625-current2315-morning-disclosure-registry-v2','02fad496c50898ffec03a3489b705a60277b87c7d939fbfd73d992939bca455d')
PREV_POST=('PG16629-current2315-morning-disclosure-registry-post-v1','8dc884efbccffad4785c6e50b9e6fb0b0d71875eb60c9adf35e7acb3e890dbbe')
ERR=('PG16634-effect-disclosure-family-eight-v1','736aaeb460a5e31a81465b0cb284331faeed6e7cb1bb182bb4a002fe31a4955b')
QUAL=('PG16636-effect-disclosure-family-eight-post-v1','841cf677b32ed7ac63c9159f8d407456e5a1d956273b0eb1697628d9b556cb67')
OUT=data.BASE/'PG16638-current2315-family-disclosure-registry-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,e,q=[read(v) for v in [PREV,PREV_POST,ERR,QUAL]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,e,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['parentManifestSha256']==ERR[1] and q['metadataNegativeVectors']==42 and q['unresolved']==0,'qualified current immutable family')
    result=copy.deepcopy(old)
    for key,row in e['corrections'].items():
        require(key not in result['postDisclosureCorrections'],'not duplicated')
        result['postDisclosureCorrections'][key]=dict(bug='BUG2184',horizontal='YKT1931',manifest=str((data.BASE/ERR[0]/'manifest.json').relative_to(data.ROOT)),sha256=ERR[1],originalPostSha256=key,effectiveDisclosure=copy.deepcopy(row['effectiveDisclosure']),originalQualificationAndCountersUnchanged=True)
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),sourceProgramDelta=0,uniqueProductMethodDelta=0,lastUpdateKind='POST_DISCLOSURE_ERRATUM_ONLY_NO_CASE_OR_COUNTER_ADDITION')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','sourceProgramDelta','uniqueProductMethodDelta','lastUpdateKind','postDisclosureCorrections'}
    require(all(result[k]==v for k,v in old.items() if k not in changed) and all(result['postDisclosureCorrections'][k]==v for k,v in old['postDisclosureCorrections'].items()),'all old case/counter/history/cost bytes semantically preserved')
    for v in [old,prior,e,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
