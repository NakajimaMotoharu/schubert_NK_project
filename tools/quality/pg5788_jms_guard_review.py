"""Three exact new self-suppression guards and one moved unchanged guard; whole join pending."""
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,TC,sha
from static_disposition_overlay import BASE
from pg5780_jms_primary_whole import SOURCE,W
from pg5760_changed_context_review import opcode

OUT=BASE/'PG5788-jms-guard4-v1'
SPECS={
 ('InboundTransactions.java',38):('NEW',['PT-JMS-PRE004','PT-JMS-PRE005']),
 ('InboundTransactions.java',52):('NEW',['PT-JMS-PRE001','PT-JMS-PRE002']),
 ('ArtemisReplyConsumer.java',56):('NEW',['PT-JMS-PRE006','PT-JMS-PRE007']),
 ('ArtemisReplyConsumer.java',70):('RECHECK',[])}


def main():
    bp=BASE/'PG5784-current-dispositions-v1/manifest.json'
    if sha(bp)!='1c739fd6782ce692ae241a8f1223e7e6817194a71ab4616b68d3d1c1584e36fb':raise ValueError('exact current472 pending source bindings')
    before=json.loads(bp.read_bytes());rp=bp.with_name('findings.json')
    if sha(rp)!=before['inventorySha256']:raise ValueError('all1585 current raw and pending decisions')
    rows=json.loads(rp.read_bytes());fp=W/'pg5786-jms-identity-facts-v2/manifest.safe.json'
    if sha(fp)!='47fe5bddb7c60e5f74063dd45c328503265f3686657253feaeb823a60e77b566':raise ValueError('actual current33 typed guard facts')
    facts=json.loads(fp.read_bytes());sp=BASE/'PG5776-jms-primary-static-v1/manifest.json';proof=json.loads((W/'pg5776-jms-primary-static-v1/manifest.safe.json').read_bytes())
    if sha(sp)!='aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':raise ValueError('actual new guard/source/class proof')
    if facts['source']!=SOURCE or facts['actualExit']!=0 or facts['independentJdkFixtureExit']!=facts['compileExit']or facts['compileExit']!=0 or facts['identity']['physicalMainSha256']!=proof['auxClassHashes']:raise ValueError('all current1664 actual typed input and independent fixture0')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=facts['identity']['sourceHashes']:raise ValueError('all849 actual source fixed')
    gp=BASE/'PG5778-jms-primary14/manifest.json'
    if sha(gp)!='9be091b5b0293ce1c04998890decbe36a09912b875d980deea1ab257708ba5aa':raise ValueError('actual current finite14, not whole success')
    green=json.loads(gp.read_bytes());traces={r['designTestId']:r for r in green['newDesignTestIdTrace']}
    index={}
    for fact in facts['rows']:
        key=(fact['path'],int(fact['firstLine']),int(fact['firstColumn']))
        if key in index or fact['kind']!='SELF_SUPPRESSION_GUARD':raise ValueError('unique narrow compiler fact only')
        index[key]=fact
    decisions=[];counts=Counter()
    for row in rows:
        spec=SPECS.get((Path(row['sourcePath']).name,int(row['beginline'])))
        if row['rule']!='CompareObjectsWithEquals'or spec is None:continue
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('never double-classify source-bound diagnostics')
        key=(row['sourcePath'],int(row['beginline']),int(row['begincolumn']));fact=index.get(key)
        if fact is None or int(row['endline'])!=int(fact['lastLine'])or int(row['endcolumn'])!=int(fact['lastColumn'])+1:raise ValueError('exact typed source/rule/span')
        kind,ids=spec;extra={}
        if kind=='RECHECK':
            old=subprocess.check_output(['git','show','9463db1ac23437043facf95b87f64b9fc7e758bd:'+row['sourcePath']],cwd=ROOT,text=True);current=(ROOT/row['sourcePath']).read_text();marker='  private static void rollbackAfterFailure('
            if old.count(marker)!=1 or current.count(marker)!=1 or old[old.index(marker):]!=current[current.index(marker):]:raise ValueError('entire unchanged moved rollback method tail')
            cls='dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumer';dumps=[]
            for snapshot in(W/'pg5748-exception-green-v1/source',W/'pg5774-jms-primary-green-v1/source'):
                text=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(snapshot/'src/schubert-nk-web/target/classes'),cls],text=True)
                needle='  private static void rollbackAfterFailure('
                if text.count(needle)!=1:raise ValueError('one actual disassembled method')
                dumps.append(opcode(text[text.index(needle):]))
            if dumps[0]!=dumps[1]:raise ValueError('moved method actual descriptors/opcodes/literals unchanged')
            extra.update(unchangedMethodTailSha256=hashlib.sha256(current[current.index(marker):].encode()).hexdigest(),unchangedMethodOpcodeSha256=hashlib.sha256(dumps[1].encode()).hexdigest(),priorFindingId=before['heldPriorDispositions'][0]['findingId'])
        else:
            guards=proof['newGuardsActualCoverage'];matches=[g for g in guards if g['sourcePath']==row['sourcePath']and int(g['line'])==int(row['beginline'])]
            if len(matches)!=1 or matches[0]['missedBranches']!=0 or matches[0]['coveredBranches']!=2:raise ValueError('both actual new identity outcomes observed')
            extra.update(actualNewGuardBranches=matches[0],selectedContractCases=[traces[i]for i in ids],currentSelectedManifestSha256=sha(gp))
        value=copy.deepcopy(row);value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',reason='SS312/321/352, PG-D440: exact Throwable self-suppression is forbidden by JDK identity, not equals. The current compiler proves the compared parameters guard the same addSuppressed call without reassignment/field mutation/lambda escape. Independent equal-valued distinct Throwable fixture verifies that distinct nodes remain retained. Only this exact typed span is reviewed; runtime/owned cleanup or pending whole success is not inferred.',typedSelfSuppressionFact=fact,currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True,newDispositionCreated=kind=='NEW',recheckedMovedPrior=kind=='RECHECK',**extra)
        decisions.append(value);counts[kind]+=1
    if len(decisions)!=4 or counts!=Counter({'NEW':3,'RECHECK':1}):raise ValueError('all and only exact four reviewed guards')
    os.umask(0o077);OUT.mkdir();dp=OUT/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':bp.relative_to(ROOT).as_posix(),'baseManifestSha256':sha(bp),'decisionsSha256':sha(dp),'currentTypedFactsSha256':sha(fp),'newIndividualDispositions':3,'recheckedMovedPrior':1,'rawFindings':1585,'statusCounts':{'SOURCE_REBOUND_CURRENT_WHOLE_PENDING':476,'NOT_REVIEWED_CURRENT_SOURCE':1109},'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
