"""Independent public producer-reference metadata verification, no Product or historical decoder replay."""
import copy
import json
import platform
from pathlib import PurePosixPath
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15842_g07_public_exec_producer_preflight as original

PIN='99485b46ac1d11d208902a32e56e4d14b5936f5f469b2c5f207737d8baf6182f'
OUT=data.BASE/'PG15844-g07-public-exec-producer-post-v1'
WKEYS={'manifest','manifestSha256','sourceCommit','gitObject','execBindings','coverageDeclarationKeys','declarationDoesNotProveGeneratorConfiguration','sessionGeneratorConfigurationQualified','classNameOriginQualified','currentNativeAccepted'}
BKEYS={'path','sha256','gitObject','producerManifestReferenceMatched'}
SKEYS={'path','sha256','gitObject','role','generatorImplementationQualified'}

def require(ok,message):
    if not ok:raise ValueError(message)

def assess(p,rows,roles,scan,inventory,manifests):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['historicalScanSource']==data.HISTORICAL and p['contentCommit']==data.CONTENT,'source domains')
    require((p['producerManifestCount'],p['exactExecReferenceCount'],p['publicSourceRoleCount'])==(5,10,2),'exact original witness counts')
    require(p['scanManifestSha256']==original.SCAN_SHA and p['inventorySha256']==original.INV_SHA and p['priorFormatIndependentSha256']=='a014f3e734bdb2c966dfc6887522363c034f78c165a0b206e4a644c0148f0228','fixed upstream proof')
    require(p['remainingUnclassified']==4493 and p['remainingBinaryOrContainerGate']==22 and p['actualSecretCount'] is p['effortPercent'] is None,'no false gate closure')
    for key in ['producerConfigurationLocatedInBoundReadSet','sessionAndClassProvenanceQualified','binaryReviewCompleted','whole451SecretGateAccepted','historicalSessionValuesOrHashesSaved','historicalClassNameValuesOrHashesSaved','execFormatsReparsed','operatorScriptsExecuted','historyExpanded','privateRawRead','productClassesLoaded','productMethodsInvoked','coverageExecUnion','oldNativeResultsTransferred','scannerExecuted','formalUpdated']:
        require(p[key] is False,'no operation or invented provenance: '+key)
    for key in ['productTestsExecuted','actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','newAccepted']:
        require(type(p[key]) is int and p[key]==0,'no actual target/acceptance: '+key)
    expected={path for path in scan['binaryOrContainerLimitedPaths'] if path.endswith('.exec')}
    require(len(rows)==5 and len({r['manifest'] for r in rows})==5,'distinct producer manifests')
    seen=[]
    for row in rows:
        require(set(row)==WKEYS,'safe manifest reference schema')
        folder=PurePosixPath(row['manifest']).parent.name
        require(folder in original.EXPECTED,'fixed original folder')
        pin,source=original.EXPECTED[folder]
        bound=inventory[row['manifest']]
        require((row['manifestSha256'],row['sourceCommit'],row['gitObject'])==(pin,source,bound['gitObject']) and bound['sha256']==pin,'original inventory/manifest identity')
        raw=manifests[row['manifest']]
        require(raw['sourceCommit']==source and sorted(raw.get('coverage',{}))==row['coverageDeclarationKeys'],'declaration keys only, not qualification')
        require(row['declarationDoesNotProveGeneratorConfiguration'] is True and all(row[k] is False for k in ['sessionGeneratorConfigurationQualified','classNameOriginQualified','currentNativeAccepted']),'no declaration escalation')
        for ref in row['execBindings']:
            require(set(ref)==BKEYS and ref['path'] in expected,'safe fixed exec references')
            item=inventory[ref['path']]
            require((ref['sha256'],ref['gitObject'])==(item['sha256'],item['gitObject']) and ref['producerManifestReferenceMatched'] is True,'exact inventory hash/object')
            matches=[v for v in raw['files'] if PurePosixPath(v['path']).name==PurePosixPath(ref['path']).name]
            require(len(matches)==1 and matches[0]['sha256']==ref['sha256'] and PurePosixPath(ref['path']).parent==PurePosixPath(row['manifest']).parent,'independent original reference join')
            seen.append(ref['path'])
    require(len(seen)==len(set(seen))==10 and set(seen)==expected,'all ten exactly once')
    require(len(roles)==2 and {r['path'] for r in roles}==set(original.SOURCES),'exact two source-only roles')
    declared={'tools/quality/vm/050_s1/NativeCoverage.java':'EXEC_CONSUMER_UNION_DIAGNOSTIC_NOT_FIELD_GENERATOR','tools/quality/vm/050_s1/pg383_deploy.sh':'OPERATOR_DISPATCH_SOURCE_ONLY_NOT_EXECUTED'}
    for row in roles:
        require(set(row)==SKEYS and row['sha256']==original.SOURCES[row['path']]==inventory[row['path']]['sha256'] and row['gitObject']==inventory[row['path']]['gitObject'],'exact public source schema/hash')
        require(row['role']==declared[row['path']] and row['generatorImplementationQualified'] is False,'consumer/dispatcher not generator')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(original.OUT/'manifest.json',PIN)
    rows=data.read_checked(original.OUT/'producer-reference-witnesses.json',p['producerWitnessesSha256'])
    roles=data.read_checked(original.OUT/'public-source-roles.json',p['sourceRolesSha256'])
    scan=data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/manifest.json',original.SCAN_SHA)
    inventory={v['path']:v for v in data.read_checked(data.BASE/'PG8968-public-blob-scan-v1/inventory.json',original.INV_SHA)['rows']}
    manifests={r['manifest']:data.read_checked(data.ROOT/r['manifest'],r['manifestSha256']) for r in rows}
    assess(p,rows,roles,scan,inventory,manifests)
    negatives=[]
    for key,value in [('producerManifestCount',4),('exactExecReferenceCount',9),('publicSourceRoleCount',1),('producerConfigurationLocatedInBoundReadSet',True),('sessionAndClassProvenanceQualified',True),('binaryReviewCompleted',True),('whole451SecretGateAccepted',True),('actualSecretCount',0),('remainingUnclassified',0),('remainingBinaryOrContainerGate',0),('productTestsExecuted',1),('newAccepted',False),('effortPercent',0),('operatorScriptsExecuted',True),('oldNativeResultsTransferred',True),('execFormatsReparsed',True)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad,rows,roles,scan,inventory,manifests)
        except ValueError:negatives.append(key)
        else:raise ValueError('unrejected false manifest: '+key)
    for label,mutate in [('duplicate-producer',lambda r,s:r.__setitem__(0,copy.deepcopy(r[1]))),('missing-exec',lambda r,s:r[0]['execBindings'].clear()),('wrong-exec-hash',lambda r,s:r[0]['execBindings'][0].update(sha256='0'*64)),('arbitrary-field',lambda r,s:r[0].update(historicalFieldValue='PUBLIC_SYNTHETIC_TOOL_LABEL')),('source-qualification',lambda r,s:s[0].update(generatorImplementationQualified=True)),('source-role-escalation',lambda r,s:s[0].update(role='GENERATOR'))]:
        badrows=copy.deepcopy(rows);badroles=copy.deepcopy(roles);mutate(badrows,badroles)
        try:assess(p,badrows,badroles,scan,inventory,manifests)
        except ValueError:negatives.append(label)
        else:raise ValueError('unrejected reference mutation: '+label)
    verify(p['invocation']);verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,parentManifestSha256=PIN,producerWitnessesSha256=p['producerWitnessesSha256'],sourceRolesSha256=p['sourceRolesSha256'],producerManifestCount=5,exactExecReferenceCount=10,publicSourceRoleCount=2,independentMetadataNegativeVectors=len(negatives),negativeLabels=negatives,producerProvenanceQualified=False,missingEvidence=p['missingEvidence'],binaryReviewCompleted=False,remainingUnclassified=4493,remainingBinaryOrContainerGate=22,actualSecretCount=None,whole451SecretGateAccepted=False,originalExecReparsed=False,operatorScriptsExecuted=False,productTestsExecuted=0,productClassesLoaded=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,privateRawRead=False,formalUpdated=False,newAccepted=0,effortPercent=None,python=platform.python_version()))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,independentMetadataNegativeVectors=len(negatives),producerProvenanceQualified=False)))
if __name__=='__main__':main()
