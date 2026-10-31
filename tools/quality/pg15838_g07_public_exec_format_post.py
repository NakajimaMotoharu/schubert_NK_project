"""Independent G07 public-format metadata post; no decoder/product/native replay or secret classification."""
import copy
import json
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15836_g07_public_exec_format as original
from public_jacoco_exec_format_v1 import COMMON

PIN='f8371195e95594877a815e32f19e86bef246376207b68f5c06ef5227781028d2'
OUT=data.BASE/'PG15838-g07-public-exec-format-post-v1'
RESULT_KEYS={'path','inputSha256','gitObject','bytes','python','official','allDeclaredBytesConsumed','sessionIdValuesOrHashesSaved','classNameValuesOrHashesSaved','provenanceQualified','secretGateAccepted'}
def require(ok,message):
    if not ok:raise ValueError(message)
def assess(p,rows,scan,inventory):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['historicalScanSource']==data.HISTORICAL and p['contentCommit']==data.CONTENT,'review/current and historical domains separate')
    require(p['scanManifestSha256']==original.SCAN[1] and p['inventorySha256']==original.INVENTORY_SHA and p['formatInspectedFiles']==10 and p['formatInspectedBytes']==155226,'fixed ten original public inputs')
    require((p['metadataPositiveVectors'],p['metadataNegativeVectors'],p['apiTypeNegativeVectors'])==(5,14,4) and len(p['stages'])==30,'all genuine metadata vectors/stages')
    require(p['formatEvidenceOnly'] is True and p['sessionAndClassProvenanceQualified'] is p['binaryReviewCompleted'] is p['whole451SecretGateAccepted'] is False and p['actualSecretCount'] is None,'format evidence not G07/privacy acceptance')
    require(p['remainingUnclassified']==4493 and p['remainingBinaryOrContainerGate']==22 and p['otherPngFilesUninspected']==12,'all unmet original gates retained')
    require(all(p[k] is False for k in ['inputFilesMutated','sessionIdValuesOrHashesSaved','classNameValuesOrHashesSaved','probeArraysSaved','productClassesLoaded','productMethodsInvoked','sourceRuntimeQualificationTransferred','coverageExecUnion','originalNativeReexecuted','scannerExecuted','historyExpanded','privateRawRead','formalUpdated']) and all(type(p[k]) is int and p[k]==0 for k in ['productTestsExecuted','actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions','additionalFalsePositives','newAccepted']) and p['effortPercent'] is None,'no target/value transfer/external action or false closure')
    expected={path for path in scan['binaryOrContainerLimitedPaths'] if path.endswith('.exec')}
    require(len(rows)==len(expected)==10 and len({r['path'] for r in rows})==10 and {r['path'] for r in rows}==expected,'exact original ten, no path substitution')
    for row in rows:
        require(set(row)==RESULT_KEYS,'aggregate-only result schema, no arbitrary value channel')
        bound=inventory[row['path']]
        require((row['inputSha256'],row['gitObject'],row['bytes'])==(bound['sha256'],bound['gitObject'],bound['bytes']),'fixed source/blob hash/size')
        require(set(row['python'])==set(COMMON)|{'unusedPaddingSetBits','consumedBytes'} and set(row['official'])==set(COMMON) and all(type(v) is int for d in [row['python'],row['official']] for v in d.values()),'only typed numeric format statistics')
        require(row['official']=={k:row['python'][k] for k in COMMON} and row['bytes']==row['python']['bytes']==row['python']['consumedBytes'],'two independent complete byte decodes')
        require(row['allDeclaredBytesConsumed'] is True and row['sessionIdValuesOrHashesSaved'] is row['classNameValuesOrHashesSaved'] is row['provenanceQualified'] is row['secretGateAccepted'] is False,'no value provenance or secret gate invented')
    require(sum(r['bytes'] for r in rows)==155226,'ten original total bytes')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(original.OUT/'manifest.json',PIN)
    rows=data.read_checked(original.OUT/'results.json',p['resultsSha256'])
    vectors=data.read_checked(original.OUT/'metadata-vectors.json',p['vectorsSha256'])
    scan=data.read_checked(data.BASE/original.SCAN[0]/'manifest.json',original.SCAN[1])
    all_rows=data.read_checked(data.BASE/original.SCAN[0]/'inventory.json',original.INVENTORY_SHA)['rows'];inventory={r['path']:r for r in all_rows}
    assess(p,rows,scan,inventory)
    own_classpath=str(original.SLOT/'classes')+':'+str(original.JAR)
    expected_inputs={str(data.ROOT/r['path']) for r in rows}
    stage=p['stages'][0];require(stage['actualExit']==0 and not stage['timedOut'] and stage['command'][0]==str(original.JDK/'javac') and '-Werror' in stage['command'] and '-proc:none' in stage['command'],'metadata-only javac0')
    for suffix in ['stdout','stderr']:
        require(data.sha((original.SLOT/('compile-format-helper.'+suffix)).read_bytes())==stage[suffix+'Sha256'],'actual own compiler output hashes')
    historical_commands=[]
    for stage in p['stages'][1:]:
        cmd=stage['command'];require(len(cmd)==5 and cmd[:4]==[str(original.JDK/'java'),'-cp',own_classpath,'PublicJacocoFormatMetadataV1'] and not stage['timedOut'],'no agent, target Jar/entrypoint/alternate command')
        path=Path(cmd[4])
        if str(path) in expected_inputs:
            require(stage['actualExit']==0,'original public parse actual0');historical_commands.append(str(path))
            label='historical-public-'+str(len(historical_commands)).zfill(2)
        else:
            require(path.is_relative_to(original.SLOT/'public-tool-fixtures') and stage['actualExit'] in (0,2),'only finite public metadata fixtures')
            label='vector-'+path.stem
        for suffix in ['stdout','stderr']:
            require(data.sha((original.SLOT/(label+'.'+suffix)).read_bytes())==stage[suffix+'Sha256'],'actual owned metadata step output hashes')
    require(len(historical_commands)==len(set(historical_commands))==10,'ten once-only historical metadata reads')
    cases=vectors['positiveAndNegative'];require(len(cases)==19 and len(vectors['typeNegativeLabels'])==len(set(vectors['typeNegativeLabels']))==4,'complete distinct self vectors')
    positives=[v for v in cases if 'expected' in v];negatives=[v for v in cases if 'expectedExit' in v]
    require(len(positives)==5 and len(negatives)==14 and all(v['expected']==v['actual'] and v['actualExit']==0 and v['official']=={k:v['expected'][k] for k in COMMON} for v in positives) and all(v['expectedExit']==v['actualExit']==2 for v in negatives),'expected tool rejection not product failure/PASS')
    by={v['label']:v for v in positives}
    require(by['ascii-metadata']['expected']['bytes']==58 and by['ascii-metadata']['expected']['hits']==3 and by['ascii-metadata']['expected']['probes']==9 and by['modified-utf-nul-and-surrogates']['expected']['sessionUnits']==4 and by['modified-utf-nul-and-surrogates']['expected']['asciiSessions']==0 and by['unused-padding-is-not-hidden']['expected']['unusedPaddingSetBits']==1,'independent literal size/bit/modified-UTF/padding vectors')
    require(by['unused-padding-is-not-hidden']['official']==by['ascii-metadata']['official'],'official reader ignores padding, extra Python bit diagnostic retained')
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in p['toolSourceHashes'].items()) and data.sha(original.JAR.read_bytes())==p['officialLibrarySha256']==original.JAR_SHA,'own tool/library bytes unchanged')
    classes=original.SLOT/'classes'
    require({v.name for v in classes.glob('*.class')}==set(p['compiledMetadataClasses'])=={'PublicJacocoFormatMetadataV1.class','PublicJacocoFormatMetadataV1$Counts.class'} and all(data.sha((classes/name).read_bytes())==h for name,h in p['compiledMetadataClasses'].items()),'only two own metadata classes')
    require(all((data.ROOT/r['path']).resolve()==data.ROOT/r['path'] and data.sha((data.ROOT/r['path']).read_bytes())==r['inputSha256'] for r in rows),'original public bytes preserved after two readers')
    vectors_bad=[('format-count','formatInspectedFiles',9),('byte-count','formatInspectedBytes',155225),('text-closure','remainingUnclassified',0),('binary-closure','remainingBinaryOrContainerGate',0),('png-closure','otherPngFilesUninspected',0),('secrets','actualSecretCount',0),('privacy','whole451SecretGateAccepted',True),('provenance','sessionAndClassProvenanceQualified',True),('binary-review','binaryReviewCompleted',True),('product','productTestsExecuted',1),('classload','productClassesLoaded',True),('method','productMethodsInvoked',True),('ids','sessionIdValuesOrHashesSaved',True),('names','classNameValuesOrHashesSaved',True),('probes','probeArraysSaved',True),('scan','scannerExecuted',True),('history','historyExpanded',True),('raw','privateRawRead',True),('formal','formalUpdated',True),('accepted','newAccepted',1),('bool-accepted','newAccepted',False),('effort','effortPercent',0),('union','coverageExecUnion',True),('transfer','sourceRuntimeQualificationTransferred',True),('native','originalNativeReexecuted',True)]
    labels=[]
    for label,key,value in vectors_bad:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad,rows,scan,inventory)
        except ValueError:labels.append(label)
        else:raise ValueError('false public format closure '+label)
    for label,change in [('raw-result-key',lambda r:r[0].update(sessionId='PUBLIC_FAKE_NOT_A_REAL_ID')),('counter-divergence',lambda r:r[0]['official'].update(hits=0)),('partial-bytes',lambda r:r[0]['python'].update(consumedBytes=0)),('binary-file-substitution',lambda r:r[0].update(inputSha256='0'*64)),('provenance-escalation',lambda r:r[0].update(provenanceQualified=True)),('boolean-counter',lambda r:r[0]['official'].update(headers=True))]:
        changed=copy.deepcopy(rows);change(changed)
        try:assess(p,changed,scan,inventory)
        except ValueError:labels.append(label)
        else:raise ValueError('false aggregate-only input proof '+label)
    release=original.JDK.parent/'release';release_lines=release.read_text().splitlines();versions={v.split('=',1)[0]:v.split('=',1)[1].strip('"') for v in release_lines if v.startswith(('JAVA_VERSION=','JAVA_RUNTIME_VERSION='))}
    require(versions['JAVA_VERSION']=='25.0.4','actual local tool JDK release, no version inferred from historical native')
    verify(p['invocation']);verify(invocation)
    aggregate={k:sum(r['python'][k] for r in rows) for k in COMMON};aggregate['unusedPaddingSetBits']=sum(r['python']['unusedPaddingSetBits'] for r in rows)
    OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,parentManifestSha256=PIN,resultsSha256=p['resultsSha256'],vectorsSha256=p['vectorsSha256'],formatInspectedFiles=10,formatInspectedBytes=155226,independentMetadataNegativeVectors=len(labels),negativeLabels=labels,metadataPositiveVectors=5,metadataNegativeVectors=14,apiTypeNegativeVectors=4,aggregateFormatStatistics=aggregate,statisticsAreNotProductCoverageOrTestCounts=True,historicalFieldRedactionDomain='HISTORICAL_INPUT_FIELD_VALUES_ONLY; SOURCE_DECLARED_PUBLIC_SYNTHETIC_TOOL_FIXTURES_SEPARATE',publicSyntheticSessionFixtureLabelsDeclaredInToolSource=True,historicalSessionValuesOrHashesPersisted=False,historicalClassNameValuesOrHashesPersisted=False,metadataToolVersions=dict(python=platform.python_version(),jacoco='0.8.15',jdk=versions),jdkReleaseSha256=data.sha(release.read_bytes()),allOriginalInputBytesPreserved=True,independentDecodersComparedWithoutRerun=True,productClassesLoaded=False,productMethodsInvoked=False,productTestsExecuted=0,sourceRuntimeQualificationTransferred=False,coverageExecUnion=False,originalNativeReexecuted=False,scannerExecuted=False,historyExpanded=False,privateRawRead=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,additionalFalsePositives=0,remainingUnclassified=4493,remainingBinaryOrContainerGate=22,otherPngFilesUninspected=12,binaryReviewCompleted=False,sessionAndClassProvenanceQualified=False,actualSecretCount=None,whole451SecretGateAccepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,files=10,independentNegativeVectors=len(labels),aggregate=aggregate,wholeG07Accepted=False)))
if __name__=='__main__':main()
