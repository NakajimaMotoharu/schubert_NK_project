"""Independent no-replay proof of singleton metadata repair and unchanged existing8 semantics."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG14708-pure-post-minimum-cardinality-independent-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent tool proof')
    selftest=data.read_checked(data.BASE/'PG14706-pure-post-minimum-cardinality-selftest-v1/manifest.json','b90563ce834bd74c303e4f24c048882afdf40bd051b0f7a0825281ebd19e9a12')
    new=data.read_checked(data.ROOT/selftest['reanalysisPostManifest'],selftest['reanalysisPostSha256']);old=data.read_checked(data.BASE/'PG14704-backup-manifest-values-eight-post-v1/manifest.json','f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e')
    require(selftest['actualExit']==new['actualExit']==old['actualExit']==0 and selftest['pureMetadataCardinalities']==[1,2,8] and selftest['toolMetadataPositiveCases']==selftest['toolMetadataNegativeCases']==3,'actual minimum/multiple metadata checks, not Product PT')
    role_fields={'invocation','stages','profile','currentSourceExistingExecReanalyzed','originalTestsCountedElsewhere'}
    def contract(v):
        require(wire({k:x for k,x in v.items() if k not in role_fields})==wire({k:x for k,x in old.items() if k not in role_fields}),'all non-run-location semantic fields equal original post')
        require(v['currentSourceExistingExecReanalyzed'] is v['originalTestsCountedElsewhere'] is True and type(v['newProductExecutions']) is int and v['newProductExecutions']==0,'post-only accounting')
        require({k:x for k,x in v['profile'].items() if k not in ['postFolder','originalTestsAlreadyCounted']}=={k:x for k,x in old['profile'].items() if k not in ['postFolder','originalTestsAlreadyCounted']} and v['profile']['originalTestsAlreadyCounted'] is True,'same byte/scope profile, reanalysis role only')
        require(len(v['stages'])==2 and all(s['actualExit']==0 and s['timedOut'] is False for s in v['stages']),'genuine own CRC/counter diagnostics')
    contract(new);labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('methods',lambda v:v.update(tests=16)),('new-exec',lambda v:v.update(newProductExecutions=1)),('role',lambda v:v.update(originalTestsCountedElsewhere=False)),('closure',lambda v:v.update(completeSourceUnitClosure={})),('expected-as-measured',lambda v:v.update(executable={})),('old-transfer',lambda v:v.update(oldCoverageTransferred=True)),('XML',lambda v:v.update(xmlHashes={})),('scope',lambda v:v['profile'].update(kind='NATIVE')),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][0].update(timedOut=True)),('environment',lambda v:v.update(reportedEnvironment={}))]:
        bad=copy.deepcopy(new);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false repaired tool accepted '+label)
    consumers={}
    for folder,pin,count in [('PG14670-shared-pure-existing-question-eight-post-v1','d770e3ef1b510c254fd108593621002e7bd05bc15db77d02cf53fbb2466d1770',8),('PG14678-batch-cleanup-pure-five-post-v1','b5a30fe1a983ec6dc556b5af6c92c28bf436f528aedfa4e6e22b2e4ae4a1c61c',5),('PG14692-batch-run-diagnostic-three-post-v1','bae915b076e780950e98f2fbc99f6a086f921a76f42a94b596247cf036fd2c73',3),('PG14698-batch-cleanup-step-ten-post-v1','854da25a8435d5be7f31f2704e23597fb18c84e22c863d91099c36998475f4b7',10),('PG14704-backup-manifest-values-eight-post-v1','f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e',8)]:
        value=data.read_checked(data.BASE/folder/'manifest.json',pin);require(value['actualExit']==0 and len(value['cases'])==value['tests']==count and count>=2,'prior consumer not affected, no rerun')
        consumers[folder]=dict(sha256=pin,actualOriginalMethodCount=count,status='NOT_APPLICABLE_CARDINALITY_AT_LEAST_TWO',reexecuted=False)
    for v in [selftest,new,old]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=new['source'],invocation=invocation,bug='BUG-2109',ykt='YKT-1856',selftestSha256='b90563ce834bd74c303e4f24c048882afdf40bd051b0f7a0825281ebd19e9a12',reanalysisPostSha256=selftest['reanalysisPostSha256'],priorPostSha256='f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e',allNonRunLocationSemanticFieldsEqual=True,metadataPositive=3,metadataNegative=3,semanticNegativeVectors=len(labels),negativeLabels=labels,priorConsumers=consumers,existingProductMethodsReferenced=8,newProductMethods=0,newProductExecutions=0,sourceChanged=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
