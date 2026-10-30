"""Independently verify resource postv2 optional-trace shape and unchanged real Music proof."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG14822-resource-dom-post-v2-independent-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only tool independent proof')
    old=data.read_checked(data.BASE/'PG14792-music-hierarchy-template-six-post-v1/manifest.json','056734806be65ff09bb99d5636ab02649ff25e9045e067e7871104ce568b2447')
    new=data.read_checked(data.BASE/'PG14820-music-existing-resource-post-v2/manifest.json','aca238ae4558482138cbf3ea284a16952d33e3ca5361d93af37fa9f5fc26b516')
    checks=data.read_checked(data.BASE/'PG14818-resource-dom-post-v2-tool-qualification-v1/manifest.json','8b030bbf959802a473d167b8782da191c66648c21feea77a3d23e64766a34966')
    require(all(v['actualExit']==0 and v['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [old,new,checks]),'same source genuine evidence')
    expected={k:v for k,v in old.items() if k!='invocation'}
    def contract(value):
        require(json.dumps({k:v for k,v in value.items() if k!='invocation'},sort_keys=True)==json.dumps(expected,sort_keys=True),'all prior actual substantive values exactly equal')
    contract(new)
    require(checks['profileNegativeVectors']==21 and checks['noTraceProfilePositive'] is True and checks['duplicateMetadataCardinalities']==[1,2,8] and checks['toolChecks']==26 and checks['productTestsExecuted']==0 and checks['postSha256']=='aca238ae4558482138cbf3ea284a16952d33e3ca5361d93af37fa9f5fc26b516','actual21 profile negatives/three cardinalities/two positives')
    files={**old['xmlHashes'],'PT-SCR-071.txt':old['ownedSyntheticTrace']['sha256']}
    for name,pin in files.items():
        require(data.sha((data.BASE/'PG14792-music-hierarchy-template-six-post-v1'/name).read_bytes())==data.sha((data.BASE/'PG14820-music-existing-resource-post-v2'/name).read_bytes())==pin,'all returned XML and original public trace bytes equal')
    labels=[]
    for label,key,value in [('source','source','OLD'),('case-count','tests',8),('subset','cases',new['cases'][:-1]),('Main-credit','javaSourceProgramsQualified',4),('Java-coverage','javaCounterCoverageClaimed',True),('resource-coverage','resourceCounterCoverageClaimed',True),('Browser','actualBrowserActions',1),('original-env','reportedEnvironment',{}),('resources','reviewedResourceHashes',{}),('repeat','productTestsReexecutedByPost',6),('formal','formalUpdated',True),('acceptance','newAccepted',1),('effort','effortPercent',25)]:
        bad=copy.deepcopy(new);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false shared tool proof accepted '+label)
    for v in [old,new,checks]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=new['source'],invocation=invocation,sharedMusicPostSha256='aca238ae4558482138cbf3ea284a16952d33e3ca5361d93af37fa9f5fc26b516',toolQualificationSha256='8b030bbf959802a473d167b8782da191c66648c21feea77a3d23e64766a34966',allSubstantivePriorReceiptValuesEqual=True,profileNegativeVectors=21,noTraceProfilePositive=True,duplicateMetadataCardinalities=[1,2,8],toolChecks=26,independentNegativeVectors=len(labels),negativeLabels=labels,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
