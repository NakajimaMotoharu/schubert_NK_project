"""New-source scratch ordering, exact old body/handlers, all eight fixture factories."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
import pg5506_snapshot_ownership_review as prior

ROOT=prior.ROOT
W=prior.W
RUN='pg5540-snapshot-scratch-green-v1'
SLOT='pg5542-snapshot-scratch-bytecode-v1'
CODEC='dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec'
EXPECTED={'ResponseSnapshotCodecTest.java','AuthenticationInboxInspectorTest.java','InboxResponseInspectorTest.java',
    'LogVectors.java','UserMutationReplayServiceTest.java','QuestionQueryReplayServiceTest.java','ScenarioReplayFixture.java','MediaReplayFixture.java'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_body(text,swap=False):
    starts=[start for start,_,_,kind in prior.handlers(text)if kind=='any']
    if not starts:raise ValueError('actual any/finally handler required')
    lower=min(starts);rows=[]
    for pc,op,args in prior.instructions(text):
        if pc<lower:continue
        if swap and re.fullmatch(r'a(?:load|store)_[12]',op):op=op[:-1]+('2'if op[-1]=='1'else'1')
        args=re.sub(r'^#\d+\s+//\s*','// ',args)
        rows.append((pc,op,args))
    return rows


def fixture_guard(text):
    ops=prior.instructions(text);handlers=prior.handlers(text)
    constructors=[i for i,(_,op,args)in enumerate(ops)if op=='invokespecial'and 'java/util/zip/Deflater."<init>"'in args]
    if len(constructors)!=1:raise ValueError('one native fixture acquisition per actual method')
    index=constructors[0]
    if index+2>=len(ops)or not re.fullmatch(r'astore(?:_\d+)?',ops[index+1][1]):raise ValueError('immediate native store required')
    first=ops[index+2][0]
    if not any(start<=first<end and kind=='any'for start,end,_,kind in handlers):raise ValueError('first post-store action must already have native finally protection')
    ends=[pc for pc,op,args in ops if op=='invokevirtual'and 'java/util/zip/Deflater.end:'in args]
    if len(ends)!=2:raise ValueError('normal/exception cleanup sites required')
    return{'constructorPc':ops[index][0],'immediateStorePc':ops[index+1][0],'firstProtectedActionPc':first,'endPcs':ends,'anyHandlers':[row for row in handlers if row[3]=='any']}


def method_parts(text):
    marks=list(re.finditer(r'^  (\S[^\n]*\([^\n]*\)[^\n]*);\s*$',text,re.M))
    return[(m.group(1),text[m.end():marks[i+1].start()if i+1<len(marks)else len(text)])for i,m in enumerate(marks)]


def javap(classpath,name):
    return subprocess.check_output([str(prior.JDK),'-c','-p','-classpath',classpath,name],text=True)


def main():
    proof_path=W/RUN/'manifest.safe.json'
    if sha(proof_path)!='fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78':raise ValueError('fixed original29 actual selected report')
    proof=json.loads(proof_path.read_bytes());source=proof['sourceSnapshot']
    if not(proof['greenSelectedQualified']and proof['sourceFixed']and proof['actualCases']==29 and proof['targetFour100']):raise ValueError('actual selected/target four100 first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('same fixed new Main/Test/settings')
    snapshot=W/RUN/'source';classes=snapshot/'src/schubert-nk-api/target/classes';test_classes=snapshot/'src/schubert-nk-api/target/test-classes'
    key='api:'+CODEC.replace('.','/')+'.class';path=classes/(CODEC.replace('.','/')+'.class')
    if sha(path)!=proof['physicalMain']['sha256'][key]:raise ValueError('actual selected new class, not rebuilt/old')
    original=json.loads(prior.WHOLE.read_bytes());old_jar=W/'pg5430-release-v1/api/api.jar';old_jar_sha=sha(old_jar)
    if original['productionSource']!=prior.SOURCE:raise ValueError('historical compiled base source')
    with zipfile.ZipFile(old_jar)as archive:
        old_class_sha=hashlib.sha256(archive.read(CODEC.replace('.','/')+'.class')).hexdigest()
        if old_class_sha!=original['allPhysicalMainSha256'][key]:raise ValueError('exact historical3896 compiled class for structural nonchange comparison')
    new=javap(str(classes),CODEC);old=javap(str(old_jar),CODEC)
    if sha(old_jar)!=old_jar_sha:raise ValueError('historical jar changed during structural read')
    methods={}
    for name,kind in(('compress','Deflater'),('decompress','Inflater')):
        signature='private static byte[] '+name+'(byte[])'
        n,o=prior.method(new,signature),prior.method(old,signature);point=prior.scratch_gap(n,kind)
        if not(point['scratchNewarrayPc']<point['constructorPc']and not point['allocationAfterNativeBeforeGuard']):raise ValueError('scratch before native ownership required')
        if prior.handlers(n)!=prior.handlers(o)or canonical_body(n,True)!=canonical_body(o):raise ValueError('entire post-prefix body/handler priority must remain identical modulo buffer/native local slots')
        methods[name]={**point,'postPrefixBodyAndHandlersUnchanged':True,'classSha256':sha(path)}
    fixtures={};negative=0
    for path in sorted(test_classes.rglob('*.class')):
        raw=path.read_bytes()
        if b'java/util/zip/Deflater'not in raw and b'java/util/zip/Inflater'not in raw:continue
        name=path.relative_to(test_classes).with_suffix('').as_posix().replace('/','.')
        text=javap(str(test_classes)+os.pathsep+str(classes),name)
        compiled=re.search(r'^Compiled from "([^"]+)"',text,re.M)
        for signature,body in method_parts(text):
            if not any(op=='invokespecial'and 'java/util/zip/Deflater."<init>"'in args for _,op,args in prior.instructions(body)):continue
            filename=compiled.group(1)if compiled else''
            if filename=='SnapshotScratchOwnershipTest.java':negative+=1;continue
            if filename not in EXPECTED or filename in fixtures:raise ValueError('every actual native fixture uniquely declared')
            source_paths=list((snapshot/'src/schubert-nk-api/src/test/java').rglob(filename))
            if len(source_paths)!=1:raise ValueError('one actual source per fixture class')
            fixtures[filename]={'class':name,'method':signature,'classSha256':sha(path),'sourceSha256':sha(source_paths[0]),**fixture_guard(body)}
    if set(fixtures)!=EXPECTED or negative!=1:raise ValueError('all eight actual factories plus explicit Deflater negative control accounted for')
    value={'actualExit':0,'sourceSnapshot':source,'selectedReceiptSha256':sha(proof_path),'actualSelectedCases':29,
        'mainMethods':methods,'fixtureFactories':fixtures,'intentionalNegativeDeflaterFactories':negative,
        'originalOther237CurrentQualificationNotClaimed':True,'wholeQualificationPending':True,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    out=W/SLOT;os.umask(0o077);out.mkdir(mode=0o700)
    with(out/'manifest.safe.json').open('x')as target:json.dump(value,target,sort_keys=True);target.flush();os.fsync(target.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':source,'mainMethods':methods,'fixtureCount':len(fixtures),'sha256':sha(out/'manifest.safe.json'),'wholeQualificationPending':True,'formalAccepted':False},sort_keys=True))


if __name__=='__main__':main()
