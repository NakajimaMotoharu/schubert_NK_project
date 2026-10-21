"""Original89 four-boundary JVM review; no Production, provider, runtime or PT execution."""
import json
import os
import re
import subprocess
import zipfile
import hashlib
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6186_native_ownership_order import methods,instructions,one_call
from pg6326_web_graph_qualification import original_source
from classfile_line_numbers import compare

OWNERS={
 ('api','messaging.outbound.OutboxDispatcher'):(' dispatch(',' preserveFatal('),
 ('api','messaging.outbound.OwnedOutboxDispatcher'):(' run(',),
 ('web','logging.WebLogDispatcher'):(' send(',' preserveFatal('),
 ('web','logging.WebLogReplayWorker'):(' run(',)}


def graph_policy(code):
    ops=instructions(code)
    if not ops:raise ValueError('actual graph method instructions')
    for token in ('IdentityHashMap.','Collections.newSetFromMap:','Set.add:',
        'Throwable.getCause:','Throwable.getSuppressed:','JMSException.getLinkedException:','SQLException.getNextException:'):
        one_call({'graph':code},token)
    if sum(op=='athrow'for _,op,_ in ops)!=1 or any(t in code for t in ('addSuppressed:','initCause:', 'Exception table:')):
        raise ValueError('one identity Error exit, no graph mutation or conversion catch')
    predicates=[(i,a)for i,(_,op,a)in enumerate(ops)if op=='instanceof']
    if len(predicates)!=3 or not all(any(name in a for _,a in predicates)for name in ('java/lang/Error','jakarta/jms/JMSException','java/sql/SQLException')):
        raise ValueError('all three exact fatal/provider predicates')
    seen=one_call({'graph':code},'Set.add:')[0][2]
    fatal=next(i for i,a in predicates if'java/lang/Error'in a)
    if seen>=fatal:raise ValueError('identity visited before fatal/provider traversal')
    allowed=('java/util/ArrayDeque.','java/util/IdentityHashMap.','java/util/Collections.newSetFromMap:',
        'java/util/Set.add:','java/lang/Throwable.getCause:','java/lang/Throwable.getSuppressed:',
        'java/util/Arrays.asList:','jakarta/jms/JMSException.getLinkedException:','java/sql/SQLException.getNextException:')
    calls=[a.split('//',1)[-1].strip()for _,op,a in ops if op.startswith('invoke')]
    if any(not any(t in a for t in allowed)for a in calls):raise ValueError('local collection/diagnostic getters only; no I/O/cleanup/logging')
    return dict(identityVisitedBeforeClassification=True,oneIdentityErrorExit=True,graphMutationCalls=0,
        actualIoOrCleanupCalls=0,diagnosticGetterCalls=4,invocations=calls)


