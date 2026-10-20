"""Exact35 identity contracts, with compiler facts/current XML; raw diagnostics never removed."""
import copy
import json
import os
from collections import Counter
from pathlib import Path
from pg5756_private_contract_qualification import SOURCE,ROOT,W,BASE
from pg5540_snapshot_scratch_selected import sha

REQUEST={'UserMutationReplayService','UserQueryReplayService','LogReplayService','QuestionMutationReplayService','QuestionQueryReplayService'}
THREAD={'ApiProcessLifetime','OwnedOutboxDispatcher','InspectorEnvironmentFiles','FixedNativeCoverageStopHold','FixedNativeCoverageTerminal','WebProcessLifetime','WebLogReplayWorker','RevocationRetryWorker'}
RECEIPT={'BackupStartIntentFiles','MorningCompletionEvidence','BackupUnitReceiptGate','MorningBackupUnitCycle'}
SESSION={'ApiSessionInvalidHandler','EncryptedSessionRequestCache','EncryptedSessionSecurityContextRepository','LocalLogoutHandler','SpringWebSession'}
ALIASES={
 'OutboxJmsSender':['OutboxDispatcherTest','OwnedOutboxDispatcherTest'],
 'ApiSessionInvalidHandler':['ApiSessionInvalidTest'],
 'EncryptedSessionRequestCache':['SessionSavedRequestTest','SessionAccessFailureTest'],
 'EncryptedSessionSecurityContextRepository':['SessionSecurityContextTest','SessionAccessFailureTest'],
 'LocalLogoutHandler':['LogoutControllerTest']}
OUT=BASE/'PG5768-reference-identity35-v1'


def contract(name,fact):
    left,right=fact['leftExpression'],fact['rightExpression'];a,b=fact['leftType'],fact['rightType']
    if name in REQUEST and fact['method']=='reply'and(left,right)==('saved.request','request')and a==b and a.endswith('Request'):
        return 'REQUEST_HANDLE','SS312/324: the verified snapshot belongs to this exact decoded request handle, not another equal-valued request. Actor/scope/result are independently rechecked; this guard grants no new replay or business operation.'
    if (name in THREAD or name=='WebRequestTrace')and a==b=='java.lang.Thread'and'Thread.currentThread()'in(left,right):
        return 'THREAD_OWNER','SS312/342/343/351: exact current Thread ownership prevents self-join or foreign-thread consumption. equals must not replace owner identity. This static contract is not proof of native capture, process ownership, real shutdown or resource postconditions.'
    if name=='SyncRequestConsumers'and fact['method']=='closeAfterFailure'and(left,right)==('closing','startupFailure')and a==b=='java.lang.Throwable':
        return 'THROWABLE_CHAIN','SS312/352: same Throwable identity returns before addSuppressed because Java rejects self-suppression; equal-valued distinct exceptions are different nodes. Fatal precedence and original diagnostic chain remain separate.'
    if name=='OutboxJmsSender'and fact['method']=='closeAfterFailure'and(left,right)==('closing','typed.getCause()')and a==b=='java.lang.Throwable':
        return 'THROWABLE_CHAIN','SS312/321/352: an already retained cause is the exact causal node; do not add that same object as a duplicate suppressed diagnostic. Distinct exceptions with equals=true must not be merged. The original primary guard and fatal precedence are not changed.'
    if name in RECEIPT and a.startswith('dev.codex.schubert.nk.batch.')and b.startswith('dev.codex.schubert.nk.batch.'):
        return 'RECEIPT_CAPABILITY','SS342/343/SSC136: private owner/baseline/receipt is a nonforgeable object capability retained by the exact issuing gate/cycle. Reconstructed equal-valued fields are not authorization. Snapshot/generation/quiescent/budget checks remain required; no real stop/retirement is certified here.'
    if name=='WebRequestTrace'and(left,right)==('CURRENT.get()','this')and a==b=='dev.codex.schubert.nk.web.logging.WebRequestTrace.Scope':
        return 'WEB_SCOPE_ORDER','SS312/351: ThreadLocal stack closes only the exact current Scope, after current-thread check, then restores previous or removes it. Equal contents cannot authorize an out-of-order close.'
    if name in SESSION and b=='dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository':
        marker='request.getAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR)'
        if ((left,right)==(marker,'sessions')and a=='java.lang.Object')or(name=='SpringWebSession'and(left,right)==('owner','repository')and a==b):
            return 'SESSION_INSTANCE','SS314 marker/same-owner repository contract: request/filter/session must use this configured encrypted repository instance. Equal configuration or another repository is not the same owner. No real session, token, DB or authentication operation is executed by this review.'
    raise ValueError('no reviewed contract for this exact typed operand/method pair')


