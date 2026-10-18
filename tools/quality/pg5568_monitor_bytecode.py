"""Actual selected bytes: fourteen private monitors, acquisition order, all debug differences."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import pg5138_factory_bytecode as bytecode
import pg5566_private_monitor_selected as selection

ROOT=selection.ROOT
W=ROOT.parent/'pgpt-runs/PG379'
SLOT='pg5568-monitor-bytecode-v2'
JARS={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar',
    **{m:'api/lib/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'for m in('protocol','storage','bootstrap')}}
METHODS={
 'batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Attempt.class':('status','requireRetained','retireReadyAfter','preserveObservation','retireAfter','awaitClient'),
 'batch:dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient$Attempt.class':('status','awaitClient'),
 'bootstrap:dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$ReadyOnce.class':('release','information','complete','finish'),
 'web:dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.class':('install','close')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def release_jars(release):
    manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
    if sha(manifest)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('actual signed historical release BOM, not guessed directory convention')
    entries={r['path']:r['sha256']for r in json.loads(manifest)['artifacts']};result={}
    for module,path in JARS.items():
        target=release/path
        if path not in entries or target.is_symlink()or sha(target.read_bytes())!=entries[path]:raise ValueError('each exact actual role artifact must match signed BOM')
        result[module]=target
    return result


def private_monitor(method):
    ops=method['ops'];prefix=ops[:5]
    if 'synchronized'in method['header']or len(prefix)!=5:raise ValueError('no exposed synchronized method')
    if not(prefix[0][1]=='aload_0'and prefix[1][1]=='getfield'and'Field stateLock:Ljava/lang/Object;'in prefix[1][2]
        and prefix[2][1]=='dup'and re.fullmatch(r'astore(?:_[0-9]+)?',prefix[3][1])and prefix[4][1]=='monitorenter'):
        raise ValueError('only private stateLock enters before any owner state operation')
    if sum(op=='monitorenter'for _,op,_ in ops)!=1 or sum(op=='monitorexit'for _,op,_ in ops)<2:raise ValueError('normal and exceptional monitor release required')
    body=ops[5][0]
    if not any(first<=body<last and kind=='any'for first,last,_,kind in method['handlers']):raise ValueError('compiler finally must protect first synchronized body action')
    return{'method':method['header'],'privateLockPc':prefix[1][0],'monitorEnterPc':prefix[4][0],'firstProtectedBodyPc':body,
        'monitorExitPcs':[pc for pc,op,_ in ops if op=='monitorexit'],'finallyHandlers':[h for h in method['handlers']if h[3]=='any']}


def allocation_before_native(method,intent=False):
    ops=method['ops'];pcs=[pc for pc,_,_ in ops]
    if pcs!=sorted(set(pcs)):raise ValueError('actual ordered unique bytecode PCs required')
    created=[pc for pc,op,arg in ops if op=='new'and arg.endswith('// class java/lang/Object')]
    if len(created)!=1:raise ValueError('one dedicated state lock allocated by admitted caller')
    native=[pc for pc,_,arg in ops if '$Start.execute:'in arg]
    markers=[pc for pc,_,arg in ops if '$Intent.begin:'in arg]
    if len(native)!=1 or not created[0]<native[0]or(intent and(len(markers)!=1 or not created[0]<markers[0]<native[0])):
        raise ValueError('new lock must precede every possibly owned marker/process result')
    return{'lockNewPc':created[0],'nativeStartPc':native[0],'intentBeginPcs':markers}


def lexical_private_locks(baseline):
    rows=[];fields={}
    for finding in baseline['findings']:
        if finding['rule']!='AvoidSynchronizedStatement':continue
        path=ROOT/finding['sourcePath'];raw=path.read_bytes()
        if sha(raw)!=finding['sourceSha256']:raise ValueError('each original statement source remains exactly current, not guessed after line shift')
        source=raw.decode().splitlines();line=int(finding['beginline']);match=re.fullmatch(r'\s*synchronized \(((?:result\.)?\w+)\) \{\s*',source[line-1])
        if not match:raise ValueError('only explicit checked lock source grammar')
        expression=match[1];field=expression.rsplit('.',1)[-1]
        declaration=re.compile(r'\s*private final Object '+field+r' = new Object\(\);\s*')
        declarations=[i+1 for i,text in enumerate(source)if declaration.fullmatch(text)]
        if len(declarations)!=1:raise ValueError('one unambiguous private final fresh lock declaration per file')
        uses=[]
        for i,text in enumerate(source):
            if re.search(r'\b'+field+r'\b',text)is None:continue
            allowed=declaration.fullmatch(text)or re.fullmatch(r'\s*synchronized \((?:result\.)?'+field+r'\) \{\s*',text)
            allowed=allowed or re.fullmatch(r'\s*(?:if \(!signalled\) )?'+field+r'\.(?:notifyAll\(\)|wait\((?:100|left / 1_000_000, \(int\) \(left % 1_000_000\))\));\s*',text)
            if not allowed:raise ValueError('unreviewed reference/escape/shadow of private lock '+finding['sourcePath']+':'+str(i+1))
            uses.append(i+1)
        key=(finding['sourcePath'],field);fields[key]={'field':field,'sourcePath':key[0],'sourceSha256':sha(raw),'declarationLine':declarations[0],'allUseLines':uses}
        rows.append({'findingId':finding['findingId'],'sourcePath':key[0],'sourceSha256':sha(raw),'statementLine':line,'lockExpression':expression,
            'lockDeclarationLine':declarations[0],'privateFinalFreshAndNoTextualEscape':True,'pmdPerformanceDispositionPending':True})
    if len(rows)!=161 or len(fields)!=47:raise ValueError('all161 individually bound to47 nonescaping private lock declarations')
    return rows,list(fields.values())


def main():
    selected=W/'pg5566-private-monitor-green-v2/manifest.safe.json';raw=selected.read_bytes();proof=json.loads(raw)
    if not(proof['actualExit']==0 and proof['greenSelectedQualified']and proof['actualCases']==71 and proof['sourceFixed']
        and proof['physicalMain']['count']==1664 and len(proof['physicalMain']['sha256'])==1664):raise ValueError('genuine fixed71 green/all1664 first, never partial41')
    source=proof['sourceSnapshot']
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('same fixed source before proof')
    baseline=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5550-current3900-cases/qualification.json';prior=json.loads(baseline.read_bytes())
    if sha(baseline.read_bytes())!='5914b32a415f39e6a17147bee326a619995f31fe1383f54282242c3c13b356be':raise ValueError('immutable all1664 original actual base')
    snapshot=selected.parent/'source';jars=release_jars(W/'pg5430-release-v1')
    originals={}
    for key in proof['physicalMain']['changed']:
        module,entry=key.split(':',1)
        with zipfile.ZipFile(jars[module])as z:blob=z.read(entry)
        if sha(blob)!=prior['allPhysicalMainSha256'][key]:raise ValueError('each actual old class must equal a19 before any output')
        originals[key]=blob
    out=W/SLOT;os.umask(0o077);out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    helper=Path(__file__).with_name('MonitorDebugCanonical.java')
    subprocess.run([str(selection.TC/'jdk-25.0.4/bin/javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(helper)],check=True)
    comparisons=[];decoded={}
    for key in proof['physicalMain']['changed']:
        module,entry=key.split(':',1);actual=snapshot/('src/schubert-nk-'+module+'/target/classes')/entry
        new=actual.read_bytes()
        if sha(new)!=proof['physicalMain']['sha256'][key]:raise ValueError('actual fixed selected class')
        # Old signed296 bytes are only a class-byte source: every class used must match the
        # independently qualified a19 baseline. No native/test success is imported.
        old=originals[key]
        if sha(old)!=prior['allPhysicalMainSha256'][key]:raise ValueError('old class bytes equal exact a19, not presumed ABI equivalence')
        left=out/('old-'+str(len(comparisons))+'.class');left.write_bytes(old)
        command=[str(selection.TC/'jdk-25.0.4/bin/java'),'-cp',str(classes),'MonitorDebugCanonical',str(left),str(actual)]
        result=subprocess.check_output(command,text=True).strip().split('\t')
        if len(result)!=3 or any(re.fullmatch('[0-9a-f]{64}',s)is None for s in result[:2])or result[2]not in('true','false'):raise ValueError('actual canonical debug comparator result')
        expected=key not in selection.EXPECTED_CHANGES
        if(result[2]=='true')!=expected:raise ValueError('only declared six code changes; every extra physical difference must genuinely be debug-only')
        comparisons.append({'class':key,'oldRawSha256':sha(old),'newRawSha256':sha(new),'oldDebugStrippedSha256':result[0],'newDebugStrippedSha256':result[1],
            'classification':'DEBUG_ONLY'if expected else'DECLARED_CODE_CHANGE'})
        if key in selection.EXPECTED_CHANGES:
            text=subprocess.check_output([str(selection.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(snapshot/('src/schubert-nk-'+module+'/target/classes')),entry[:-6].replace('/','.')],text=True)
            if key in METHODS and'private final java.lang.Object stateLock;'not in text:raise ValueError('actual compiler private-final lock field required')
            decoded[key]=bytecode.methods(text)
    monitors={key:[private_monitor(bytecode.one([m for m in decoded[key]if bytecode.named(m,name)],'one actual synchronized state method'))for name in names]for key,names in METHODS.items()}
    acquire={}
    for name,method in(('BackupUnitStartClient','start'),('MaintenanceUnitStopClient','stop')):
        key='batch:dev/codex/schubert/nk/batch/platform/'+name+'.class'
        acquire[name]=allocation_before_native(bytecode.one([m for m in decoded[key]if bytecode.named(m,method)],'one actual native owner entry'),name.startswith('Backup'))
    original=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5560-snapshot-static-findings-v1/manifest.json').read_bytes())
    rows,fields=lexical_private_locks(original)
    value={'actualExit':0,'sourceSnapshot':source,'selectedManifestSha256':sha(raw),'actualSelectedCases':71,'allPhysicalMain':1664,
        'allPhysicalDifferenceClassifications':comparisons,'privateMonitorMethods':monitors,'lockBeforeNativeAcquisition':acquire,
        'existingStatementRows':rows,'existingPrivateLockFields':fields,'existingStatementSourceHashesUnchanged':True,
        'pmdPerformanceDispositionPending':True,'debugStrippingAnalysisOnly':True,'rawMainOrNativeCrcRewritten':False,
        'comparisonControlCases':3,'wholeQualified':False,'newNativeQualified':False,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':source,'privateMonitorMethods':sum(map(len,monitors.values())),
        'physicalDifferences':len(comparisons),'debugOnly':sum(r['classification']=='DEBUG_ONLY'for r in comparisons),'existingPrivateStatements':len(rows),
        'sha256':sha((out/'manifest.safe.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
