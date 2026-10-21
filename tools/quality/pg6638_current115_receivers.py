"""Review explicit SQL routes and join original whole artifacts; no new PT/build/network."""
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6542_jdbc_catch_inventory import LEX,balanced,sites

INVENTORY_SHA='e2aa6e25e9f090767dc88fc8fa8e0821aa979aee4a8f874d1372f27d77509c4a'
RAW_ROLES={
 'API_OWNED_ROLLBACK_RETHROW':(3,6,9,12,17,20,24,26,27,30,32,38,42,46,52,53,54),
 'API_TEMP_SECONDARY_ATTACH':(4,7,10,13,18,21,28,31,33,39,43,47),
 'OUTBOX_SETUP_CLOSE_RETHROW':(55,), 'OUTBOX_SECONDARY_RETAIN':(56,57),
 'READINESS_CAPTURE_TO_OWNED_FINALLY':(35,81),'READINESS_CLOSE_TO_FINAL_GUARD':(36,82),
 'WEB_LOG_OWNED_RETHROW':(84,86),'WEB_LOG_SECONDARY_TO_FINAL_GUARD':(85,87),
 'REQUEST_PROJECTION_ROLLBACK_RETHROW':(90,),'REQUEST_PROJECTION_SECONDARY':(91,),
 'RECEIPT_PRIMARY_RETHROW':(92,94,96,98,100),'RECEIPT_SECONDARY_REPLACE_TABLE':(93,95,97,99,101),
 'REVOCATION_CAPTURE_TO_CLEANUP':(103,),'REVOCATION_COMBINE_TO_FINAL_GUARD':(104,105),
 'SESSION_SECONDARY_OUTER_TWR':(107,),'INSPECTOR_UNRETURNED_SECONDARY':(115,)}
RAW_REASONS={
 'API_OWNED_ROLLBACK_RETHROW':'Owned rollback is attempted, transient secondary retained, original rethrown through outer Temp catalog guard; Outbox paths052..054 reach OwnedOutboxDispatcher final classifier. No success/retry assigned here.',
 'API_TEMP_SECONDARY_ATTACH':'Qualified pure Temp attachment preserves same-object/direct-primary and disabled-suppression fatal; enclosing finally/TWR retains close ownership.',
 'OUTBOX_SETUP_CLOSE_RETHROW':'Unreturned setup closes once before original rethrow; final OwnedOutboxDispatcher classifier precedes ordinary temporary handling.',
 'OUTBOX_SECONDARY_RETAIN':'retainFailure preserves SS320 direct cleanup precedence and qualified Temp attachment; final classifier precedes ordinary mark/retry.',
 'READINESS_CAPTURE_TO_OWNED_FINALLY':'Capture and raw rethrow do not map false/catalog; DB/JMS owned finally runs before module-local final pure classifier.',
 'READINESS_CLOSE_TO_FINAL_GUARD':'Existing direct-primary/direct-close table first, shared attachment next; outer module classifier before ordinary startup catalog, including suppression-disabled providers.',
 'WEB_LOG_OWNED_RETHROW':'Rollback and remaining owned close precede raw propagation to WebLogDispatcher final graph guard, before failed-cycle metric/ordinary retry.',
 'WEB_LOG_SECONDARY_TO_FINAL_GUARD':'Qualified Web attachment and legacy direct Error priority retained; finally closes remaining resource before final classification.',
 'REQUEST_PROJECTION_ROLLBACK_RETHROW':'Rollback/rethrow plus outer TWR close precede SessionStore graph guard and explicit FAILED projection; local sink paths are outside this SQL inventory.',
 'REQUEST_PROJECTION_SECONDARY':'Web shared attachment plus legacy direct rollback Error table; outer TWR retains close before FAILED mapper.',
 'RECEIPT_PRIMARY_RETHROW':'Manual ResultSet/Statement/Connection scopes retain exact selected primary, attempt remaining close, and propagate to outer SQL guard; never discard a SQL graph before catalog.',
 'RECEIPT_SECONDARY_REPLACE_TABLE':'Existing approved replace table, not blanket fatal precedence: both-SQL graphs classified before discard; unknown-primary fixed marker and direct-primary Error priority remain unchanged.',
 'REVOCATION_CAPTURE_TO_CLEANUP':'No ordinary mapping on capture; rollback/combine is protected by remaining-close finally, then existing final graph classifier.',
 'REVOCATION_COMBINE_TO_FINAL_GUARD':'combine uses qualified Web attachment; early fatal cannot skip remaining owned close; final classifier precedes temporary result.',
 'SESSION_SECONDARY_OUTER_TWR':'Qualified Web attachment, original Session catalog guard and outer TWR retain close even if attachment propagates fatal early.',
 'INSPECTOR_UNRETURNED_SECONDARY':'Unreturned admission failure owns one close; shared Temp attachment and primary final guard follow, never yielding an admitted connection on failure.'}


