"""Independent shared-post semantic qualification using existing PT only, not Product replay."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG14672-shared-pure-post-independent-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent post')
    selftest=data.read_checked(data.BASE/'PG14670-shared-pure-post-profile-selftest-v1/manifest.json','5631263f0523cdd80bd7fdfe6ddd71731a0b35a4b02d38ec022532c528e48c06')
    current=data.read_checked(data.ROOT/selftest['reanalysisPostManifest'],selftest['reanalysisPostSha256'])
    old=data.read_checked(data.BASE/'PG14660-question-plain-whole-eight-post-v1/manifest.json','f3db377596bf97bb831e6e538a46e3a62bc383eaad88533e4d14f120f3e9c79f')
    require(selftest['actualExit']==current['actualExit']==old['actualExit']==0 and selftest['profileNegativeVectors']==18,'actual tool qualification')
    require(selftest['newProductMethods']==selftest['newProductExecutions']==0 and selftest['originalMethodsAlreadyCounted']==8,'no new PT credit')
    fields=['source','originalManifestSha256','normalManifestSha256','staticPostManifestSha256','tests','suites','failures','errors','skipped','reruns','newTestIds','newAccepted','sourceChanged','targetSourceUnits','completeSourceUnitClosure','sourcePhysicalInventory','completeSourceCoverageMeasured','fullSourceUnits','targetUnitFour100','strictFour100GateExit','missedLines','cases','xmlHashes','execSha256','singleSession','sessionIdentity','crcMismatch','physicalClasses','executable','totals','owners','metadataNegativeVectors','negativeLabels','reportedEnvironment','manualCounterExclusions','officialGeneratedFiltersUnchanged','whole451Accepted','wholeF03Accepted','formalUpdated','effortPercent']
    def contract(value):
        require(all(wire(value[k])==wire(old[k]) for k in fields),'every original semantic value unchanged')
        require(value['profile']==selftest['profile'] and value['originalTestsCountedElsewhere'] is value['currentSourceExistingExecReanalyzed'] is True and type(value['newProductExecutions']) is int and value['newProductExecutions']==0,'explicit reanalysis accounting')
        require(value['profile']['kind']=='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES' and value['onlyReviewedPureValueSuites'] is True,'limited common shape only')
        require(value['productTestsReexecutedByPost']==0 and not value['priorProductResultsReused'] and not value['oldCoverageTransferred'],'no replay or old-source union')
    contract(current)
    labels=[]
    vectors=[('source',lambda v:v.update(source='0'*40)),('methods-as-new',lambda v:v.update(tests=16)),('erased-gap',lambda v:v['totals']['LINE'].update(missed=0)),('closure-erased',lambda v:v.update(completeSourceUnitClosure={})),('XML-forged',lambda v:v.update(xmlHashes={})),('exec-forged',lambda v:v.update(execSha256='0'*64)),('environment-substituted',lambda v:v.update(reportedEnvironment={'currentHost':'not original'})),('failed',lambda v:v.update(failures=1)),('formal',lambda v:v.update(formalUpdated=True)),('bool-exec',lambda v:v.update(newProductExecutions=False)),('already-counted-erased',lambda v:v.update(originalTestsCountedElsewhere=False)),('scope-broadened',lambda v:v['profile'].update(kind='LIVE_RESOURCE'))]
    for label,change in vectors:
        wrong=copy.deepcopy(current);change(wrong)
        try:contract(wrong)
        except ValueError:labels.append(label)
        else:raise ValueError('false shared post accepted')
    require(len(labels)==12,'all nonvacuous semantic negatives')
    for m in [selftest,current,old]:verify(m['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=current['source'],invocation=invocation,selftestSha256='5631263f0523cdd80bd7fdfe6ddd71731a0b35a4b02d38ec022532c528e48c06',sharedPostSha256=selftest['reanalysisPostSha256'],originalPostSha256='f3db377596bf97bb831e6e538a46e3a62bc383eaad88533e4d14f120f3e9c79f',profileNegativeVectors=18,semanticNegativeVectors=len(labels),negativeLabels=labels,equalSemanticFields=fields,existingProductMethodsReferenced=8,newProductMethods=0,newProductExecutions=0,sourceChanged=False,gapRetained=dict(LINE=15,METHOD=1,BRANCH=6),newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None,toolQualifiedShape='PURE_WHOLE_NO_FIXTURES_NO_METADATA_CLASSES_BASELINE_OWNER_ONLY_NOT_DYNAMIC_PERMISSION'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
