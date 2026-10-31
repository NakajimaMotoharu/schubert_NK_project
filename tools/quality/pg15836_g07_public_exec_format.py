"""WBS-G07/3021: fixed ten public historical exec files, independent metadata decoders only."""
import json
import platform
import subprocess
from pathlib import Path
import g07_host_class_provenance_inputs as data
import public_jacoco_exec_format_v1 as fmt
import pg9666_pagination_static as run
from host_tool_invocation import capture,verify

ROOT=data.ROOT
OUT=data.BASE/'PG15836-g07-public-exec-format-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg15836-g07-public-exec-format-v1'
JDK=run.TC/'jdk-25.0.4/bin'
JAR=run.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
JAR_SHA='ade1e0fdb4cd80d8537b57c6edb70a1360c47fdc518c20c65314517479bc4d0d'
HELPER=ROOT/'tools/quality/architecture/PublicJacocoFormatMetadataV1.java'
HELPER_SHA='5042f1732f0b1e2741f8331ca789fd4139cad063cfda10f94e64fb3267fd47aa'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SCAN=('PG8968-public-blob-scan-v1','f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739')
INVENTORY_SHA='f14aadb1a1e2f5d6a435ef53e701f315a9f116c29ae4c6a426ff221c7a9e698d'
EXPECTED={
 'PG383-native-deployment/morning-first.exec':('c77cbd6cd72b2d0d719f84d42a17225377531f9468a77992e000f7e1c36846ce',22568),
 'PG384-native-deployment/morning-first.exec':('723aae99ec447f483653ff9538ff078ea94f70089e09b801a33cb04cdb66d6d7',21997),
 'PG385-native-deployment/backup-first.exec':('a216ab497da0caca691c8f65430d0c7692c5f21dfb510beea3e54510e86d2270',3078),
 'PG385-native-deployment/morning-first.exec':('40f18ecde6d3a9debcaa528fcdbfa5f70ddab88b2b61660736784b89f2575254',25324),
 'PG386-native-backup-failure/pg386-failed-backup.exec':('c696c2db2f2c390f550027dfbd1b10f2974ad94670d5343bbd41e635b84dbd94',3207),
 'PG386-native-backup-failure/pg386-failed-parent.exec':('fc2d5ca736350a2ef32a6644d3d2fc946264b95116afb7486c27023b374757e3',23289),
 'PG386-native-backup-failure/pg386-positive-backup.exec':('ea120e61570e0bb66d7aa088c35e8d65bffeb5c939244ed7c93dadbe1e599dd2',3078),
 'PG386-native-backup-failure/pg386-positive-parent.exec':('46e183453cba73352e971def35a6543868e8c9513da415203e15b29433f56b5d',25325),
 'PG387-native-normal-resume/backup.exec':('cc0e30af21680d25c162b4543a6478660315d7b9115fc0e9375c4867d476f5e0',3005),
 'PG387-native-normal-resume/parent.exec':('50d3465505487249518045a321c6bc563bbeadbc93f2b72f60eebc4659a913c1',24355)}
PREFIX='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'

def require(ok,label):
    if not ok:raise ValueError(label)

def bound_rows():
    scan=data.read_checked(data.BASE/SCAN[0]/'manifest.json',SCAN[1])
    inventory=data.read_checked(data.BASE/SCAN[0]/'inventory.json',INVENTORY_SHA)
    require(scan['actualExit']==0 and scan['inventorySha256']==INVENTORY_SHA and scan['contentCommit']==data.CONTENT and scan['source']==data.HISTORICAL and scan['binaryOrContainerLimitedCount']==22,'fixed historical scan, no current gate')
    selected={PREFIX+k:v for k,v in EXPECTED.items()}
    require({p for p in scan['binaryOrContainerLimitedPaths'] if p.endswith('.exec')}==set(selected),'exact ten original binary exec paths')
    rows=[r for r in inventory['rows'] if r['path'] in selected]
    require(len(rows)==10 and len({r['path'] for r in rows})==10,'ten original rows only')
    for r in rows:
        path=ROOT/r['path'];pin,size=selected[r['path']]
        require(r['sha256']==pin and r['bytes']==size and r['inspectionLimit']=='BINARY_OR_CONTAINER_NO_INNER_SCAN','original manifest binding')
        require(path.resolve()==path and path.is_file() and not path.is_symlink() and path.stat().st_size==size and data.sha(path.read_bytes())==pin,'same public repo blob, no alternative/private/history read')
    return scan,rows

