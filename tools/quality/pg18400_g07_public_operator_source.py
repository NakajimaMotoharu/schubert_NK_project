"""Fixed public operator source metadata; never executes any operator or opens referenced paths."""
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG18400-g07-public-operator-source-v1'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SCAN_SHA='f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739'
INV_SHA='f14aadb1a1e2f5d6a435ef53e701f315a9f116c29ae4c6a426ff221c7a9e698d'
PINS={
 'tools/quality/vm/050_s1/Pg383TrustedDeployment.java':'3252f49bfdeab72ba2ca30e1404cd12e6a1e762fbc83c032eb9accef63ae1560',
 'tools/quality/vm/050_s1/Pg384TrustedDeployment.java':'c37ca6c907327cd3b15ac80381181945c7a2c9dee9fee15c151cb1fa0b475b32',
 'tools/quality/vm/050_s1/Pg385TrustedDeployment.java':'12d8e47e6ff6d8ff838d8c435fa6bf5cfdc75b8feead50dfa6a97e1a5288e835',
 'tools/quality/vm/050_s1/Pg386TrustedDeployment.java':'6b22e954534c3879c5da9623ba598d47abd75bc6186b8ae166bc8ba804b5d32e',
 'tools/quality/vm/050_s1/Pg387TrustedDeployment.java':'ec63768dd9e98c2140c209fe3c178ac4c94400d8b178a928e4de545298150d83'}
TOKENS=['-javaagent:','sessionid=','destfile=','org.jacoco','ExecutionDataWriter','new RuntimeData','setSessionId']
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    scan=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/manifest.json',SCAN_SHA)
    inventory=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/inventory.json',INV_SHA)
    require(scan['actualExit']==0 and scan['inventorySha256']==INV_SHA and scan['contentCommit']==data.CONTENT,'fixed historical scan')
    by={r['path']:r for r in inventory['rows']};rows=[]
    for name,pin in PINS.items():
        require(name in by and by[name]['sha256']==pin,'original bound public source')
        tracked=subprocess.check_output(['git','ls-files','--error-unmatch','--',name],cwd=data.ROOT,text=True)
        require(tracked.strip()==name,'tracked exact path')
        path=data.ROOT/name;require(not path.is_symlink() and path.is_file(),'regular source')
        blob=path.read_bytes();require(data.sha(blob)==pin,'original immutable bytes')
        text=blob.decode('utf-8');declared=path.stem
        require('public final class '+declared+' {' in text and 'public static void main(String[] args) throws Exception' in text,'public operator declaration')
        positions={token:[i for i,line in enumerate(text.splitlines(),1) if token in line] for token in TOKENS}
        require(all(not v for v in positions.values()),'not a directly configured agent generator in this read set')
        rows.append(dict(path=name,sha256=pin,gitObject=by[name]['gitObject'],bytes=len(blob),lines=len(text.splitlines()),declaredPublicClass=declared,literalConfigurationLines=positions,role='TRUSTED_OPERATOR_SOURCE_ONLY_NOT_EXECUTED',referencedPathsOpened=False,wholeTransitiveClosureReviewed=False))
    require(len(rows)==5 and sum(r['lines'] for r in rows)==982,'fixed exact read set')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'source-witnesses.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,analysisSourceOnly=True,historicalScanSource=data.HISTORICAL,contentCommit=data.CONTENT,invocation=invocation,scanManifestSha256=SCAN_SHA,inventorySha256=INV_SHA,sourceWitnessesSha256=data.sha((OUT/'source-witnesses.json').read_bytes()),sourceCount=5,sourceLines=982,directLiteralConfigurationMatches=0,result='NO_DIRECT_LITERAL_CONFIGURATION_IN_FIXED_READ_SET',generatorProvenanceQualified=False,environmentAndTransitiveClosureQualified=False,sessionAndClassProvenanceQualified=False,missingEvidence='ACTUAL_SOURCE_BOUND_AGENT_GENERATOR_CONFIGURATION_NOT_PROVEN',binaryClosedByThisScope=0,remainingBinaryOrContainerGate=22,remainingUnclassified=4493,actualSecretCount=None,publicOperatorSourcesOnly=True,operatorScriptsExecuted=False,operatorClassesCompiledOrLoaded=False,productTestsExecuted=0,coverageExecuted=False,scannerExecuted=False,execFormatsReparsed=False,historyExpanded=False,privateRawRead=False,referencedPathsOpened=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,oldNativeResultsTransferred=False,wholeG07Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,environment=dict(system=platform.system(),release=platform.release(),python=platform.python_version())))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