def raw_role(site):
    matches=[name for name,ids in RAW_ROLES.items() if int(site.removeprefix('SQLCATCH-')) in ids]
    if len(matches)!=1:raise ValueError('one explicit reviewed raw route, never default non-applicable')
    return matches[0]


def body_at(text,line):
    tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    matches=[]
    for at,(value,offset) in enumerate(tokens):
        if value!='catch' or text.count('\n',0,offset)+1!=line:continue
        end=balanced(tokens,at+1,'(',')')
        last=balanced(tokens,end+1,'{','}')
        matches.append(tokens[end+2:last])
    if len(matches)!=1:raise ValueError('one exact source catch at declared line')
    return matches[0]


def review(row,text):
    body=body_at(text,row['beginLine']);values=[v for v,_ in body];var=row['catchVariable']
    calls=[i for i in range(len(values)-3) if values[i:i+4]==['preserveFatal','(',var,')']]
    if row['category']=='GUARDED_REVIEW':
        if not calls:raise ValueError('actual caught-variable classification required')
        if row['siteId'] in ('SQLCATCH-106','SQLCATCH-114'):
            if values[:2]!=['try','{'] or 'rollback' not in values and 'close' not in values:
                raise ValueError('two explicitly reviewed cleanup-before-catalog scopes only')
            role='OWNED_CLEANUP_BEFORE_FINAL_GUARD'
            reason='Session outer TWR or unreturned inspector connection is owned until cleanup, then original graph classification precedes catalog; final cleanup is not skipped on fatal.'
        else:
            if calls[0] not in (0,2):raise ValueError('first executable statement must guard the caught variable')
            role='DIRECT_GUARD_BEFORE_MAPPING'
            reason='The first executable statement calls the qualified module graph classifier on this captured variable before SQLstate/catalog/ordinary metric; no conditional guard or provider graph retained in new catalog.'
        line=text.count('\n',0,body[calls[0]][1])+1
    elif row['category']=='RETHROW_OR_ATTACH_REVIEW':
        role=raw_role(row['siteId']);reason=RAW_REASONS[role];line=None
    else:raise ValueError('new translation/SQLstate scope requires separate review')
    return dict(role=role,reason=reason,guardLine=line,pgReviewed=True,
                perTestCausalityProved=False,accepted=False)


def read_whole():
    qp=BASE/'PG6634-current4158-cases/qualification.json';cp=qp.with_name('cases.json')
    rp=W/'pg6636-original4158-artifacts-v1/manifest.safe.json'
    op=W/'pg6634-jdbc-jms-six-v1/manifest.safe.json'
    q,r,o=[json.loads(p.read_bytes()) for p in (qp,rp,op)]
    if not(q['actualExit']==r['actualExit']==o['actualExit']==0 and q['productionSource']==r['source']==o['source']
           and (q['tests'],q['suites'],q['mainClasses'])==(4158,635,1667)
           and q['returnedOriginalTerminalExact'] and q['currentOriginalXmlQualified']
           and q['FESFlakyNotRun']==q['staticSixModules']==0 and not r['wholeReplayed']
           and r['originalManifestSha256']==sha(op) and r['publicQualificationSha256']==sha(qp)
           and r['publicCasesSha256']==sha(cp)):raise ValueError('genuine current whole and original collector receipt first')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=851 or current!=q['allSourceHashes']:raise ValueError('all current851 exact Main bytes')
    cases=json.loads(cp.read_bytes())
    if len(cases)!=4158 or any(c['source']!=q['productionSource'] or c['result']!='PASS_ORIGINAL_XML' for c in cases):
        raise ValueError('all actual same-source case identities')
    return qp,q,cases