def main():
    source=original_source();qp=BASE/'PG6326-web-graph-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6326-web-graph-qualification-v1/manifest.safe.json'
    if not(q['actualExit']==0 and q['source']==source and(q['tests'],q['suites'],q['physicalMain'])==(89,15,1667)
        and sha(private)==q['privateManifestSha256']):raise ValueError('genuine original89 all Main/static qualification')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 current Main fixed')
    oldq=BASE/'PG6298-web-send-qualification-v1/manifest.json'
    if sha(oldq)!='00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27':raise ValueError('old qualified5eb original physical map')
    oldpublic=json.loads(oldq.read_bytes());oldprivate=W/'pg6298-web-send-qualification-v1/manifest.safe.json'
    if sha(oldprivate)!=oldpublic['privateManifestSha256']:raise ValueError('old immutable all1667 map')
    beforeproof=json.loads(oldprivate.read_bytes())
    run=W/'pg6324-web-graph-selected-v1/source';old=W/'pg6296-web-send-selected-v1/source'
    jar=lambda root,module:root/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    def read(root,module,name):
        return methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar(root,module)),
            'dev.codex.schubert.nk.'+module+'.'+name],text=True))
    current=proof['allPhysicalMainSha256'];previous=beforeproof['allPhysicalMainSha256']
    prefixes={m+':dev/codex/schubert/nk/'+m+'/'+n.replace('.','/')for m,n in OWNERS}
    changed=sorted(k for k in current if current[k]!=previous.get(k))
    expected={p+'.class'for p in prefixes}|{'web:dev/codex/schubert/nk/web/logging/WebLogDispatcher$Report.class'}
    if set(current)!=set(previous)or set(changed)!=expected:raise ValueError('exact four outer plus Report debug physical differences; others same')
    for module in ('api','web'):
        with zipfile.ZipFile(jar(run,module))as z:
            actual={module+':'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
        if actual!={k:v for k,v in current.items()if k.startswith(module+':')}:raise ValueError('every original Jar class remains qualified')
    results={};graphs={}
    for(module,name),changed_methods in OWNERS.items():
        before,after=read(old,module,name),read(run,module,name)
        keep=lambda values:{k:v for k,v in values.items()if not any(t in k for t in changed_methods)}
        if keep(before)!=keep(after):raise ValueError('every other method/exception region unchanged '+name)
        if {k for k in before if k.startswith('  public ')}!={k for k in after if k.startswith('  public ')}:raise ValueError('public ABI unchanged '+name)
        choose=lambda token:next(v for k,v in after.items()if token in k)
        if name in ('messaging.outbound.OutboxDispatcher','logging.WebLogDispatcher'):
            graph=choose(' preserveFatal(');graphs[module]=graph;policy=graph_policy(graph)
        else:policy=None
        entry=choose(' dispatch('if name=='messaging.outbound.OutboxDispatcher'else' send('if name=='logging.WebLogDispatcher'else' run(')
        checks=one_call({'entry':entry},'preserveFatal:',2 if name=='logging.WebLogDispatcher'else 1)
        if name=='messaging.outbound.OutboxDispatcher':
            mark=one_call({'entry':entry},'Method markFailure:')[0]
            if checks[0][1]>=mark[1]:raise ValueError('fatal inspection before ordinary API mark')
        elif name=='logging.WebLogReplayWorker':
            if checks[0][1]>=one_call({'entry':entry},'AtomicLong.incrementAndGet:',2)[1][1]:raise ValueError('fatal inspection before failed cycle')
        elif name=='logging.WebLogDispatcher':
            literals=[(pc,a)for pc,op,a in instructions(entry)if op.startswith('ldc')and any(t in a for t in ('WEB_LOG_PAYLOAD_INVALID','JMS_SEND_FAILURE'))]
            if len(literals)!=2 or any(checks[i][1]>=literals[i][0]for i in range(2)):raise ValueError('fatal inspection before both ordinary Web failure codes')
        else:
            sql=re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class java/sql/SQLException\s*$',entry)
            if len(sql)!=1 or checks[0][1]<int(sql[0][2]):raise ValueError('worker inspection inside temporary failure handler, not successful dispatch')
        results[module+':'+name]=dict(publicAbiUnchanged=True,otherMethodsUnchanged=sorted(keep(after)),
            classificationOffsets=[p[1]for p in checks],policy=policy)
    if graphs['api']!=graphs['web']:raise ValueError('both provider graph helpers executable/descriptor/exception policy equal')
    member='dev/codex/schubert/nk/web/logging/WebLogDispatcher$Report.class'
    with zipfile.ZipFile(jar(old,'web'))as before,zipfile.ZipFile(jar(run,'web'))as after:debug=compare(before.read(member),after.read(member))
    if debug['rawEqual']or not debug['lineNumberNormalizedEqual']:raise ValueError('Report physical difference is parsed line-number-u2 only')
    value=dict(actualExit=0,source=source,qualificationSha256=sha(qp),ownershipReviewed=True,originalSelectedTests=89,
        scope='ORIGINAL_SOURCE_JVM_NOT_REAL_RUNTIME_NATIVE_OR_PT_ALTERNATIVE',fourBoundaryProofs=results,
        helperExecutableEqual=True,changedPhysical=changed,unchangedPhysical=len(current)-len(changed),reportDebugOnly=debug,
        comparisonToolSha256=sha(ROOT/'tools/quality/classfile_line_numbers.py'),productionClassesExecuted=0,testsExecuted=0,
        additionalBuildsIssued=0,vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,
        residualRisks=['global/F03/native/CHR/451/trace remain separate','finite standard Throwable fixtures do not prove arbitrary provider getter failure, actual VM OOM or physical cleanup'])
    os.umask(0o077);out=BASE/'PG6328-outbox-graph-order-v1';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,boundaries=4,physicalDifferences=len(changed),reportDebugOnly=True,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
