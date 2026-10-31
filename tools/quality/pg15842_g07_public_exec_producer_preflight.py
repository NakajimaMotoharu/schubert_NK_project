"""WBS-G07/3023: exact public manifest/exec references; no producer-code inference or operation."""
import json
import platform
import re
from pathlib import PurePosixPath
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG15842-g07-public-exec-producer-preflight-v1'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SCAN_SHA='f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739'
INV_SHA='f14aadb1a1e2f5d6a435ef53e701f315a9f116c29ae4c6a426ff221c7a9e698d'
PREFIX='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'
EXPECTED={
 'PG383-native-deployment':('53d427daa039fdc07639fd37212aa69e58140c06c05db83f1620f57508f2264a','741a02f7b35688f2dc8bcdf480a5c0c2874e1bd9'),
 'PG384-native-deployment':('4b80d2e9115bcd8a27c089ff0de9074b833691aa88621c31926e796bcf03e048','ba126a25b64ec120845a929fb94f4144bd7790be'),
 'PG385-native-deployment':('037b65cf95afa6bd68242761c77908b99eec58a9c93c2912403c70dea3e5721f','a6b5c7c8b021c4b391b3af90572eab5d0eac8ab1'),
 'PG386-native-backup-failure':('c76c0c050544a06fa2acf8ed2cfbad0dcef9f1a2254fa48c62520a925c994c69','d49a3a9fb0876ccf07e3e968df9e961bce215397'),
 'PG387-native-normal-resume':('e34d282aa7c345bca237c7cb1bbf7c509c85a3fc6f52c66ed8f0533e62b59bc7','7ba352d6f0b7c08c371e838683fb6c2ba58725af')}
