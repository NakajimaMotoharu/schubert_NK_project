"""Independent shared v2 one-case tool-only qualification; no Product replay or extra acceptance."""
import copy
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG15326-shared-pure-single-case-independent-v2'
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    tool=data.read_checked(data.BASE/'PG15324-shared-pure-single-case-tool-v2/manifest.json','c81ead2bae7c0ee38e805eaad1f7db4195662914af989dd740a4314dc5834244')
    current=data.read_checked(data.ROOT/tool['reanalysisPostManifest'],tool['reanalysisPostSha256'])
    original=data.read_checked(data.BASE/'PG15309-required-column-one-post-v2/manifest.json','e26d863768b8659de2840b77421fd2f675d66a5dd9418b91a1796e691853d632')
    require(tool['actualExit']==current['actualExit']==original['actualExit']==0 and tool['source']==current['source']==original['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c','same genuine current source')
    require(tool['caseCardinalityNegativeVectors']==6 and set(tool['negativeLabels'])=={a+'-'+str(n) for a in ['duplicate-append','missing-case'] for n in [1,11,16]},'all new minimum/multi-case negatives; not old replay')
    require(tool['priorProfileNegativeVectorsReused']==18 and tool['priorSemanticNegativeVectorsReused']==12 and tool['originalMethodsAlreadyCounted']==1,'old18/12 proof reused, existing method not new')
    fields=['source','originalManifestSha256','normalManifestSha256','tests','suites','failures','errors','skipped','cases','xmlHashes','execSha256','sessionIdentity','singleSession','crcMismatch','physicalClasses','sourcePhysicalInventory','completeSourceUnitClosure','fullSourceUnits','targetUnitFour100','strictFour100GateExit','missedLines','executable','totals','owners','metadataNegativeVectors','metadataClasses','manualCounterExclusions','officialGeneratedFiltersUnchanged','reportedEnvironment','newAccepted','formalUpdated','whole451Accepted','wholeF03Accepted','effortPercent','helperSourceProgramsNotAcceptedByTheseTargetCounters']
    require(current['negativeLabels']==['source','failed','duplicate','scope','union','formal','timeout','fixture'] and original['negativeLabels']==['source','failure','duplicate','scope','union','formal','timeout','fixture'],'same eight semantic vectors, label spelling distinguished')
    require(tool['reanalysisPostSha256']=='bc24f6102df70e30da145d9b88f7a6517160df51de5fec0e306cbe4b055cc0ab' and current['strictFour100GateExit']==0,'actual new tool post exact path/hash, not caller stdout first hash')
    profile=tool['profile'];require(profile['kind']=='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES' and profile['originalTestsAlreadyCounted'] is True and len(profile['sources'])==1,'unchanged closed pure shape')
    def contract(value):
        require(all(wire(value[k])==wire(original[k]) for k in fields),'all actual old/new semantics and typed counts identical')
        require(value['profile']==profile and value['originalTestsCountedElsewhere'] is value['currentSourceExistingExecReanalyzed'] is True and type(value['newProductExecutions']) is int and value['newProductExecutions']==0,'explicit already-counted existing exec')
        require(value['productTestsReexecutedByPost']==0 and value['newTestIds']==0 and value['sourceChanged'] is value['registryChanged'] is value['priorProductResultsReused'] is value['oldCoverageTransferred'] is False and value['onlyReviewedPureValueSuites'] is True,'no Source/replay/registry/quality scope expansion')
    contract(current);labels=[]
    for key,value in [('source','OLD'),('tests',2),('suites',2),('cases',[]),('execSha256','0'*64),('physicalClasses',{}),('fullSourceUnits',{}),('totals',{}),('owners',{}),('metadataNegativeVectors',7),('metadataClasses',['invented']),('manualCounterExclusions',['ctor']),('newAccepted',1),('formalUpdated',True),('whole451Accepted',True),('effortPercent',50),('newProductExecutions',1),('newProductExecutions',False),('newTestIds',1),('sourceChanged',True),('registryChanged',True),('originalTestsCountedElsewhere',False),('onlyReviewedPureValueSuites',False)]:
        bad=copy.deepcopy(current);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key+'-'+str(value))
        else:raise ValueError('false shared v2 qualification '+key)
    require(len(labels)==23,'all new actual semantic negatives')
    require(data.sha((data.ROOT/tool['libraryPath']).read_bytes())==tool['librarySha256'] and data.sha((data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v1.py').read_bytes())==tool['legacyLibrarySha256']=='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341','both library versions immutable')
    for row in tool['originalInputReferences']:
        m=data.read_checked(data.ROOT/row['path'],row['sha256']);require(m['actualExit']==0 and len(m['cases'])==row['actualCases'],'all original1/11/16 manifests unchanged');verify(m['begin']['invocation'])
    for stage in current['stages']:
        slot=Path(stage['cwd']);label='session-identity' if 'CoverageSessionIdentity' in stage['command'] else 'coverage-audit'
        require(stage['actualExit']==0 and not stage['timedOut'] and data.sha((slot/(label+'.stdout')).read_bytes())==stage['stdoutSha256'] and data.sha((slot/(label+'.stderr')).read_bytes())==stage['stderrSha256'],'actual passive post stages/hash, no Product')
    for m in [tool,current,original]:verify(m['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=current['source'],invocation=invocation,selftestSha256='c81ead2bae7c0ee38e805eaad1f7db4195662914af989dd740a4314dc5834244',sharedPostSha256=tool['reanalysisPostSha256'],originalPostSha256='e26d863768b8659de2840b77421fd2f675d66a5dd9418b91a1796e691853d632',legacyQualificationSha256=tool['legacyQualificationSha256'],caseCardinalityNegativeVectors=6,priorProfileNegativeVectorsReused=18,priorSemanticNegativeVectorsReused=12,semanticNegativeVectors=len(labels),negativeLabels=labels,equalSemanticFields=fields,existingProductMethodsReferenced=1,newProductMethods=0,newProductExecutions=0,sourceChanged=False,registryChanged=False,toolScope='PURE_WHOLE_NO_FIXTURE_NO_METADATA_BASELINE_ONLY_MINIMUM1_SUPPORTED_NOT_PERMISSION',newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
