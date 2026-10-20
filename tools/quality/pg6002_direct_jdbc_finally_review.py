"""21 direct JDBC finally/42 catches: explicit SS332 precedence review, not dynamic PT waiver."""
import copy
import json
import os
import re
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5994_web24_public import SOURCE,STATIC_SHA
from pg5996_web_contract_rebind import CATCH_SHA,require_current_facts
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load,apply_decisions

PREFIX='src/schubert-nk-'
PACKAGE='dev/codex/schubert/nk/'
SCOPES={
 'batch/cleanup/LogCleanupService':(4,'replace',['batch.cleanup.LogCleanupServiceTest']),
 'batch/repository/CleanupDatabaseSession':(3,'closeReplace',['batch.repository.CleanupDatabaseSessionTest']),
 'batch/repository/CleanupTerminalRepository':(2,'JdbcResourceFailures.replace',['batch.repository.CleanupTerminalRepositoryTest']),
 'batch/repository/MorningDatabaseSession':(4,'closeReplace',['batch.repository.MorningDatabaseSessionTest']),
 'api/bootstrap/SchemaHistoryAdmission':(2,'JdbcAdmissionFailures.replace',['api.maintenance.SchemaHistoryAdmissionTest']),
 'api/bootstrap/ServiceDatabaseAdmission':(2,'JdbcAdmissionFailures.replace',['api.maintenance.ServiceDatabaseAdmissionTest']),
 'web/receipt/ReceiptReferenceRepository':(4,'replace',['web.receipt.ReceiptReferenceRepositoryTest','web.receipt.ReceiptReferenceFaultTest'])}

# Independent specification matrix: no production helper is called to generate expectations.
MATRIX=[['NONE','SQL','SECONDARY_SQL_FIXED'],['NONE','UNKNOWN','SECONDARY_IDENTITY'],
        ['SQL','SQL','PRIMARY_SQL_FIXED'],['SQL','UNKNOWN','SECONDARY_IDENTITY'],
        ['UNKNOWN','SQL','PRIMARY_IDENTITY_FIXED_SUPPRESSED'],['UNKNOWN','UNKNOWN','PRIMARY_IDENTITY_FIXED_SUPPRESSED'],
        ['NONE','NONE','SUCCESS_ONLY_AFTER_CLOSE'],['SQL','NONE','PRIMARY_SQL_FIXED'],['UNKNOWN','NONE','PRIMARY_IDENTITY']]


def source_path(owner):
    module='bootstrap' if owner.startswith('api/bootstrap/') else owner.split('/')[0]
    return PREFIX+module+'/src/main/java/'+PACKAGE+owner+'.java'


def require_finally(body,helper):
    compact=re.sub(r'\s+','',body)
    if not compact.startswith('finally{') or any(x in compact for x in ('return','getCause(','getSuppressed(','getMessage(','.commit(','.rollback(','.execute(','.prepare')):
        raise ValueError('no normal return/provider operation or raw diagnostics in owned finally')
    closes=re.findall(r'\b(\w+)\.close\(\);',body)
    connection=closes==['owned','connection']
    if not connection and (len(closes)!=1 or closes[0] not in ('row','rows','statement','connection')):
        raise ValueError('one direct JDBC owner close, plus sole credential wipe for owned connection')
    guards=re.findall(r'if\('+re.escape(helper)+r'\((\w+),secondary\)\)\{?throw(secondary|unavailable\(\));',compact)
    if len(guards)!=(2 if connection else 1) or any(p not in ('rowFailure','rowsFailure','statementFailure','connectionFailure','failure','primary') for p,_ in guards):
        raise ValueError('every secondary throw is guarded by the exact typed precedence helper')
    if len(re.findall(r'\bthrow\b',body))!=len(guards):
        raise ValueError('no unconditional or additional finally throw')
    if connection and {result for _,result in guards}!={'secondary','unavailable()'}:
        raise ValueError('known SQL close fixed;unknown close identity only')
    return closes,guards


def block_helper(owner,body,declared):
    if owner not in ('batch/repository/CleanupDatabaseSession','batch/repository/MorningDatabaseSession'):
        return declared
    closes=re.findall(r'\b(\w+)\.close\(\);',body)
    if closes==['owned','connection']:
        return 'closeReplace'
    if len(closes)==1 and closes[0] in ('rows','statement'):
        return 'JdbcResourceFailures.replace'
    raise ValueError('only fixed JDBC owner scopes in these two session classes')