SOURCES={
 'tools/quality/vm/050_s1/NativeCoverage.java':'5685404757c2092202c6b1cc78984ed91a600641b1b345be7e863070c04cc862',
 'tools/quality/vm/050_s1/pg383_deploy.sh':'ae35fa9ceeb252d9c39136f0e46dc82ae64e5cf2587f4cfea30672c7000191ee'}

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    scan=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/manifest.json',SCAN_SHA)
    inv=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/inventory.json',INV_SHA);by={r['path']:r for r in inv['rows']}
    prior=data.read_checked(data.BASE/'PG15838-g07-public-exec-format-post-v1/manifest.json','a014f3e734bdb2c966dfc6887522363c034f78c165a0b206e4a644c0148f0228')
    require(scan['source']==data.HISTORICAL and scan['contentCommit']==data.CONTENT and prior['actualExit']==0 and prior['formatInspectedFiles']==10 and prior['binaryReviewCompleted'] is False,'fixed prior format evidence only')
    targets={p:by[p] for p in scan['binaryOrContainerLimitedPaths'] if p.endswith('.exec')}
    require(len(targets)==10,'ten exact original exec inputs')
    witnesses=[];covered=set()
    for folder,(pin,source) in EXPECTED.items():
        name=PREFIX+folder+'/manifest.json';path=data.ROOT/name
        require(name in by and by[name]['sha256']==pin and path.resolve()==path and not path.is_symlink(),'fixed public manifest identity')
        value=data.read_checked(path,pin)
        require(value['sourceCommit']==source and re.fullmatch('[0-9a-f]{40}',source) is not None and isinstance(value['files'],list),'historical source/manifest file schema')
        selected=[p for p in targets if p.startswith(PREFIX+folder+'/')]
        bindings=[]
        for target in selected:
            leaf=PurePosixPath(target).name
            refs=[r for r in value['files'] if isinstance(r,dict) and isinstance(r.get('path'),str) and PurePosixPath(r['path']).name==leaf]
            require(len(refs)==1 and refs[0]['sha256']==targets[target]['sha256'],'exact original manifest/exec reference')
            require(data.sha((data.ROOT/target).read_bytes())==targets[target]['sha256'],'original public input preserved, no decoder replay')
            bindings.append(dict(path=target,sha256=targets[target]['sha256'],gitObject=targets[target]['gitObject'],producerManifestReferenceMatched=True))
            covered.add(target)
        witnesses.append(dict(manifest=name,manifestSha256=pin,sourceCommit=source,gitObject=by[name]['gitObject'],execBindings=bindings,coverageDeclarationKeys=sorted(value.get('coverage',{})),declarationDoesNotProveGeneratorConfiguration=True,sessionGeneratorConfigurationQualified=False,classNameOriginQualified=False,currentNativeAccepted=False))
    require(covered==set(targets) and sum(len(w['execBindings']) for w in witnesses)==10,'all ten exact producer references')
    source_rows=[]
    for name,pin in SOURCES.items():
        path=data.ROOT/name
        require(name in by and by[name]['sha256']==pin and path.resolve()==path and not path.is_symlink() and data.sha(path.read_bytes())==pin,'exact old public source before interpretation')
        text=path.read_text()
        if name.endswith('.java'):
            require(all(v in text for v in ['new ExecFileLoader()','data.load(new File(args[i]))','new Analyzer(','not a formal collector or coverage waiver']) and all(v not in text for v in ['new RuntimeData','setSessionId','ExecutionDataWriter']),'reviewed consumer not a generator-code witness')
            role='EXEC_CONSUMER_UNION_DIAGNOSTIC_NOT_FIELD_GENERATOR'
        else:
            require(all(v in text for v in ['Pg383TrustedDeployment','javac','ssh -i','scp -i']) and 'RuntimeData' not in text and 'setSessionId' not in text,'operator dispatcher not generator source')
            role='OPERATOR_DISPATCH_SOURCE_ONLY_NOT_EXECUTED'
        source_rows.append(dict(path=name,sha256=pin,gitObject=by[name]['gitObject'],role=role,generatorImplementationQualified=False))
    require(all(data.sha((data.ROOT/w['manifest']).read_bytes())==w['manifestSha256'] for w in witnesses) and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in SOURCES.items()),'all source and public manifests preserved')
    verify(prior['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'producer-reference-witnesses.json',witnesses);data.write(OUT/'public-source-roles.json',source_rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,wbs='WBS-G07',historicalScanSource=data.HISTORICAL,contentCommit=data.CONTENT,scanManifestSha256=SCAN_SHA,inventorySha256=INV_SHA,priorFormatIndependentSha256='a014f3e734bdb2c966dfc6887522363c034f78c165a0b206e4a644c0148f0228',producerManifestCount=5,exactExecReferenceCount=10,publicSourceRoleCount=2,producerWitnessesSha256=data.sha((OUT/'producer-reference-witnesses.json').read_bytes()),sourceRolesSha256=data.sha((OUT/'public-source-roles.json').read_bytes()),os=dict(system=platform.system(),release=platform.release(),python=platform.python_version()),producerConfigurationLocatedInBoundReadSet=False,missingEvidence='SOURCE_BOUND_GENERATOR_AND_CONFIGURATION_WITNESS_NOT_ESTABLISHED_BY_DECLARATION_OR_CONSUMER',historicalSessionValuesOrHashesSaved=False,historicalClassNameValuesOrHashesSaved=False,execFormatsReparsed=False,productClassesLoaded=False,productMethodsInvoked=False,productTestsExecuted=0,operatorScriptsExecuted=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,privateRawRead=False,historyExpanded=False,scannerExecuted=False,oldNativeResultsTransferred=False,coverageExecUnion=False,remainingUnclassified=4493,remainingBinaryOrContainerGate=22,binaryReviewCompleted=False,sessionAndClassProvenanceQualified=False,actualSecretCount=None,whole451SecretGateAccepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,producerManifests=5,exactExecReferences=10,sourceRoles=2,generatorProvenanceQualified=False,wholeG07Accepted=False)))
if __name__=='__main__':main()
