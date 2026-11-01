"""Independent code-free/annotation/source boundaries; no analyzer or Product replay."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST='6eb6c989f53530b4e6eb3d991c31561809aa0066b6600e08e5299713e9569cb7'
DIAG='04763edb92a176b5c043b191af2266e281947590805c17cbf8d264e0c7b1b04d'
OUT=data.BASE/'PG17856-codefree-definitions-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only metadata')
    p=data.read_checked(data.BASE/'PG17854-codefree-official-passive54-recovery-v3/manifest.json',POST)
    d=data.read_checked(data.BASE/'PG17842-codefree-main-diagnosis-v1/manifest.json',DIAG)
    measured={u['sourceOuter']:u for path,u in d['newCodefreeCandidates'].items() if not path.endswith('/package-info.java')}
    annotations={path:u for path,u in d['newCodefreeCandidates'].items() if path.endswith('/package-info.java')}
    require(len(measured)==17 and len(annotations)==37,'source kind, not 54 programs')
    expected_physical={n:h for u in measured.values() for n,h in u['physical'].items()}
    expected_all={n:h for u in d['newCodefreeCandidates'].values() for n,h in u['physical'].items()}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['diagnosisSha256']==DIAG,'genuine source and diagnostic')
        require(v['recoveredAnalyzerStage']['actualExit']==0 and v['recoveredAnalyzerStage']['timedOut'] is False and v['outputSchemaNegativeVectors']==8,'successful one original analyzer and exact footer')
        require(v['allInputPhysicalClasses']==expected_all and v['physicalClasses']==expected_physical and set(v['metadataClasses'])==set(expected_physical) and len(v['metadataClasses'])==17,'54 input classes kept,17 modeled classes')
        require(set(v['fullSourceUnits'])==set(measured) and v['interfaceZeroCounterSourceCount']==17 and v['officialPackageInfoDefinitionCount']==37,'only17 measured Source scopes')
        for n,u in measured.items():
            row=v['fullSourceUnits'][n]
            require(row==dict(path=u['path'] if 'path' in u else next(path for path,x in d['newCodefreeCandidates'].items() if x['sourceOuter']==n),sourceSha256=u['sourceSha256'],physical=sorted(u['physical']),totals={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']},metadataOnly=True,four100=False,branchNaturallyZero=False,threeCounter100=False),'whole Code-free scope with natural zero, never four100')
        require(set(v['officialPackageInfoDefinitions'])==set(annotations),'all37 definition paths')
        for path,u in annotations.items():
            require(v['officialPackageInfoDefinitions'][path]==dict(sourceSha256=u['sourceSha256'],physical=u['physical'],flags=5632,fields=0,methods=[],modelCounterStatus='OFFICIAL_PACKAGE_INFO_FILTERED_NO_CODE_NO_RUNTIME_COUNTERS',coverageCountersMeasured=False,productCodeExecuted=False),'inert annotation bytes, no runtime coverage claim')
        require(v['officialFiltersUnchanged'] is v['allFourCounterTotalsZeroVerified'] is True and v['executableCounterExclusions']==[],'no custom exclusion/filter')
        require(v['applicableCodeCrcClasses']==0 and v['noCodeCrcQualification']=='NOT_APPLICABLE_NO_EXECUTABLE_CODE_BYTE_IDENTITY_BY_NORMAL_JAR_SNAPSHOT_SHA','no imagined execution CRC')
        require(v['tests']==v['suites']==v['newTestIds']==v['productTestsExecuted']==v['productTestsReexecuted']==v['compilerCommandsIssued']==v['passiveAnalyzerJvmCommandsIssuedByRecovery']==v['actualVmActions']==v['actualDatabaseActions']==v['actualNetworkActions']==0 and v['productClassesLoaded'] is False and v['existingSuccessfulAnalyzerJvmStagesReused']==1,'only saved analyzer receipt, no PT or rerun')
        require(v['newAccepted']==0 and v['formalUpdated'] is False and v['effortPercent'] is None,'no formal effort/acceptance')
    contract(p);negative=[]
    vectors=[('source','OLD'),('actualExit',True),('diagnosisSha256','0'*64),('allInputPhysicalClasses',{}),('physicalClasses',{}),('metadataClasses',['unknown']*17),('fullSourceUnits',{}),('interfaceZeroCounterSourceCount',54),('officialPackageInfoDefinitionCount',0),('officialPackageInfoDefinitions',{}),('officialFiltersUnchanged',False),('executableCounterExclusions',['x']),('applicableCodeCrcClasses',17),('noCodeCrcQualification','ALL54_EXECUTED'),('tests',54),('productTestsExecuted',1),('passiveAnalyzerJvmCommandsIssuedByRecovery',1),('productClassesLoaded',True),('existingSuccessfulAnalyzerJvmStagesReused',0),('newAccepted',17),('formalUpdated',True),('effortPercent',100),('outputSchemaNegativeVectors',0)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value;require(bad!=p,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false NoCode metadata '+key)
    first=next(iter(p['fullSourceUnits']))
    bad=copy.deepcopy(p);bad['fullSourceUnits'][first]['four100']=True
    try:contract(bad)
    except ValueError:negative.append('NoCode-as-four100')
    else:raise ValueError('zero-denominator percentage accepted')
    for path,u in d['newCodefreeCandidates'].items():require(data.sha((data.ROOT/path).read_bytes())==u['sourceSha256'],'actual same source bytes')
    verify(p['invocation']);verify(d['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST,diagnosisSha256=DIAG,semanticNegativeVectors=len(negative),negativeLabels=negative,interfaceSourceDefinitions=17,packageInfoDefinitions=37,independentDefinitionRows=54,executableProgramDelta=0,newPtPass=0,newFour100=0,allInputBytesRetained=True,productClassesLoaded=False,productTestsExecuted=0,analyzerJvmsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
