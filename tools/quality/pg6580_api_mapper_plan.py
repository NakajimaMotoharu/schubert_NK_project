"""Explicit ordinary API edit plan, pure preview only; source edits use apply_patch after red proof."""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6542_jdbc_catch_inventory import LEX, balanced

SOURCE='f3fffb246ee1dc62389ec0085c1fd6556ad79694'
NAMES={
 'UserCommandService','UserMutationApplicationService','UserQueryApplicationService','LogQueryApplicationService',
 'MediaApplicationService','QuestionCommandService','QuestionMutationApplicationService','QuestionQueryApplicationService',
 'QuestionSubmissionService','QuestionWorkerService','ScenarioApplicationService','JdbcInboxCoordinator',
 'WebLogIngestService','InboxCleanup','LoginInboxService','LoginReplayService','LogoutInboxService','LogoutReplayService',
 'OutboxDispatcher'}
SQL_IDS={'SQLCATCH-'+str(n).zfill(3) for n in (1,2,5,8,11,14,15,16,19,22,23,25,29,34,41,44,48,77,78,79,80)}
PURE_INPUT_EXCLUSIONS={('LoginInboxService',81),('LoginInboxService',155),
                       ('LogoutInboxService',75),('QuestionWorkerService',163),
                       ('UserCommandService',93),('UserCommandService',258),
                       ('WebLogIngestService',45),('WebLogIngestService',91)}


