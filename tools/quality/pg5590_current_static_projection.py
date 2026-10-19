"""Fresh original diagnostic binding; preserve raw warnings and unresolved dispositions."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run
import pg5426_static_finding_projection as base
import pg5554_thread_rule_applicability as threads
import pg5578_monitor_static as diagnostic_entry
from pg5574_monitor_whole_qualification import SOURCE,ROOT,W

BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG5590-current-static-findings-v1'
PREPARED={
 'map':('PG5582-confined-map-context-v1/manifest.json','bfbdaea62259033a840c7959d59b5ba11946e3e307441f8f136cfb622386a34f'),
 'fields':('PG5584-field-accessor-inspection-v1/manifest.json','31a2a4f92e8a5a2ad0c320a1e6d78008bd560f61e4e3284388ed0a560217bc04')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def load_fixed(relative,digest):
    raw=(BASE/relative).read_bytes()
    if sha(raw)!=digest:raise ValueError('immutable prepared facts, not old test acceptance')
    return json.loads(raw)


def collect_source():
    raw=inspect.getsource(base.collect)
    for old,new in(('PG5424-ownership-static-v1','PG5578-monitor-static-v1'),('PG5424-ownership-static-input-v1','PG5578-monitor-static-input-v1')):
        if raw.count(old)!=1:raise ValueError('one exact original diagnostic namespace')
        raw=raw.replace(old,new)
    return raw+'\ncollect()\n'


def base_rows(data,diagnostic,cases):
    count=diagnostic['result']['pmd']['rawFindings']
    if type(count)is not int or count<=0:raise ValueError('actual nonempty original diagnostic inventory')
    # Only the historical inventory constant is parameterized. Every original
    # row, rule-count, source hash, unique id and explicit review guard remains.
    class Inventory(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant(count),node)if type(node.value)is int and node.value==1647 else node
    raw=ast.unparse(ast.fix_missing_locations(Inventory().visit(ast.parse(inspect.getsource(base.project)))))
    scope={**vars(base),'SOURCE':SOURCE}
    exec(compile(raw,'<fresh diagnostic exact raw inventory>','exec'),scope)
    return scope['project'](data,diagnostic,cases)


def exact_fact(row,fact,source_key='sourceSha256'):
    if any(row[k]!=fact[k]for k in('sourcePath','beginline','endline','priority'))or row['sourceSha256']!=fact[source_key]:
        raise ValueError('individual current coordinate/source must match prepared fact')
    lines=(ROOT/row['sourcePath']).read_text().splitlines(keepends=True)
    span=''.join(lines[int(row['beginline'])-1:int(row['endline'])]).encode()
    expected=fact.get('sourceSpanSha256',fact.get('declarationSpanSha256'))
    if expected is not None and sha(span)!=expected:raise ValueError('individual current source span changed')


def suite_refs(cases,suffixes):
    selected=[r for r in cases if any(r['class'].endswith('.'+name)for name in suffixes)]
    if not selected or any(r['result']!='PASS_ORIGINAL_XML'for r in selected):raise ValueError('actual current whole original XML required')
    return[{'testId':r['testId'],'xmlSha256':r['xmlSha256']}for r in selected]


def bind_prepared(rows,cases,whole,maps,fields):
    current=whole['allPhysicalMainSha256']
    seen_maps=set();seen_fields=set()
    map_index={(r['sourcePath'],r['beginline']):r for r in maps['sourceContexts']}
    field_index={(r['sourcePath'],r['beginline']):r for r in fields['fields']}
    if len(map_index)!=21 or len(field_index)!=64:raise ValueError('all21/all64 distinct prepared facts')
    if fields['all849SourceHashes']!={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in ROOT.glob('src/*/src/main/java/**/*.java')}:raise ValueError('all849 actual Main remain identical to typed inspection; no old test imported')
    for path,fact in maps['witnesses'].items():
        if sha((ROOT/path).read_bytes())!=fact['sourceSha256']:raise ValueError('map caller and immutable-boundary witnesses remain current')
        if any(current.get(k)!=v for k,v in fact.get('actualCompiledClassSha256',{}).items()):raise ValueError('each map actual current whole class must match prepared class bytes')
    for row in rows:
        key=(row['sourcePath'],row['beginline'])
        if row['rule']=='UseConcurrentHashMap':
            if key not in map_index:raise ValueError('unknown Map context cannot inherit a disposition')
            fact=map_index[key];exact_fact(row,fact);seen_maps.add(key)
            row.update(status='CONTEXT_NOT_APPLICABLE',reason=fact['basis'],contextScope='EXACT_REVIEWED_CONCURRENCY_PREMISE_ONLY',
                threadSafetyCertified=False,wholeCaseRefs=suite_refs(cases,[fact['relatedTestClass']]),preparedFactId=fact['findingId'])
        if row['rule']=='AvoidFieldNameMatchingMethodName':
            if key not in field_index:raise ValueError('unknown matching field requires a new typed inspection')
            fact=field_index[key];exact_fact(row,fact,'currentSourceSha256');seen_fields.add(key)
            row.update(status='INSPECTED_PENDING_DISPOSITION',reason='Compiler binds this exact private-final field to its same-name simple getter. Enum/Throwable and serialized-field facts are inspection only, not a style waiver.',
                compilerFacts={k:fact[k]for k in('field','declaringType','ownerKind','serializable','defaultSerializedField','publicSimpleGetter')},
                preparedFactId=fact['findingId'],currentDiagnosticBindingPending=False,dispositionAccepted=False)
    if seen_maps!=set(map_index)or seen_fields!=set(field_index):raise ValueError('all prepared contexts individually rebound, no missing/extra row')


def project(data,diagnostic,cases,whole,maps,fields):
    if not(whole['productionSource']==SOURCE and whole['tests']==3905 and whole['suites']==563 and whole['mainClasses']==1664
        and whole['staticSixModules']==whole['FESFlakyNotRun']==0 and len(cases)==3905):raise ValueError('same current genuinely qualified3905 first')
    rows=base_rows(data,diagnostic,cases)
    scope={**vars(threads),'SOURCE':SOURCE};exec(compile(inspect.getsource(threads.architecture),'<current standalone architecture>','exec'),scope)
    architecture=scope['architecture']();definition=threads.rule();thread_rows=[]
    old=load_fixed('PG5550-current3900-cases/qualification.json','5914b32a415f39e6a17147bee326a619995f31fe1383f54282242c3c13b356be')
    byte_raw=(W/'pg5542-snapshot-scratch-bytecode-v1/manifest.safe.json').read_bytes()
    if sha(byte_raw)!='cc4b8e5ccd0b1f359b9acd1bb44e1d0cefad390cc5a48bc99b7c5219965fcbb1':raise ValueError('immutable actual scratch bytecode proof')
    byte=json.loads(byte_raw);codec='api:dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'
    for name in('compress','decompress'):
        proof=byte['mainMethods'][name]
        if not(proof['classSha256']==whole['allPhysicalMainSha256'][codec]and proof['postPrefixBodyAndHandlersUnchanged']and proof['scratchNewarrayPc']<proof['constructorPc']and not proof['allocationAfterNativeBeforeGuard']):raise ValueError('actual current codec bytecode equals established acquisition proof')
    fingerprint='api:dev/codex/schubert/nk/api/idempotency/OperationFingerprint.class'
    fp=load_fixed('PG5506-snapshot-ownership-review-v1/manifest.json','bf739a63c02c95c7aba5b51a60c53a4d119a9acf01ae2de18ec8f4754563e270')
    if old['allPhysicalMainSha256'][fingerprint]!=whole['allPhysicalMainSha256'][fingerprint]or fp['fingerprintClosePcs']!=[133,140]:raise ValueError('unchanged actual fingerprint acquisition/cleanup evidence')
    native_rows=0;fingerprint_rows=0
    for row in rows:
        path=row['sourcePath'];line=int(row['beginline']);source=(ROOT/path).read_text().splitlines(keepends=True)
        if row['rule']=='DoNotUseThreads':
            row.update(status='CONTEXT_NOT_APPLICABLE',reason='Installed PMD7.28 J2EE-managed deployment premise does not apply to approved SS311/343 standalone executable/library JARs and own systemd lifecycle.',threadSafetyCertified=False,
                sourceSpanSha256=sha(''.join(source[line-1:int(row['endline'])]).encode()))
            thread_rows.append(row['findingId'])
        if row['rule']=='CloseResource'and path.endswith('/api/idempotency/ResponseSnapshotCodec.java'):
            if source[line-1].strip()not in('Deflater deflater = new Deflater(3);','Inflater inflater = new Inflater();'):raise ValueError('exact two reviewed native acquisition rows')
            refs=suite_refs(cases,['SnapshotScratchOwnershipTest','ResponseSnapshotCodecTest'])
            if len(refs)!=11:raise ValueError('all current four fault and seven actual Main public codec cases')
            row.update(status='FALSE_POSITIVE',reason='Current actual class equals bytecode proof: scratch before native acquisition, unchanged protected body/finally end; all11 current whole XML attached.',bug='BUG-1453',wholeCaseRefs=refs);native_rows+=1
        if row['rule']=='CloseResource'and path.endswith('/api/idempotency/OperationFingerprint.java'):
            row.update(status='FALSE_POSITIVE',reason='Current exact Main acquisitionPC11/Throwable handler15..132/close133,140 unchanged; current whole cases, not old test success.',wholeCaseRefs=suite_refs(cases,['OperationFingerprintTest','SecretBufferTest']));fingerprint_rows+=1
    if len(thread_rows)!=239 or len(set(thread_rows))!=239 or native_rows!=2 or fingerprint_rows!=1:raise ValueError('all individual thread and native lifecycle rows required')
    bind_prepared(rows,cases,whole,maps,fields)
    return rows,{'architecture':architecture,'threadPrimaryRule':definition,'threadFindingIds':thread_rows}


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('current source fixed')
    diag_path=W/diagnostic_entry.SLOT/'manifest.safe.json';diagnostic=json.loads(diag_path.read_bytes())
    whole_path=BASE/'PG5588-current3905-cases/qualification.json';case_path=whole_path.with_name('cases.json')
    whole=json.loads(whole_path.read_bytes());cases=json.loads(case_path.read_bytes())
    maps=load_fixed(*PREPARED['map']);fields=load_fixed(*PREPARED['fields'])
    script=collect_source();compile(script,'<metadata read only>','exec')
    os.umask(0o077);private=W/'pg5590-current-static-projection-v1';private.mkdir(mode=0o700)
    code,text=run("python3 -B - <<'PG5590_READ_ONLY'\n"+script+'\nPG5590_READ_ONLY',timeout=30)
    with(private/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('read original diagnostic only; never replay for collection')
    rows,context=project(json.loads(text),diagnostic,cases,whole,maps,fields)
    counts={s:sum(r['status']==s for r in rows)for s in sorted({r['status']for r in rows})}
    accepted=sum(r['status']in('CONTEXT_NOT_APPLICABLE','FALSE_POSITIVE','REQUIRED_CONTRACT')for r in rows)
    value={'actualExit':0,'source':SOURCE,'rawFindings':len(rows),'statusCounts':counts,'findings':rows,'context':context,
        'rowsWithAcceptedIndividualDisposition':accepted,'pendingDispositionCountsAsAccepted':False,
        'pmd':diagnostic['result']['pmd'],'checkstyle':diagnostic['result']['checkstyle'],'sameCurrentSixJarAbi':True,'sourceFiles':849,
        'wholeQualificationSha256':sha(whole_path.read_bytes()),'wholeCaseProjectionSha256':sha(case_path.read_bytes()),'diagnosticManifestSha256':sha(diag_path.read_bytes()),
        'preparedFacts':PREPARED,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'rulesSuppressed':0,'vmActions':0,'testReplays':0,'rawDiagnosticOrSecretExported':False}
    OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'rawFindings':len(rows),'statusCounts':counts,'acceptedIndividualDispositions':accepted,'sha256':sha((OUT/'manifest.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
