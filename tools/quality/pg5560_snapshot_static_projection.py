"""Fresh a19 diagnostic rows and exact per-row reviews; raw1647 retained."""
import hashlib
import inspect
import json
import os
from lan_server import run
import pg5426_static_finding_projection as previous
from pg5556_snapshot_static import SOURCE,ROOT,W,SLOT

BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG5560-snapshot-static-findings-v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def collect_source():
    raw=inspect.getsource(previous.collect)
    for before,after in(('runs/PG5424-ownership-static-v1/pmd.xml','runs/PG5556-snapshot-static-v1/pmd.xml'),
        ('runs/PG5424-ownership-static-input-v1/candidate/','runs/PG5556-snapshot-static-input-v1/candidate/')):
        if raw.count(before)!=1:raise ValueError('one exact producer report/input namespace')
        raw=raw.replace(before,after,1)
    if 'PG5424'in raw or'PG5556-ownership'in raw:raise ValueError('no partial namespace rename')
    return raw+'\ncollect()\n'


def project(data,diagnostic,cases,thread,whole,bytecode):
    if not(whole['productionSource']==SOURCE and whole['tests']==3900 and whole['mainClasses']==1664
        and whole['staticSixModules']==whole['FESFlakyNotRun']==0 and len(cases)==3900):raise ValueError('actual current qualified whole/cases required')
    scope={**vars(previous),'SOURCE':SOURCE}
    exec(compile(inspect.getsource(previous.project),'<fresh original diagnostic rows>','exec'),scope)
    rows=scope['project'](data,diagnostic,cases)
    if thread['sourceSnapshot']!=SOURCE or thread['reviewedContextRows']!=239 or thread['ruleSuppressionAdded']is not False:raise ValueError('exact limited context review required')
    context={r['findingId']:r for r in thread['findings']};matched=set();ziprows=0;fingerprints=0
    codec='api:dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'
    if not(bytecode['actualExit']==0 and bytecode['sourceSnapshot']==SOURCE and bytecode['actualSelectedCases']==29):raise ValueError('actual current fault/bytecode qualification required')
    for name in('compress','decompress'):
        proof=bytecode['mainMethods'][name]
        if not(proof['classSha256']==whole['allPhysicalMainSha256'][codec]and proof['postPrefixBodyAndHandlersUnchanged']
            and proof['scratchNewarrayPc']<proof['constructorPc']and not proof['allocationAfterNativeBeforeGuard']):raise ValueError('same current actual codec must establish scratch before ownership')
    old=json.loads((BASE/'PG5414-current3896-cases/qualification.json').read_bytes())
    fingerprint='api:dev/codex/schubert/nk/api/idempotency/OperationFingerprint.class'
    old_review=json.loads((BASE/'PG5506-snapshot-ownership-review-v1/manifest.json').read_bytes())
    if not(old['productionSource']==old_review['source']and old['allPhysicalMainSha256'][fingerprint]==whole['allPhysicalMainSha256'][fingerprint]
        and old_review['fingerprintClosePcs']==[133,140]):raise ValueError('exact unchanged actual fingerprint TWR proof, not old test success')
    for row in rows:
        key=row['findingId'];path=row['sourcePath'];line=int(row['beginline'])
        if key in context:
            ref=context[key]
            fields=('rule','sourcePath','sourceSha256','beginline','endline','priority')
            if any(row[k]!=ref[k]for k in fields)or row['rule']!='DoNotUseThreads':raise ValueError('every fresh finding must exactly match individual context row')
            lines=(ROOT/path).read_text().splitlines(keepends=True)
            if sha(''.join(lines[line-1:int(row['endline'])]).encode())!=ref['sourceSpanSha256']:raise ValueError('fresh source span, not only matching count')
            row.update(status='CONTEXT_NOT_APPLICABLE',reason=ref['basis'],contextReviewFindingId=key,threadSafetyCertified=False)
            matched.add(key)
        if row['rule']=='CloseResource'and path.endswith('/api/idempotency/ResponseSnapshotCodec.java'):
            source=(ROOT/path).read_text().splitlines()
            wanted=[i+1 for i,text in enumerate(source)if text.strip()in('Deflater deflater = new Deflater(3);','Inflater inflater = new Inflater();')]
            if line not in wanted:raise ValueError('exact two current native acquisition findings only')
            refs=[r for r in cases if r['class'].endswith(('.SnapshotScratchOwnershipTest','.ResponseSnapshotCodecTest'))]
            if len(refs)!=11:raise ValueError('current original four independent fault plus seven public codec tests')
            row.update(status='FALSE_POSITIVE',reason='BUG1453 fixed: actual scratch PC3 precedes native constructor; unchanged finally end and independent fixed-Error fault test. Current whole11 actual XML; no old native credit.',bug='BUG-1453',
                wholeCaseRefs=[{'testId':r['testId'],'xmlSha256':r['xmlSha256']}for r in refs])
            ziprows+=1
        if row['rule']=='CloseResource'and path.endswith('/api/idempotency/OperationFingerprint.java'):
            refs=[r for r in cases if r['class'].endswith(('.OperationFingerprintTest','.SecretBufferTest'))]
            if not refs:raise ValueError('current original fingerprint cases required')
            row.update(status='FALSE_POSITIVE',reason='Exact physical Main unchanged; verified acquisitionPC11/Throwable handler15..132/normal close133/exception close140. Actual current whole case refs, not old success imported.',
                wholeCaseRefs=[{'testId':r['testId'],'xmlSha256':r['xmlSha256']}for r in refs])
            fingerprints+=1
    if matched!=set(context)or ziprows!=2 or fingerprints!=1:raise ValueError('all239 individual contexts plus exact three lifecycle rows, no missing/extra review')
    return rows