def main():
    base=BASE/'PG5764-current-static-whole-v1/findings.json';mp=base.with_name('manifest.json')
    if sha(base)!='2b758e909aff50e50962d97a0dbe0bce1224c4ac6670008b9129a1d8163a3c93'or sha(mp)!='2ccfa8c7271d621f074d917861b06670d964677186a42e70eae0b27dbac0a0ad':raise ValueError('immutable current384 reviewed base')
    rows=json.loads(base.read_bytes());fp=W/'pg5766-reference-identity-facts-v2/manifest.safe.json'
    if sha(fp)!='f7f4f5f1db251c2de038390cdb9cb58619f954b566dc9c0b2dd065893b354148':raise ValueError('actual fixedunion compiler facts')
    facts=json.loads(fp.read_bytes());qp=BASE/'PG5754-current3932-cases/qualification.json'
    if sha(qp)!=facts['identity']['qualifiedWholeSha256']:raise ValueError('same actual3932 qualification')
    cases_path=qp.with_name('cases.json')
    if sha(cases_path)!='f0e533df0ecea383f5e7cf0639d27f98c36691de11f644278df00ec0438a7276':raise ValueError('exact current original case projection')
    q=json.loads(qp.read_bytes());cases=json.loads(cases_path.read_bytes())
    if not(facts['source']==q['productionSource']==SOURCE and facts['actualExit']==facts['independentFixtureExit']==facts['compileExit']==0 and facts['identity']['physicalMainSha256']==q['allPhysicalMainSha256']and q['tests']==3932):raise ValueError('same-source/all1664 typed/current whole first')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=facts['identity']['sourceHashes']:raise ValueError('all849 source immutable')
    index={}
    for f in facts['rows']:
        key=(f['path'],int(f['firstLine']),int(f['firstColumn']))
        if key in index:raise ValueError('compiler coordinate ambiguity')
        index[key]=f
    decisions=[];groups=Counter()
    for row in rows:
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or row['rule']!='CompareObjectsWithEquals':continue
        key=(row['sourcePath'],int(row['beginline']),int(row['begincolumn']))
        if key not in index:raise ValueError('all35 exact compiler spans, not inferred text')
        fact=index[key]
        if int(row['endline'])!=int(fact['lastLine'])or int(row['endcolumn'])!=int(fact['lastColumn'])+1 or row['sourceSha256']!=facts['identity']['sourceHashes'][row['sourcePath']]:raise ValueError('exact entire typed diagnostic span')
        name=Path(row['sourcePath']).stem;group,reason=contract(name,fact);suites=ALIASES.get(name,[name+'Test'])
        refs=[{'testId':c['testId'],'xmlSha256':c['xmlSha256'],'class':c['class'],'caseNameSha256':c['caseNameSha256']}for c in cases if c['class'].rsplit('.',1)[-1]in suites]
        if not refs or any(c['result']!='PASS_ORIGINAL_XML'for c in cases if c['class'].rsplit('.',1)[-1]in suites):raise ValueError('actual successful current suites only')
        member=row['sourcePath'].split('/src/main/java/')[1][:-5];prefix=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-')+':'+member
        classes={k:v for k,v in q['allPhysicalMainSha256'].items()if k==prefix+'.class'or k.startswith(prefix+'$')}
        if not classes:raise ValueError('all owning current classbytes')
        new=copy.deepcopy(row);new.update(status='REQUIRED_CONTRACT',reason=reason,identityCategory=group,typedReferenceFact=fact,currentPhysicalClasses=classes,currentWholeCaseRefs=refs,currentQualificationSha256=sha(qp),currentWholeJoinPending=False,rawWarningRetained=True,ptAlternativeCompleted=False,reviewSource=SOURCE)
        decisions.append(new);groups[group]+=1
    if len(decisions)!=35 or groups!=Counter({'REQUEST_HANDLE':5,'THREAD_OWNER':11,'THROWABLE_CHAIN':2,'RECEIPT_CAPABILITY':11,'WEB_SCOPE_ORDER':1,'SESSION_INSTANCE':5}):raise ValueError('all and only35 per-site reviewed contracts')
    if len({r['findingId']for r in decisions})!=35:raise ValueError('all diagnostic identities unique')
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':mp.relative_to(ROOT).as_posix(),'baseManifestSha256':sha(mp),'baseFindingsPath':base.relative_to(ROOT).as_posix(),'baseFindingsSha256':sha(base),'typedFactsSha256':sha(fp),'currentWholeQualificationSha256':sha(qp),'newIndividualDispositions':35,'identityCategoryCounts':dict(groups),'rawFindings':1582,'statusCounts':{'CONTEXT_NOT_APPLICABLE':261,'REQUIRED_CONTRACT':154,'FALSE_POSITIVE':4,'NOT_REVIEWED_CURRENT_SOURCE':1163},'overlayDoesNotRemoveDiagnostics':True,'productionChanges':0,'testExecutionsIssued':0,'ptAlternativeCompleted':0,'F03Accepted':False,'formalAccepted':False,'effortPercent':None,'vmActions':0}
    os.umask(0o077);OUT.mkdir()
    for name,data in(('manifest.json',value),('decisions.json',decisions)):
        with(OUT/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value))
    print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'decisionsSha256':sha(OUT/'decisions.json')}))


if __name__=='__main__':main()
