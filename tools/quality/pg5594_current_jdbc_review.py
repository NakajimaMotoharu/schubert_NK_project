"""Fresh same-source exact approved JDBC precedence; other catches remain unresolved."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg3940_jdbc_finally_contract_review import SPECS,DOC
from pg5590_current_static_projection import ROOT,W,BASE,SOURCE,suite_refs

FACTS='f19448f741d78ef78472744f45dc07f4e0427943a1c46260c7538810b6ee9a33'
OUT=BASE/'PG5594-current-jdbc-review-v1'
BROAD={'java.lang.Exception','java.lang.RuntimeException','java.lang.Error','java.lang.Throwable','java.lang.NullPointerException'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def assess(original,facts,cases,whole,design):
    if not(original['source']==facts['source']==whole['productionSource']==SOURCE and original['actualExit']==facts['actualExit']==0
        and whole['tests']==3905 and whole['mainClasses']==1664 and whole['FESFlakyNotRun']==0):raise ValueError('same current source/raw report/typed facts/genuine whole required')
    current={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if facts['identity']['sourceHashes']!=current or facts['identity']['physicalMainSha256']!=whole['allPhysicalMainSha256']:raise ValueError('all849/1664 exact current typed inputs and whole Main')
    catches=facts['results']['SourceCatchContextInventory']['rows'];jdbc=facts['results']['SourceJdbcClosePrecedenceInventory']['rows']
    rows=copy.deepcopy(original['findings']);joined=0;generic_sites=set();reviewed_finally=set();reviewed_secondary=set();seen_specs=set()
    for row in rows:
        path=row['sourcePath'];line=int(row['beginline']);name=Path(path).stem
        if row['sourceSha256']!=current[path]:raise ValueError('current individual finding source')
        if row['rule']=='AvoidCatchingGenericException':
            match=[c for c in catches if c['path']==path and int(c['firstLine'])<=line<=int(c['lastLine'])]
            if len(match)!=1 or not(set(match[0]['type'].split('|'))&BROAD):raise ValueError('every raw generic warning must join one exact typed catch')
            fact=match[0];row.update(genericCatchFacts=fact,catchFactsAloneAreNotDisposition=True);joined+=1;generic_sites.add((path,fact['start'],fact['end']))
        if name not in SPECS or '/batch/repository/'not in path:continue
        candidates=[f for f in jdbc if f['path']==path and int(f['firstLine'])<=line<=int(f['lastLine'])]
        if row['rule']=='DoNotThrowExceptionInFinally':candidates=[f for f in candidates if int(f['firstLine'])==line]
        elif row['rule']!='AvoidCatchingGenericException':continue
        if not candidates:continue
        if len(candidates)!=1:raise ValueError('one exact approved finally shape per assessed row')
        shape=candidates[0]
        if row['rule']=='AvoidCatchingGenericException':
            fact=row['genericCatchFacts']
            if set(fact['type'].split('|'))!={'java.sql.SQLException','java.lang.RuntimeException','java.lang.Error'}:raise ValueError('only exact approved secondary catch types')
            reviewed_secondary.add(row['findingId'])
        else:reviewed_finally.add(row['findingId'])
        owning='dev.codex.schubert.nk.batch.repository.'+name+'Test'
        expected=owning+'#'+SPECS[name]
        refs=suite_refs(cases,[name+'Test'])
        matched=[c for c in cases if c['class']==owning and c['caseNameSha256']==sha(SPECS[name].encode())]
        if len(matched)!=1 or matched[0]['result']!='PASS_ORIGINAL_XML':raise ValueError('current original compound-failure owning case required')
        row.update(status='REQUIRED_CONTRACT',reason='SS332/SSC063199 requires direct close-once with unknown/SQL primary-secondary precedence. Compiler proves exact capture, close receiver, three caught types, same secondary identity and JdbcResourceFailures.replace decision. Current independent compound-failure XML attached; not a generic catch waiver.',
            typedJdbcFact=shape,owningCase=expected,wholeCaseRefs=refs,approvedDesign=design,rawWarningRetained=True)
        seen_specs.add(name)
    expected_count=original['pmd']['ruleCounts']['AvoidCatchingGenericException']
    if joined!=expected_count or len(reviewed_finally)!=26 or len(reviewed_secondary)!=52 or seen_specs!=set(SPECS):raise ValueError('all raw generic rows and exact reviewed26 finally/52 secondary catch rows; no missing/extra approval')
    return rows,{'genericRawRowsJoined':joined,'distinctGenericCatchSites':len(generic_sites),'jdbcFinallyAssessed':len(reviewed_finally),'jdbcSecondaryWarningsAssessed':len(reviewed_secondary),
        'genericCatchFactsAloneAccepted':0,'newRuleSuppression':0,'unreviewedJdbcShapesRemainOpen':True}


def main():
    raw=(W/'pg5592-current-failure-facts-v1/manifest.safe.json').read_bytes()
    if sha(raw)!=FACTS:raise ValueError('immutable genuine typed current facts')
    original_path=BASE/'PG5590-current-static-findings-v1/manifest.json';original=json.loads(original_path.read_bytes())
    whole_path=BASE/'PG5588-current3905-cases/qualification.json';whole=json.loads(whole_path.read_bytes());cases=json.loads(whole_path.with_name('cases.json').read_bytes())
    approved=subprocess.check_output(['git','show','origin/main:'+DOC],cwd=ROOT)
    if approved!=(ROOT/DOC).read_bytes()or b'SSC063'not in approved or b'SSC199'not in approved:raise ValueError('approved exact current SS332 precedence, no implementation convenience change')
    design={'path':DOC,'originMain':subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),'sha256':sha(approved),'basis':'SSC063/SSC199'}
    rows,counts=assess(original,json.loads(raw),cases,whole,design)
    statuses={s:sum(r['status']==s for r in rows)for s in sorted({r['status']for r in rows})}
    value={'actualExit':0,'source':SOURCE,'findings':rows,'rawFindings':len(rows),'statusCounts':statuses,'typedBindingCounts':counts,
        'currentProjectionSha256':sha(original_path.read_bytes()),'currentWholeSha256':sha(whole_path.read_bytes()),'typedFactsSha256':FACTS,'approvedDesign':design,
        'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'vmActions':0,'productionChanges':0,'wholeReplayed':False}
    os.umask(0o077);OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'rawFindings':len(rows),'statusCounts':statuses,'typedBindingCounts':counts,'sha256':sha((OUT/'manifest.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
