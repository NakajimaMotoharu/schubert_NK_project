"""Fixed296 F03 review: actual zip scratch gap is OPEN, fingerprint TWR false-positive only."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
W=ROOT.parent/'pgpt-runs/PG379'
SOURCE='29612b2a484a5ab7418e02a491c4360af7444626'
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PRIOR=BASE/'PG5426-static-findings-v1/manifest.json'
WHOLE=BASE/'PG5414-current3896-cases/qualification.json'
CASES=BASE/'PG5414-current3896-cases/cases.json'
JDK=ROOT.parent/'toolchain/jdk-25.0.4/bin/javap'


def method(text,signature):
    marker='  '+signature+';'
    if text.splitlines().count(marker)!=1:raise ValueError('one exact javap method declaration')
    part=text.split(marker,1)[1]
    match=re.search(r'^  \S.*;\s*$',part,re.M)
    return part[:match.start()]if match else part


def instructions(text):
    return[(int(m[1]),m[2],m[3]or'')for line in text.splitlines()if(m:=re.fullmatch(r'\s*(\d+):\s+(\S+)(?:\s+(.*))?',line))]


def handlers(text):
    return[(int(m[1]),int(m[2]),int(m[3]),m[4])for line in text.splitlines()if(m:=re.fullmatch(r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(any|Class .*)',line))]


def scratch_gap(text,kind):
    ops=instructions(text);table=handlers(text)
    constructors=[pc for pc,op,args in ops if op=='invokespecial'and f'java/util/zip/{kind}."<init>"'in args]
    arrays=[pc for pc,op,args in ops if op=='newarray'and args=='byte']
    ends=[pc for pc,op,args in ops if op=='invokevirtual'and f'java/util/zip/{kind}.end:'in args]
    if len(constructors)!=1 or len(arrays)!=1 or len(ends)!=2:raise ValueError('exact one constructor/scratch and normal+exceptional end')
    ctor,array=constructors[0],arrays[0]
    protected=any(start<=array<end and kind_ in('any','Class java/lang/Throwable')for start,end,_,kind_ in table)
    return{'constructorPc':ctor,'scratchNewarrayPc':array,'endPcs':ends,'scratchProtectedByErrorHandler':protected,
        'allocationAfterNativeBeforeGuard':array>ctor and not protected,'handlers':table}


def checked(path,digest):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('immutable original metadata hash')
    return json.loads(raw)


def main():
    prior=checked(PRIOR,'41ddbd7c37b2bbcbc7ee69ef911c4743f59b29523559068581622c24efdb42bc')
    whole=checked(WHOLE,'273d2710743c5da8d45918feb4dc9542ad2043306efce0a29f4ca18d5c16a56f')
    if prior['source']!=SOURCE or whole['productionSource']!=SOURCE or whole['mainClasses']!=1664:raise ValueError('same296 analyzed and compiled source')
    release=W/'pg5430-release-v1';manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest).hexdigest()!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('fixed current signed candidate BOM')
    artifact=next(row for row in json.loads(manifest)['artifacts']if row['path']=='api/api.jar');jar=release/'api/api.jar'
    if hashlib.sha256(jar.read_bytes()).hexdigest()!=artifact['sha256']:raise ValueError('same actual candidate API Jar')
    classes={};javap={}
    with zipfile.ZipFile(jar)as archive:
        for name in('ResponseSnapshotCodec','OperationFingerprint','WipingByteArrayOutputStream'):
            entry='dev/codex/schubert/nk/api/idempotency/'+name+'.class';digest=hashlib.sha256(archive.read(entry)).hexdigest()
            if whole['allPhysicalMainSha256']['api:'+entry]!=digest:raise ValueError('class equals actual3896 original whole, not an old class')
            result=subprocess.run([str(JDK),'-c','-p','-classpath',str(jar),'dev.codex.schubert.nk.api.idempotency.'+name],capture_output=True,text=True,check=True)
            classes[name]=digest;javap[name]=result.stdout
    gaps={name:scratch_gap(method(javap['ResponseSnapshotCodec'],'private static byte[] '+name+'(byte[])'),kind)for name,kind in(('compress','Deflater'),('decompress','Inflater'))}
    if not all(v['allocationAfterNativeBeforeGuard']for v in gaps.values()):raise ValueError('known1453 actual bytecode path must remain proven, not silently resolved')
    fingerprint=method(javap['OperationFingerprint'],'byte[] canonicalBytes(dev.codex.schubert.nk.api.idempotency.CanonicalRequest)')
    ops=instructions(fingerprint);table=handlers(fingerprint)
    if not any(pc==11 and op=='invokespecial'and 'WipingByteArrayOutputStream."<init>"'in args for pc,op,args in ops):raise ValueError('exact fingerprint resource acquisition')
    if not any(start==15 and end==132 and kind=='Class java/lang/Throwable'for start,end,_,kind in table):raise ValueError('actual TWR body handler')
    if [pc for pc,op,args in ops if op=='invokevirtual'and 'WipingByteArrayOutputStream.close:'in args]!=[133,140]:raise ValueError('actual normal+exceptional TWR close')
    cases=json.loads(CASES.read_bytes());rows=[];hits=0
    for original in prior['findings']:
        row=dict(original);path=row['sourcePath'];line=int(row['beginline'])
        if row['rule']=='CloseResource'and(path.endswith('/OperationFingerprint.java')or(path.endswith('/ResponseSnapshotCodec.java')and line in(203,220))):
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=row['sourceSha256']:raise ValueError('exact reviewed current source')
            defect=path.endswith('/ResponseSnapshotCodec.java')
            row['status']='DEFECT_OPEN'if defect else'FALSE_POSITIVE'
            row['reason']=('BUG1453: native constructor succeeds before unprotected scratch NEWARRAY; finally end is bypassed on that allocation Error. Fault reproduction/correction still pending.'if defect else'Exact current javap: TWR acquisitionPC11/store14; Throwable handler15..132; close133 normal/140 exceptional. Resource is closed, no rule-wide exemption.')
            suites=('ResponseSnapshotCodecTest',)if defect else('OperationFingerprintTest','SecretBufferTest')
            refs=[case for case in cases if any(case['class'].endswith('.'+suite)for suite in suites)]
            if not refs or any(case['result']!='PASS_ORIGINAL_XML'for case in refs):raise ValueError('actual sameSource whole XML references only')
            row['wholeCaseRefs']=[{'testId':case['testId'],'xmlSha256':case['xmlSha256']}for case in refs]
            row['wholeCasesDoNotProveMissingFault']=defect;row['bug']='BUG-1453'if defect else None
            hits+=1
        rows.append(row)
    if hits!=3:raise ValueError('exact3 individually reviewed PMD rows')
    counts={status:sum(row['status']==status for row in rows)for status in('REQUIRED_CONTRACT','FALSE_POSITIVE','REVIEW_OPEN_STYLE','DEFECT_OPEN','NOT_REVIEWED')}
    value={'actualExit':0,'source':SOURCE,'priorProjectionSha256':hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        'rawFindings':1647,'reviewed':13,'statusCounts':counts,'findings':rows,'actualClassSha256':classes,
        'bytecodeGapProof':gaps,'fingerprintClosePcs':[133,140],'wholeQualificationSha256':hashlib.sha256(WHOLE.read_bytes()).hexdigest(),
        'actualFaultInjected':False,'F03Accepted':False,'formalAccepted':False,'productionCodeChanged':False,'rulesSuppressed':0,
        'vmActions':0,'testReplays':0,'acceptedLeafDelta':0,'effortPercent':None,'nativeCreditsTransferred':False}
    out=BASE/'PG5506-snapshot-ownership-review-v1';os.umask(0o077);out.mkdir(parents=True);path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'statusCounts':counts,'bytecodeGapProof':gaps,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'F03Accepted':False}))


if __name__=='__main__':main()
