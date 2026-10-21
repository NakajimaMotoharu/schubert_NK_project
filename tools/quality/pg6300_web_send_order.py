"""Original84 source/JVM ownership review, never invokes Production or real runtime."""
import json
import os
import re
import subprocess
import zipfile
import hashlib
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6186_native_ownership_order import methods,instructions,one_call
from pg6298_web_send_qualification import original_source


def edges(body):
    return [(int(a),int(b),int(c),t)for a,b,c,t in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+(any|Class [\w/$]+)\s*$',body)]


def main():
    source=original_source();qp=BASE/'PG6298-web-send-qualification-v1/manifest.json'
    if sha(qp)!='00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27':raise ValueError('actual original84 qualification')
    q=json.loads(qp.read_bytes());private=W/'pg6298-web-send-qualification-v1/manifest.safe.json'
    if q['actualExit']!=0 or q['source']!=source or sha(private)!=q['privateManifestSha256']:raise ValueError('exact original current all source/class/static proof')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('all851 Main fixed')
    snapshot=W/'pg6296-web-send-selected-v1/source';before=W/'pg6266-outbox-failure-selected-v1/source'
    def jar(root):return root/'src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar(snapshot))as z:
        actual={'web:'+n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
    if actual!={k:v for k,v in proof['allPhysicalMainSha256'].items()if k.startswith('web:')}:raise ValueError('all original Web Jar bytes qualified')
    def read(root,name):
        return methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar(root)),
            'dev.codex.schubert.nk.web.'+name],text=True))
    choose=lambda values,token:next(v for k,v in values.items()if token in k)
    results={};helpers={}
    for name in ('messaging.ArtemisRequestSender','logging.WebLogMessageSender'):
        old,new=read(before,name),read(snapshot,name)
        changed=(' closeAfterFailure(',)if name.startswith('messaging.')else(' send(',' closeAfterFailure(')
        keep=lambda values:{k:v for k,v in values.items()if not any(t in k for t in changed)}
        if keep(old)!=keep(new):raise ValueError('every other method instruction/exception body unchanged '+name)
        if {k for k in old if k.startswith('  public ')}!={k for k in new if k.startswith('  public ')}:raise ValueError('public ABI unchanged '+name)
        code=choose(new,' closeAfterFailure(');ops=instructions(code);regions=edges(code)
        close=one_call({'helper':code},'JMSContext.close:')[0]
        if len(regions)!=2 or {t for *_,t in regions}!={'Class java/lang/RuntimeException','Class java/lang/Error'}or len({r[:3]for r in regions})!=1:
            raise ValueError('only RTE/Error from one actual context.close are protected')
        if not all(a<=close[1]<b for a,b,_,_ in regions):raise ValueError('actual close inside both guards')
        if sum(op=='instanceof'and'java/lang/Error'in a for _,op,a in ops)!=2 or sum(op=='if_acmpeq'for _,op,_ in ops)!=1 or sum(op=='athrow'for _,op,_ in ops)!=2:
            raise ValueError('fatal over nonfatal, distinct identity and two direct throwable exits')
        one_call({'helper':code},'.addSuppressed:',2)
        helpers[name]=code
        results[name]=dict(publicAbiUnchanged=True,otherMethodsUnchanged=sorted(keep(new)),
            closeOffset=close[1],actualIoCalls=1,exceptionRegions=regions)
    if len(set(helpers.values()))!=1:raise ValueError('both small owned helpers have exactly the same executable/exception policy')
    old,new=read(before,'logging.WebLogMessageSender'),read(snapshot,'logging.WebLogMessageSender')
    oldsend,newsend=[choose(v,' send(')for v in (old,new)]
    tokens=('JMSContext.getSessionMode:','JMSContext.createBytesMessage:','BytesMessage.writeBytes:',
        'BytesMessage.setJMSCorrelationID:','BytesMessage.setStringProperty:','JMSContext.createProducer:',
        'JMSProducer.setDeliveryMode:','JMSProducer.setTimeToLive:','JMSProducer.send:','JMSContext.commit:',
        'BrokerTopology.fullyQualifiedQueue:','ActiveMQQueue.','Method rollback:')
    core=lambda body:[a.split('//',1)[-1].strip()for _,op,a in instructions(body)if op.startswith('invoke')and any(t in a for t in tokens)]
    literals=lambda body:[a.split('// String ',1)[1]for _,op,a in instructions(body)if op.startswith('ldc')and'// String 'in a]
    if core(oldsend)!=core(newsend)or literals(oldsend)!=literals(newsend):raise ValueError('same ordered actual wire/property/stage/commit/rollback operations and literal diagnostics')
    oldwipe=one_call({'old':oldsend},'Arrays.fill:',2);newwipe=one_call({'new':newsend},'Arrays.fill:',2)
    if any('JMSContext.close:'in a for _,_,a in instructions(newsend)):raise ValueError('no generated TWR direct close left in send')
    one_call({'newsend':newsend},'Method closeAfterFailure:',2)
    callers={}
    for name in ('messaging.JmsRequestReplyClient','logging.WebLogDispatcher','logging.WebLogReplayWorker'):
        key='web:dev/codex/schubert/nk/web/'+name.replace('.','/')+'.class'
        oldproof=json.loads((W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json').read_bytes())
        if oldproof['allPhysicalMainSha256'][key]!=proof['allPhysicalMainSha256'][key]:raise ValueError('caller unchanged original byte proof '+name)
        blocks=read(snapshot,name)
        token='JmsRequestSender.send:'if name.startswith('messaging.')else'WebLogMessageSender.send:'if name.endswith('Dispatcher')else'DispatchAction.dispatch:'
        found=one_call(blocks,token);method,pc,_=found[0];protections=[r for r in edges(blocks[method])if r[0]<=pc<r[1]]
        if any(t in ('Class java/lang/Error','Class java/lang/Throwable')for *_,t in protections):raise ValueError('direct Error cannot be converted by caller typed catches')
        if name.startswith('messaging.'):
            if not any(t=='any'for *_,t in protections)or not all(t in blocks[method]for t in ('ReplyCorrelationRegistry.cancel:','Semaphore.release:')):raise ValueError('actual nested finally cancel/release retained')
        callers[name]=dict(classSha256=proof['allPhysicalMainSha256'][key],method=method,callOffset=pc,typedAndFinallyRegions=protections,
            actualRuntimeAuthorityProven=False)
    value=dict(actualExit=0,source=source,qualificationSha256=sha(qp),scope='ORIGINAL_SOURCE_JVM_NOT_REAL_ROOT_NATIVE_OR_PT_ALTERNATIVE',
        ownershipReviewed=True,helpersExecutableEqual=True,privateHelperProofs=results,
        unchangedWlgCoreCallSequence=core(newsend),unchangedWlgLiterals=literals(newsend),
        oldWipeOffsets=[r[1]for r in oldwipe],newWipeOffsets=[r[1]for r in newwipe],unchangedCallerProofs=callers,
        originalSelectedTests=84,testsExecuted=0,additionalBuildsIssued=0,productionClassesExecuted=0,vmActions=0,
        formalAccepted=False,ptAlternativeCompleted=0,residualRisks=['global/native/CHR/451/F03/trace pending','synthetic provider faults and static caller proof do not establish actual Unit/resource completion'])
    os.umask(0o077);out=BASE/'PG6300-web-send-order-v1';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,helpersExecutableEqual=True,callers=3,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