def main():
    qp,q,cases=read_whole();path=BASE/'PG6624-jdbc-current115-v1/manifest.json'
    if sha(path)!=INVENTORY_SHA:raise ValueError('immutable115 identity inventory')
    old=json.loads(path.read_bytes());groups=defaultdict(list)
    for r in old['rows']:groups[r['sourcePath']].append(r)
    current_paths={p for p in q['allSourceHashes'] if p.split('/')[1] in ('schubert-nk-api','schubert-nk-web') and sites((ROOT/p).read_text())}
    if current_paths!=set(groups):raise ValueError('new SQL catch file outside reviewed inventory')
    rows=[];coverage={}
    for module in ('api','web'):
        p=qp.parent/'coverage'/module/'site/jacoco/jacoco.xml'
        if sha(p)!=q['modules'][module]['coverageXmlSha256']:raise ValueError('original whole coverage hash')
        coverage[module]=ET.parse(p).getroot()
    for name,priors in sorted(groups.items()):
        text=(ROOT/name).read_text();digest=sha(ROOT/name)
        priors.sort(key=lambda r:r['beginLine']);now=sites(text)
        if len(priors)!=len(now) or any(r['sourceSha256']!=digest for r in priors):
            raise ValueError('all115 source files must still exactly match qualified SQL map')
        for before,current in zip(priors,now,strict=True):
            if any(current[k]!=before[k] for k in current):raise ValueError('stable115 catch variables/body/line/token identity')
            decision=review(before,text);module=name.split('/')[1].removeprefix('schubert-nk-')
            package,file=name.split('/src/main/java/')[1].rsplit('/',1)
            sourcefile=coverage[module].find("package[@name='"+package+"']/sourcefile[@name='"+file+"']")
            if sourcefile is None:raise ValueError('original sourcefile coverage required')
            line=decision['guardLine'];node=sourcefile.find("line[@nr='"+str(line)+"']") if line else None
            cls=package.replace('/','.')+'.'+file.removesuffix('.java')+'Test'
            direct=[{k:c[k] for k in ('testId','class','caseNameSha256','xmlSha256','source')} for c in cases if c['class']==cls]
            rows.append(dict(siteId=before['siteId'],sourcePath=name,sourceSha256=digest,
                catchLine=before['beginLine'],catchVariable=before['catchVariable'],bodyTokenSha256=before['bodyTokenSha256'],
                originalInventorySha256=INVENTORY_SHA,currentWholeQualificationSha256=sha(qp),
                directClassRegressionRefs=direct,refScope='RELATED_REGRESSION_NOT_PER_SITE_FAULT_CAUSALITY',
                aggregateGuardLineCounter={k:int(node.get(k)) for k in ('ci','mi','cb','mb')} if node is not None else None,**decision))
    if len(rows)!=115 or sum(r['role']=='DIRECT_GUARD_BEFORE_MAPPING' for r in rows)!=56:
        raise ValueError('all115 explicit routes,56 direct and2 cleanup-before guards')
    out=BASE/'PG6638-current115-receivers-v1';os.umask(0o077);out.mkdir()
    value=dict(actualExit=0,source=q['productionSource'],sites=115,pgReviewedRoutes=115,
        roles=dict(Counter(r['role'] for r in rows)),rows=rows,acceptedSites=0,
        currentWholeTests=4158,currentWholeQualificationSha256=sha(qp),testsExecuted=0,
        sqlScopeOnly=True,nonSqlScopeNotExhaustive=True,formalAccepted=False,ptAlternativeCompleted=0,vmActions=0)
    target=out/'manifest.json'
    with target.open('x') as f:f.write(json.dumps(value,sort_keys=True,indent=2)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed115=True,acceptedSites=0,manifestSha256=sha(target))))


if __name__=='__main__':main()
