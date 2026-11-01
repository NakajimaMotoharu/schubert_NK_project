"""Independent metadata validation of five public operator-source references only."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG18402-g07-public-operator-source-post-v1'
PIN='7c9eb1697ec0c7a6514a820bbb5dbb7b35f788688f1e38a5c64860e315fbaaf4'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m=data.read_checked(data.BASE/'PG18400-g07-public-operator-source-v1/manifest.json',PIN)
    rows=data.read_checked(data.BASE/'PG18400-g07-public-operator-source-v1/source-witnesses.json',m['sourceWitnessesSha256'])
    inventory=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/inventory.json','f14aadb1a1e2f5d6a435ef53e701f315a9f116c29ae4c6a426ff221c7a9e698d')
    by={v['path']:v for v in inventory['rows']}
    expected=[]
    tokens=['-javaagent:','sessionid=','destfile=','org.jacoco','ExecutionDataWriter','new RuntimeData','setSessionId']
    for number,lines in [(383,177),(384,162),(385,162),(386,162),(387,319)]:
        name='tools/quality/vm/050_s1/Pg'+str(number)+'TrustedDeployment.java'
        path=data.ROOT/name;require(not path.is_symlink(),'regular exact source')
        content=path.read_bytes();text=content.decode('utf-8')
        require(data.sha(content)==by[name]['sha256'],'original inventory source hash')
        require(len(text.splitlines())==lines and 'public final class '+path.stem+' {' in text,'independent declaration/count')
        matches={token:[i for i,line in enumerate(text.splitlines(),1) if token in line] for token in tokens}
        require(not any(matches.values()),'bounded literal scope only')
        expected.append(dict(path=name,sha256=by[name]['sha256'],gitObject=by[name]['gitObject'],bytes=len(content),lines=lines,declaredPublicClass=path.stem,literalConfigurationLines=matches,role='TRUSTED_OPERATOR_SOURCE_ONLY_NOT_EXECUTED',referencedPathsOpened=False,wholeTransitiveClosureReviewed=False))
    require(wire(rows)==wire(expected),'all safe rows exact, no hidden context/unknown field')
    expected_fields=dict(actualExit=0,source=SOURCE,analysisSourceOnly=True,historicalScanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',scanManifestSha256='f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739',inventorySha256='f14aadb1a1e2f5d6a435ef53e701f315a9f116c29ae4c6a426ff221c7a9e698d',sourceWitnessesSha256=data.sha((data.BASE/'PG18400-g07-public-operator-source-v1/source-witnesses.json').read_bytes()),sourceCount=5,sourceLines=982,directLiteralConfigurationMatches=0,result='NO_DIRECT_LITERAL_CONFIGURATION_IN_FIXED_READ_SET',generatorProvenanceQualified=False,environmentAndTransitiveClosureQualified=False,sessionAndClassProvenanceQualified=False,missingEvidence='ACTUAL_SOURCE_BOUND_AGENT_GENERATOR_CONFIGURATION_NOT_PROVEN',binaryClosedByThisScope=0,remainingBinaryOrContainerGate=22,remainingUnclassified=4493,actualSecretCount=None,publicOperatorSourcesOnly=True,operatorScriptsExecuted=False,operatorClassesCompiledOrLoaded=False,productTestsExecuted=0,coverageExecuted=False,scannerExecuted=False,execFormatsReparsed=False,historyExpanded=False,privateRawRead=False,referencedPathsOpened=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,oldNativeResultsTransferred=False,wholeG07Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    def contract(v):
        require(set(v)==set(expected_fields)|{'invocation','environment'},'fixed safe manifest schema')
        require(wire({k:v[k] for k in expected_fields})==wire(expected_fields),'no invented producer, secret, test, gate or side effect')
    contract(m);labels=[]
    for key,value in expected_fields.items():
        wrong=not value if type(value) is bool else 1 if value is None or value==0 else 0 if type(value) is int else 'UNQUALIFIED'
        bad=copy.deepcopy(m);bad[key]=wrong
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false metadata accepted '+key)
    for field,value in [('referencedPathsOpened',True),('wholeTransitiveClosureReviewed',True),('role','GENERATOR'),('literalConfigurationLines',{}),('sha256','0'*64),('unexpectedRaw','NOT_RETAINED')]:
        bad=copy.deepcopy(rows);bad[0][field]=value
        require(wire(bad)!=wire(expected),'reject altered safe source row')
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,witnessRowsSha256=m['sourceWitnessesSha256'],metadataNegativeVectors=len(labels),negativeLabels=labels,safeRowNegativeVectors=6,sourceRows=5,sourceLines=982,scope='BOUNDED_LITERAL_SOURCE_READ_ONLY_NOT_GENERATOR_PROVENANCE',generatorProvenanceQualified=False,binaryClosedByThisScope=0,remainingBinaryOrContainerGate=22,remainingUnclassified=4493,actualSecretCount=None,productTestsExecuted=0,operatorClassesCompiledOrLoaded=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,privateRawRead=False,historyExpanded=False,scannerExecuted=False,execFormatsReparsed=False,oldNativeResultsTransferred=False,newAccepted=0,formalUpdated=False,wholeG07Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(metadataNegativeVectors=len(labels),safeRowNegativeVectors=6)))
if __name__=='__main__':main()
