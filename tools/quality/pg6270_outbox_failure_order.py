"""Actual original51 source/JVM/three physical differences; no repeated PT or actual runtime."""
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6186_native_ownership_order import methods,instructions,one_call
from pg6268_outbox_failure_qualification import original_source
from classfile_line_numbers import compare


def edges(body):
    return [(int(a),int(b),int(c),t)for a,b,c,t in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class ([\w/$]+)\s*$',body)]


def main():
    source=original_source();qp=BASE/'PG6268-outbox-failure-qualification-v1/manifest.json'
    if sha(qp)!='d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225':raise ValueError('actual original51 qualification')
    q=json.loads(qp.read_bytes());private=W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json'
    if q['source']!=source or q['actualExit']!=0 or sha(private)!=q['privateManifestSha256']:
        raise ValueError('same-source original all-Main/Jar/static proof')
    proof=json.loads(private.read_bytes());run=W/'pg6266-outbox-failure-selected-v1/source'
    old=W/'pg6246-normal-phase-selected-v1/source'
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 Main fixed')
    def jar(root):return root/'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar(run))as z:
        import hashlib
        actual={'api:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if actual!={k:v for k,v in proof['allPhysicalMainSha256'].items()if k.startswith('api:')}:
        raise ValueError('all actual original API Jar bytes remain qualified')
    def read(root,cls):
        return methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar(root)),
            'dev.codex.schubert.nk.api.messaging.outbound.'+cls],text=True))
    sender,dispatcher=[read(run,n)for n in ('OutboxJmsSender','OutboxDispatcher')]
    unchanged={}
    for name,blocks,changed in (('OutboxJmsSender',sender,(' closeAfterFailure(',)),
        ('OutboxDispatcher',dispatcher,(' transaction()',' closeAfterSetupFailure(',' rollback(',' retainFailure('))):
        before=read(old,name)
        selected=lambda values:{k:v for k,v in values.items()if not any(t in k for t in changed)}
        if selected(before)!=selected(blocks):raise ValueError('all other executable methods/exception tables unchanged '+name)
        exported=lambda values:{k for k in values if k.startswith('  public ')}
        if exported(before)!=exported(blocks):raise ValueError('unchanged public ABI '+name)
        unchanged[name]=dict(unchangedMethods=sorted(selected(blocks)),publicAbiUnchanged=True)
    choose=lambda blocks,token:next(v for k,v in blocks.items()if token in k)
    transaction=choose(dispatcher,' transaction()');mode=one_call({'transaction':transaction},'Connection.setAutoCommit:')[0]
    setup_edges=edges(transaction)
    if [t for *_,t in setup_edges]!=['java/sql/SQLException','java/lang/RuntimeException','java/lang/Error']or len({e[:3]for e in setup_edges})!=1:
        raise ValueError('SQL/RTE/Error same owned unreturned setup protection')
    if not all(a<=mode[1]<b for a,b,_,_ in setup_edges):raise ValueError('actual setAutoCommit inside all three guards')
    one_call({'transaction':transaction},'Method closeAfterSetupFailure:')
    cleanup=[]
    for method,token in ((' closeAfterSetupFailure(','Connection.close:'),(' rollback(','Connection.rollback:')):
        code=choose(dispatcher,method);call=one_call({method:code},token)[0];protections=edges(code)
        if [t for *_,t in protections]!=['java/sql/SQLException','java/lang/RuntimeException','java/lang/Error']or len({e[:3]for e in protections})!=1:
            raise ValueError('all three actual cleanup failure classes')
        retain=one_call({method:code},'Method retainFailure:')[0]
        if not all(a<=call[1]<b<=retain[1]for a,b,_,_ in protections):raise ValueError('only actual I/O is caught, not severity combiner')
        cleanup.append(dict(method=method,actualIoOffset=call[1],retainOffset=retain[1],exceptionEdges=protections))
    retain=choose(dispatcher,' retainFailure(');ops=instructions(retain)
    if sum(op=='instanceof'and'java/lang/Error'in a for _,op,a in ops)!=2 or sum(op=='if_acmpeq'for _,op,_ in ops)!=1:
        raise ValueError('fatal-over-nonfatal predicate and one identity guard')
    if any('Connection.'in a for _,_,a in ops)or len(one_call({'retain':retain},'.addSuppressed:',2))!=2:
        raise ValueError('pure severity combiner without new I/O or repeated cleanup')
    jms=choose(sender,' closeAfterFailure(');jops=instructions(jms)
    one_call({'jms':jms},'JMSContext.close:')
    one_call({'jms':jms},'.addSuppressed:',2)
    if edges(jms)!=edges(choose(read(old,'OutboxJmsSender'),' closeAfterFailure(')):
        raise ValueError('only actual owned context.close protected by unchanged RTE/Error region')
    if sum(op=='instanceof'and'java/lang/Error'in a for _,op,a in jops)!=3 or sum(op=='athrow'for _,op,_ in jops)!=3:
        raise ValueError('existing no-primary typed/fatal exits plus separate fatal-over-nonfatal exit')
    results={}
    for name in ('OutboxJmsSender$1','OutboxDispatcher','OutboxDestination'):
        member='dev/codex/schubert/nk/api/messaging/outbound/'+name+'.class'
        with zipfile.ZipFile(jar(old))as before,zipfile.ZipFile(jar(run))as after:
            result=compare(before.read(member),after.read(member))
        expected=(False,True)if name.endswith('$1')else(False,False)if name=='OutboxDispatcher'else(True,True)
        if(result['rawEqual'],result['lineNumberNormalizedEqual'])!=expected:raise ValueError('original independent debug/effective-change control '+name)
        results[name]=result
    value=dict(actualExit=0,source=source,qualificationSha256=sha(qp),scope='PG_SOURCE_JVM_NOT_REAL_ROOT_NATIVE_OR_PT_ALTERNATIVE',
        transactionSetupProtection=setup_edges,cleanup=cleanup,unchangedMethodProofs=unchanged,
        ownershipReviewed=True,severityCombinerPure=True,publicAbiUnchanged=True,originalPhysicalComparisons=results,comparisonToolSha256=sha(ROOT/'tools/quality/classfile_line_numbers.py'),
        supersededDraftManifestSha256='c16afee7c01c5578a4703d6993c904ce9dc6c7c3571265c19c9fdc1271323200',
        originalSelectedTests=51,testsExecuted=0,additionalBuildsIssued=0,productionClassesExecuted=0,vmActions=0,
        formalAccepted=False,ptAlternativeCompleted=0,residualRisks=['global/native/CHR/451/trace still pending',
            'static parsing/finite synthetic fault tests do not prove actual vendor failure or physical resource release'])
    os.umask(0o077);out=BASE/'PG6270-outbox-failure-order-v2';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,physicalDifferences=3,debugOnlySwitchHelper=True,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