def main():
    invocation=capture(__file__);require(not SLOT.exists() and not OUT.exists(),'new-only tool group')
    scan,rows=bound_rows()
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    require(data.sha(JAR.read_bytes())==runtime['toolAndDependencyHashes'][str(JAR)]==JAR_SHA and data.sha(HELPER.read_bytes())==HELPER_SHA,'reviewed official parser and own aggregate-only helper')
    tool_hashes={str(HELPER.relative_to(ROOT)):HELPER_SHA,str(Path(fmt.__file__).relative_to(ROOT)):data.sha(Path(fmt.__file__).read_bytes())}
    SLOT.mkdir();run.SLOT=SLOT;classes=SLOT/'classes';classes.mkdir();inputs=SLOT/'public-tool-fixtures';inputs.mkdir()
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scanManifestSha256=SCAN[1],inventorySha256=INVENTORY_SHA,inputRows=rows,toolSourceHashes=tool_hashes,librarySha256=JAR_SHA,productClassesLoaded=False,productTestsExecuted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0))
    stages=[]
    stage=run.step('compile-format-helper',[str(JDK/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',str(JAR),'-d',str(classes),str(HELPER)],SLOT,timeout=120);stages.append(stage)
    require(stage['actualExit']==0 and not stage['timedOut'],'own metadata helper compile')
    positive,negative=fmt.fixtures();self_rows=[]
    for label,blob,expected in positive:
        actual=fmt.parse(blob);require(actual==expected,'independent literal self vector '+label)
        path=inputs/(label+'.exec');path.write_bytes(blob)
        s=run.step('vector-'+label,[str(JDK/'java'),'-cp',str(classes)+':'+str(JAR),'PublicJacocoFormatMetadataV1',str(path)],SLOT,timeout=30);stages.append(s)
        require(s['actualExit']==0 and not s['timedOut'],'official parser positive vector')
        observed=json.loads((SLOT/('vector-'+label+'.stdout')).read_bytes())
        require(observed=={k:expected[k] for k in fmt.COMMON},'independent official positive summary')
        self_rows.append(dict(label=label,inputSha256=data.sha(blob),bytes=len(blob),expected=expected,actual=actual,official=observed,actualExit=0))
    for label,blob in negative:
        try:fmt.parse(blob)
        except ValueError:pass
        else:raise ValueError('negative metadata accepted '+label)
        path=inputs/(label+'.exec');path.write_bytes(blob)
        s=run.step('vector-'+label,[str(JDK/'java'),'-cp',str(classes)+':'+str(JAR),'PublicJacocoFormatMetadataV1',str(path)],SLOT,timeout=30);stages.append(s)
        require(s['actualExit']==2 and not s['timedOut'] and not (SLOT/('vector-'+label+'.stdout')).read_bytes(),'official parser negative rejected without values')
        self_rows.append(dict(label=label,inputSha256=data.sha(blob),bytes=len(blob),expectedExit=2,actualExit=s['actualExit']))
    type_labels=[]
    for label,value in [('null',None),('text','PUBLIC'),('boolean',False),('mutable-buffer',bytearray(positive[2][1]))]:
        try:fmt.parse(value)
        except ValueError:type_labels.append(label)
        else:raise ValueError('non-byte API value accepted')
    results=[]
    for index,row in enumerate(rows,1):
        raw=(ROOT/row['path']).read_bytes();python=fmt.parse(raw)
        label='historical-public-'+str(index).zfill(2)
        s=run.step(label,[str(JDK/'java'),'-cp',str(classes)+':'+str(JAR),'PublicJacocoFormatMetadataV1',str(ROOT/row['path'])],SLOT,timeout=30);stages.append(s)
        require(s['actualExit']==0 and not s['timedOut'],'official historical format parse')
        official=json.loads((SLOT/(label+'.stdout')).read_bytes())
        require(official=={k:python[k] for k in fmt.COMMON} and python['bytes']==python['consumedBytes']==row['bytes'],'two independent declared-field parses')
        results.append(dict(path=row['path'],inputSha256=row['sha256'],gitObject=row['gitObject'],bytes=row['bytes'],python=python,official=official,allDeclaredBytesConsumed=True,sessionIdValuesOrHashesSaved=False,classNameValuesOrHashesSaved=False,provenanceQualified=False,secretGateAccepted=False))
    require(len(results)==10 and all(data.sha((ROOT/r['path']).read_bytes())==r['sha256'] for r in rows),'all original input bytes preserved')
    require(all(data.sha((ROOT/p).read_bytes())==h for p,h in tool_hashes.items()) and data.sha(JAR.read_bytes())==JAR_SHA,'tool/library bytes unchanged')
    verify(invocation);OUT.mkdir();data.write(OUT/'results.json',results);data.write(OUT/'metadata-vectors.json',dict(positiveAndNegative=self_rows,typeNegativeLabels=type_labels))
    compiled={p.name:data.sha(p.read_bytes()) for p in sorted(classes.glob('*.class'))}
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,reviewHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),invocation=invocation,wbs='WBS-G07',specification='evidence/01_PT/018_NK-OPS-001/3021_G07公開exec十件_形式境界限定仕様.md',historicalScanSource=scan['source'],contentCommit=scan['contentCommit'],scanManifestSha256=SCAN[1],inventorySha256=INVENTORY_SHA,toolSourceHashes=tool_hashes,officialLibraryPath=str(JAR),officialLibrarySha256=JAR_SHA,compiledMetadataClasses=compiled,os=dict(system=platform.system(),release=platform.release(),machine=platform.machine()),stages=stages,metadataPositiveVectors=len(positive),metadataNegativeVectors=len(negative),apiTypeNegativeVectors=len(type_labels),formatInspectedFiles=10,formatInspectedBytes=sum(r['bytes'] for r in rows),resultsSha256=data.sha((OUT/'results.json').read_bytes()),vectorsSha256=data.sha((OUT/'metadata-vectors.json').read_bytes()),inputFilesMutated=False,sessionIdValuesOrHashesSaved=False,classNameValuesOrHashesSaved=False,probeArraysSaved=False,productClassesLoaded=False,productMethodsInvoked=False,productTestsExecuted=0,sourceRuntimeQualificationTransferred=False,coverageExecUnion=False,originalNativeReexecuted=False,scannerExecuted=False,historyExpanded=False,privateRawRead=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,additionalFalsePositives=0,remainingUnclassified=4493,remainingBinaryOrContainerGate=22,otherPngFilesUninspected=12,formatEvidenceOnly=True,sessionAndClassProvenanceQualified=False,binaryReviewCompleted=False,actualSecretCount=None,whole451SecretGateAccepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,formatFiles=10,bytes=sum(r['bytes'] for r in rows),positiveVectors=len(positive),negativeVectors=len(negative),typeNegativeVectors=len(type_labels),newProductTests=0,wholeG07Accepted=False)))
if __name__=='__main__':main()