def spans(text):
    ts=[(('LITERAL' if m.group().startswith(('"',"'")) else m.group()),m.start(),m.end())
        for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    simple=[(token,start) for token,start,_ in ts]; result=[]
    for at,(token,start,_) in enumerate(ts):
        if token!='catch':continue
        end=balanced(simple,at+1,'(',')');last=balanced(simple,end+1,'{','}')
        header=[x[0] for x in ts[at+2:end]]
        body=ts[end+2:last]
        line_start=text.rfind('\n',0,start)+1
        indent=re.match(r'[ \t]*',text[line_start:start]).group()+'  '
        result.append(dict(line=text.count('\n',0,start)+1,header=header,var=header[-1],body=body,
            headerStart=ts[at+1][2],headerEnd=ts[end][1],bodyStart=ts[end+1][2],indent=indent))
    return result


def apply_edits(text,edits):
    ordered=sorted(edits,key=lambda x:(x[0],x[1]))
    for first,second in zip(ordered,ordered[1:]):
        if first[1]>second[0]:raise ValueError('overlapping source operations require explicit review')
    for start,end,value in reversed(ordered):text=text[:start]+value+text[end:]
    return text


def semantic_hash(text):
    tokens=[m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    imports=[];body=[];at=0
    while at<len(tokens):
        if tokens[at]=='import':
            end=tokens.index(';',at);imports.append(tokens[at:end+1]);at=end+1
        else:body.append(tokens[at]);at+=1
    return hashlib.sha256(json.dumps({'imports':sorted(imports),'body':body}).encode()).hexdigest()


def transform(name,text,sql_ids):
    edits=[];actions=[];sql_ordinal=0;excluded=[]
    auth=name in {'LoginInboxService','LoginReplayService','LogoutInboxService','LogoutReplayService'}
    owner='AuthenticationInfrastructureException' if auth else 'TemporaryInfrastructureException'
    for row in spans(text):
        header=row['header'];var=row['var'];body=[t for t,_,_ in row['body']]
        is_sql='SQLException' in header
        if is_sql:
            if sql_ordinal>=len(sql_ids):raise ValueError('SQL cardinality changed')
            site_id=sql_ids[sql_ordinal];sql_ordinal+=1
        else:site_id=None
        if (name,row['line']) in PURE_INPUT_EXCLUSIONS:
            excluded.append(dict(line=row['line'],reason='PURE_WIRE_IP_OR_CLOSED_VALUE_VALIDATION_NO_PROVIDER_OR_OWNED_RESOURCE'))
            continue
        guarded=any(body[i:i+4]==['preserveFatal','(',var,')'] for i in range(len(body)-3))
        raw=body==['throw',var,';']
        marker=(not is_sql and not raw and ('new' in body or 'getSuppressed' in body or 'getSQLState' in body
            or ('return' in body and 'ResultCode' in body) or 'AnswerBusinessException' in header))
        if not guarded and (site_id in SQL_IDS or marker) and name!='OutboxDispatcher':
            edits.append((row['bodyStart'],row['bodyStart'],'\n'+row['indent']+owner+'.preserveFatal('+var+');'))
            actions.append(dict(kind='SQL_MAPPER_GUARD' if is_sql else 'MARKER_MAPPER_GUARD',line=row['line'],site=site_id,var=var,owner=owner))
        if (is_sql and 'RuntimeException' in header and 'Error' not in header and 'rollback' in body
                and any(body[i:i+3]==['throw',var,';'] for i in range(len(body)-2))):
            edits.append((row['headerStart'],row['headerEnd'],'SQLException | RuntimeException | Error '+var))
            actions.append(dict(kind='OWNED_PRIMARY_ERROR_ROLLBACK',line=row['line'],var=var))
        for at in range(len(row['body'])-6):
            selected=row['body'][at:at+7];tokens=[x[0] for x in selected]
            if tokens[1:]==['.','addSuppressed','(',var,')',';'] and tokens[0]!=var:
                if set(header[:-1])-{'SQLException','RuntimeException','|'}:
                    raise ValueError('secondary type policy requires explicit review')
                edits.append((row['headerStart'],row['headerEnd'],'SQLException | RuntimeException | Error '+var))
                edits.append((selected[0][1],selected[-1][2],
                    'TemporaryInfrastructureException.attachSecondary('+tokens[0]+', '+var+');'))
                actions.append(dict(kind='OWNED_SECONDARY_PORT',line=row['line'],primary=tokens[0],secondary=var))
    if sql_ordinal!=len(sql_ids):raise ValueError('SQL cardinality changed')
    if name=='OutboxDispatcher':
        old='if (primary != secondary) primary.addSuppressed(secondary);'
        if text.count(old)!=1:raise ValueError('preserve exact Outbox direct fatal selection before attachment')
        at=text.index(old);edits.append((at,at+len(old),'TemporaryInfrastructureException.attachSecondary(primary, secondary);'))
        actions.append(dict(kind='OUTBOX_SECONDARY_PORT_AFTER_EXISTING_FATAL_PRIORITY',line=text.count('\n',0,at)+1))
    if any('TemporaryInfrastructureException' in e[2] for e in edits) and 'import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;' not in text:
        first_import=next((m.start() for m in LEX.finditer(text) if m.group()=='import'),None)
        if first_import is None:
            package_end=text.index(';')+1
            edits.append((package_end,package_end,'\n\nimport dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;'))
        else:
            edits.append((first_import,first_import,'import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;\n'))
    return apply_edits(text,edits),actions,excluded


def plan():
    qp=BASE/'PG6574-jdbc-attachment-qualification-v1/manifest.json'
    if sha(qp)!='f8fb1042d4bd310987153659d7b1e51ca95a8d6337ae3df7d0e9c830efa8c5d0':raise ValueError('qualified core31 first')
    q=json.loads(qp.read_bytes());pp=W/'pg6574-jdbc-attachment-qualification-v1/manifest.safe.json'
    if q['source']!=SOURCE or q['actualExit']!=0 or sha(pp)!=q['privateManifestSha256']:raise ValueError('exact source and original receipt')
    private=json.loads(pp.read_bytes());hashes={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(hashes)!=851 or hashes!=private['allSourceHashes']:raise ValueError('all851 Main fixed before edit planning')
    original_root=BASE/'PG6542-jdbc-catch-inventory-v1'
    if sha(original_root/'manifest.json')!='d8aa3acc4f287da8581fdbdf5c2a25ce8ae94b15c468fd02acae35c043ef4435':
        raise ValueError('immutable initial site identities')
    original=original_root/'sites.json';groups=defaultdict(list)
    if sha(original)!=json.loads((original_root/'manifest.json').read_bytes())['inventorySha256']:
        raise ValueError('original site row digest')
    for row in json.loads(original.read_bytes()):groups[row['sourcePath']].append(row['siteId'])
    paths={p for p in hashes if p.split('/')[-1].removesuffix('.java') in NAMES and '/schubert-nk-api/' in p}
    if len(paths)!=19:raise ValueError('exact declared19 API Main paths')
    files=[];patches=[];all_actions=[];exclusions=[]
    for path in sorted(paths):
        old=(ROOT/path).read_text();new,actions,excluded=transform((ROOT/path).stem,old,groups[path])
        if not actions or old==new:raise ValueError('each planned Main must have a reviewed semantic operation')
        all_actions.extend(dict(path=path,**a) for a in actions)
        exclusions.extend(dict(path=path,**a) for a in excluded)
        files.append(dict(path=path,oldSha256=hashes[path],newSha256=hashlib.sha256(new.encode()).hexdigest(),
                          plannedSemanticSha256=semantic_hash(new)))
        diff=list(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),n=3))
        patches.append('*** Update File: '+str(ROOT/path)+'\n'+''.join('@@\n' if line.startswith('@@') else line for line in diff[2:]))
    counts=dict(Counter(a['kind'] for a in all_actions))
    if counts!={'SQL_MAPPER_GUARD':21,'MARKER_MAPPER_GUARD':51,'OWNED_PRIMARY_ERROR_ROLLBACK':15,
                'OWNED_SECONDARY_PORT':11,'OUTBOX_SECONDARY_PORT_AFTER_EXISTING_FATAL_PRIORITY':1} or len(exclusions)!=8:
        raise ValueError('reviewed21 SQL/51 marker/15 primary/11 secondary/Outbox1/eight pure-input exclusions')
    return dict(source=SOURCE,files=files,actions=all_actions,counts=counts,exclusions=exclusions,
        patch='*** Begin Patch\n'+''.join(patches)+'*** End Patch\n',acceptedSites=0,testsExecuted=0)


def main():
    p=argparse.ArgumentParser();p.add_argument('--emit-patch',action='store_true');args=p.parse_args();value=plan()
    if args.emit_patch:
        rp=BASE/'PG6578-provider-original-red-v1/manifest.json'
        if sha(rp)!='ba7d077f5c8ca230963b77dd7466e7286fbfceed0bf2e25955b25c721ed909ba':
            raise ValueError('qualified existing provider red before PG')
        red=json.loads(rp.read_bytes())
        if not (red['actualExit']==0 and red['originalExit']==1 and (red['tests'],red['suites'])==(9,5)
                and len(red['expectedFailures'])==2):raise ValueError('genuine two purposeful assertions')
        if subprocess.check_output(['git','diff',red['source'],'--','src'],cwd=ROOT):
            raise ValueError('all original Main/Test bytes still fixed before applying reviewed PG')
        if subprocess.check_output(['git','status','--porcelain','--','src'],cwd=ROOT):
            raise ValueError('no dirty/untracked source/test discarded by generated patch')
    if not args.emit_patch:value={k:value[k] for k in ('source','counts','exclusions','acceptedSites','testsExecuted')}
    print(json.dumps(value,ensure_ascii=False,sort_keys=True))


if __name__=='__main__':main()