def main():
    diagnostic=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    private=W/'pg5560-snapshot-static-projection-v2';os.umask(0o077);private.mkdir(mode=0o700)
    raw=collect_source()
    code,output=run("python3 -B - <<'PG5560_READ_ONLY'\n"+raw+'\nPG5560_READ_ONLY',timeout=30)
    with(private/'observer.private.log').open('x')as f:f.write(output);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original diagnostic metadata read failed, no diagnostic reissue')
    def load(path,digest=None):
        blob=path.read_bytes()
        if digest and sha(blob)!=digest:raise ValueError('immutable reviewed artifact hash')
        return json.loads(blob)
    whole_path=BASE/'PG5550-current3900-cases/qualification.json';case_path=whole_path.with_name('cases.json')
    thread_path=BASE/'PG5554-thread-applicability-v1/manifest.json';byte_path=W/'pg5542-snapshot-scratch-bytecode-v1/manifest.safe.json'
    rows=project(json.loads(output),diagnostic,load(case_path),load(thread_path,'3fe00d1a9f54c50ebf9e719db47df306aba567b8c82808438a31fd86a8d0d2a3'),
        load(whole_path,'5914b32a415f39e6a17147bee326a619995f31fe1383f54282242c3c13b356be'),
        load(byte_path,'cc4b8e5ccd0b1f359b9acd1bb44e1d0cefad390cc5a48bc99b7c5219965fcbb1'))
    counts={status:sum(r['status']==status for r in rows)for status in sorted({r['status']for r in rows})}
    value={'actualExit':0,'source':SOURCE,'rawFindings':len(rows),'reviewed':sum(r['status']!='NOT_REVIEWED'for r in rows),
        'statusCounts':counts,'findings':rows,'pmd':diagnostic['result']['pmd'],'checkstyle':diagnostic['result']['checkstyle'],
        'sameCurrentSixJarAbi':True,'sourceFiles':849,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,
        'wholeQualificationSha256':sha(whole_path.read_bytes()),'wholeCaseProjectionSha256':sha(case_path.read_bytes()),
        'diagnosticManifestSha256':sha((W/SLOT/'manifest.safe.json').read_bytes()),'threadContextSha256':sha(thread_path.read_bytes()),
        'bytecodeScratchSha256':sha(byte_path.read_bytes()),'rulesSuppressed':0,'vmActions':0,'testReplays':0,'threadSafetyCertified':False,
        'rawDiagnosticOrSecretExported':False}
    OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'statusCounts':counts,'reviewed':value['reviewed'],'sha256':sha((OUT/'manifest.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