def require_helper(text,category):
    compact=re.sub(r'\s+','',text)
    if category=='CLOSE_CONNECTION':
        required=('booleanknown=primaryinstanceofSQLException||primaryinstanceofIOException||primaryinstanceofBatchRepositoryException;',
                  'if(primary==null||(known&&!(secondaryinstanceofSQLException)))returntrue;',
                  'if(!known)primary.addSuppressed(newBatchRepositoryException());')
    elif category=='LOG_CLEANUP':
        required=('if(primary==null||(known(primary)&&!known(secondary)))returntrue;',
                  'if(!known(primary))primary.addSuppressed(newCleanupStoppedException(CleanupStopReason.DATABASE_FAILURE));',
                  'returnfailureinstanceofSQLException||failureinstanceofBatchRepositoryException||failureinstanceofCleanupStoppedException;')
    else:
        required=('if(primary==null||(primaryinstanceofSQLException&&!(secondaryinstanceofSQLException)))returntrue;',
                  'if(!(primaryinstanceofSQLException))primary.addSuppressed(')
    if any(s not in compact for s in required) or 'returnfalse;' not in compact:
        raise ValueError('exact known-vs-unknown priority and fresh fixed secondary, never ordinary TWR replacement')


def main():
    bp=BASE/'PG5996-web-contract-dispositions-v1/manifest.json';bsha='ec7291b5ee72e48f6c19f74c2e7e35693017543be9e0f0f9837df2e27e49f22d';rows=load(bp,bsha,SOURCE)
    sp=BASE/'PG5992-web-contract-static-v1/manifest.json';cp=W/'pg5998-current-catch-facts-v1/manifest.safe.json'
    if sha(sp)!=STATIC_SHA or sha(cp)!=CATCH_SHA:raise ValueError('actual current allMain/type facts first')
    facts=json.loads(cp.read_bytes());require_current_facts(facts)
    private=W/'pg5992-web-contract-static-v1/manifest.safe.json'
    if sha(private)!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('actual current851/1666 proof hash')
    proof=json.loads(private.read_bytes())
    casep=BASE/'PG5944-current3973-cases/cases.json'
    if sha(casep)!='81a354697110977b2b859b14347cf62dad6b077d609d06997a3f891d7f4cc250':raise ValueError('semantic Test identities only, not historical PASS')
    cases=json.loads(casep.read_bytes());decisions=[];scopes=[]
    for owner,(expected,helper,testclasses) in SCOPES.items():
        path=source_path(owner);text=(ROOT/path).read_text();module=path.split('/')[1].removeprefix('schubert-nk-')
        if sha(ROOT/path)!=proof['allSourceHashes'][path] or facts['identity']['sourceHashes'][path]!=sha(ROOT/path):raise ValueError('all current source/type inputs equal')
        finallys=[r for r in rows if r['sourcePath']==path and r['rule']=='DoNotThrowExceptionInFinally' and r['status']=='NOT_REVIEWED_CURRENT_SOURCE']
        if len(finallys)!=expected:raise ValueError('all exact21 originally unreviewed finally occurrences')
        helperpath=path
        if helper.startswith('JdbcResourceFailures.'):
            helperpath=source_path('batch/repository/JdbcResourceFailures')
        elif helper.startswith('JdbcAdmissionFailures.'):
            helperpath=source_path('api/bootstrap/JdbcAdmissionFailures')
        if sha(ROOT/helperpath)!=proof['allSourceHashes'][helperpath]:raise ValueError('fresh helper bytes fixed')
        category='CLOSE_CONNECTION' if helper=='closeReplace' else 'LOG_CLEANUP' if owner.endswith('/LogCleanupService') else 'SQL'
        require_helper((ROOT/helperpath).read_text(),category)
        nested_helper=None
        if helper=='closeReplace':
            nested_helper=source_path('batch/repository/JdbcResourceFailures')
            if sha(ROOT/nested_helper)!=proof['allSourceHashes'][nested_helper]:raise ValueError('actual separate borrowed-scope helper fixed')
            require_helper((ROOT/nested_helper).read_text(),'SQL')
        refs=[]
        for simple in testclasses:
            cls='dev.codex.schubert.nk.'+simple;tp=ROOT/(PREFIX+module+'/src/test/java')/(cls.replace('.','/')+'.java')
            if not tp.is_file():raise ValueError('actual independent Test source present')
            matched=[r for r in cases if r['class']==cls]
            if not matched:raise ValueError('existing distinct independent Test semantic identities')
            refs.extend(dict(**{'class':cls},klass=cls,caseNameSha256=r['caseNameSha256'],currentTestSourceSha256=sha(tp)) for r in matched)
        related=[r for r in rows if r['sourcePath']==path and r['status']=='NOT_REVIEWED_CURRENT_SOURCE' and r['rule']=='AvoidCatchingGenericException' and any(int(f['beginline'])<=int(r['beginline'])<=int(f['endline'])for f in finallys)]
        if len(related)!=expected*2:raise ValueError('exact two generic type diagnostics per owned finally, no other catches swept in')
        blocks=[]
        for row in finallys:
            body=fragment(text,row);selected_helper=block_helper(owner,body,helper);closes,guards=require_finally(body,selected_helper)
            preceding='\n'.join(text.splitlines()[max(0,int(row['beginline'])-17):int(row['beginline'])-1])
            if any(re.search(r'\b'+re.escape(primary)+r'\s*=\s*(?:primary|failure)\s*;',preceding) is None for primary,_ in guards):raise ValueError('adjacent body catch retains actual primary before finally')
            blocks.append(dict(findingId=row['findingId'],directOwners=closes,helper=selected_helper,precedenceGuards=guards))
        for row in [*finallys,*related]:
            resolved=[]
            if row['rule']=='AvoidCatchingGenericException':
                resolved=[f for f in facts['rows']if f['path']==path and int(f['firstLine'])<=int(row['beginline'])<=int(f['lastLine'])]
                if len(resolved)!=1 or resolved[0]['returns']!='0' or 'java.lang.RuntimeException' not in resolved[0]['type'] or 'java.lang.Error' not in resolved[0]['type']:raise ValueError('one exact resolved conditional secondary catch, never normal return')
            reason='SS331/332 SSC063/199 and existing source-specific admission/cleanup/receipt contract: this owned direct JDBC finally closes only its own resource once; success returns only after close. Known SQL primary plus unknown cleanup yields the unknown identity; unknown Runtime/NPE/Error primary stays the same and receives only a fresh fixed redacted secondary. SQL/SQL stays non-success fixed. The exact helper guards every secondary throw and never self-suppresses a provider object. Ordinary TWR or unconditional finally throw would change this approved precedence. Normal/boundary/null/provider/combined fault expectations are independent existing Test source, pending new same-source whole join. This source review proves neither real DB/lock release nor Root/Unit/receipt lifecycle termination.'
            value=copy.deepcopy(row);value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',reason=reason,priorReason=reason,rawWarningRetained=True,
                 currentWholeCaseRefs=[],currentWholeJoinPending=True,plannedCurrentTestRefs=refs,currentCatchFacts=resolved,currentTypeFactsSha256=sha(cp),reviewSource=SOURCE,
                 implementationReviewedNoChangeRequired=True,historicalPtImportedAsCurrent=False,ptAlternativeCompleted=False)
            decisions.append(value)
        scopes.append(dict(path=path,sourceSha256=sha(ROOT/path),helperPath=helperpath,helperSha256=sha(ROOT/helperpath),nestedHelperPath=nested_helper,nestedHelperSha256=None if nested_helper is None else sha(ROOT/nested_helper),blocks=blocks,plannedTestReferences=len(refs),independentPrecedenceMatrix=MATRIX))
    if Counter(r['rule']for r in decisions)!=Counter(DoNotThrowExceptionInFinally=21,AvoidCatchingGenericException=42):raise ValueError('all and only63 explicitly reviewed current occurrences')
    result=apply_decisions(rows,decisions);out=BASE/'PG6002-direct-jdbc-finally63-v1';os.umask(0o077);out.mkdir();dp=out/'decisions.json'
    with dp.open('x') as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=SOURCE,baseManifestPath=bp.relative_to(ROOT).as_posix(),baseManifestSha256=bsha,decisionsSha256=sha(dp),rawFindings=1366,newIndividualDispositions=63,
               statusCounts=dict(Counter(r['status']for r in result)),scopes=scopes,currentWholeJoinPending=True,sourceCodeChanged=False,executedPtAdded=0,ptAlternativeCompleted=0,F03Accepted=False,formalAccepted=False,vmActions=0)
    with (out/'manifest.json').open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,newReasons=63,pendingWhole=636,unreviewed=730,raw=1366,manifestSha256=sha(out/'manifest.json'),decisionsSha256=sha(dp))))


if __name__=='__main__':
    main()
