"""Only exact typed identity/addSuppressed findings; unrelated equality stays open."""
import copy
import hashlib
import json
import os
from pathlib import Path
from pg5590_current_static_projection import ROOT,W,BASE,SOURCE,suite_refs

OUT=BASE/'PG5690-current-identity-review-v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def assess(original,facts,whole,cases):
    if not(original['source']==facts['source']==whole['productionSource']==SOURCE and type(facts['actualExit'])is int and facts['actualExit']==0
      and facts['independentJdkFixtureExit']==facts['compileExit']==0 and whole['tests']==3905 and whole['mainClasses']==1664
      and whole['FESFlakyNotRun']==0 and facts['identity']['physicalMainSha256']==whole['allPhysicalMainSha256']):raise ValueError('current genuine3905/source/all1664/typed fixture first')
    if facts['helperSha256']!=sha((ROOT/'tools/quality/SourceSuppressionIdentityInventory.java').read_bytes())or facts['fixtureSha256']!=sha((ROOT/'tools/quality/source_suppression_identity_inventory_test.py').read_bytes()):raise ValueError('actual narrow typed helper and independent JDK fixture')
    current={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if current!=facts['identity']['sourceHashes']:raise ValueError('all849 typed Main source fixed')
    index={}
    for fact in facts['rows']:
        if fact['kind']!='SELF_SUPPRESSION_GUARD':raise ValueError('only narrow compiler self-suppression facts')
        key=(fact['path'],int(fact['firstLine']),int(fact['firstColumn']))
        if key in index:raise ValueError('no ambiguous typed guard coordinate')
        index[key]=fact
    rows=copy.deepcopy(original['findings']);reviewed=[];unmatched=[]
    for row in rows:
        if row['rule']!='CompareObjectsWithEquals'or row['status']!='NOT_REVIEWED':continue
        key=(row['sourcePath'],int(row['beginline']),int(row['begincolumn']))
        if key not in index:unmatched.append(row['findingId']);continue
        fact=index[key]
        # PMD end column is exclusive; compiler probe explicitly records end-1.
        if row['sourceSha256']!=current[fact['path']]or int(row['endline'])!=int(fact['lastLine'])or int(row['endcolumn'])!=int(fact['lastColumn'])+1:raise ValueError('one exact PMD/compiler source span')
        name=Path(row['sourcePath']).stem
        suites={'OutboxJmsSender':['OutboxDispatcherTest','OwnedOutboxDispatcherTest'],'LocalLogoutHandler':['LogoutControllerTest']}.get(name,[name+'Test'])
        refs=suite_refs(cases,suites)
        module=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-');member=row['sourcePath'].split('/src/main/java/',1)[1][:-5]
        classes={k:v for k,v in whole['allPhysicalMainSha256'].items()if k==module+':'+member+'.class'or k.startswith(module+':'+member+'$')}
        if not classes:raise ValueError('exact current owning physical Main classes')
        row.update(status='REQUIRED_CONTRACT',reason='Throwable.addSuppressed rejects self by reference identity, not equals. Compiler proves exact Throwable operands guard the same addSuppressed call without reassignment/field mutation/lambda escape. Independent JDK fixture uses distinct equals-true Throwables and same-identity rejection. Applies only this exact typed span; no request/Thread/value comparison exemption.',
          typedSelfSuppressionFact=fact,currentPhysicalClasses=classes,wholeCaseRefs=refs,
          independentContractFixture='source_suppression_identity_inventory_test.IdentityFacts.test_exact_guards_and_jdk_self_suppression',rawWarningRetained=True)
        reviewed.append(row['findingId'])
    return rows,{'individualSelfSuppressionGuards':len(reviewed),'reviewedFindingIds':reviewed,'otherEqualityStillUnreviewed':unmatched,'typedFactsAloneGrantNoBlanketExemption':True}


def main():
    path=W/'pg5689-current-identity-facts-v1/manifest.safe.json';raw=path.read_bytes();facts=json.loads(raw)
    if sha(raw)!='21a9d5a8c8e01e9aca8429e1487a87a9de21cf2f3fb00c7cf44e15540f332b1e':raise ValueError('immutable original actual typed facts')
    old=BASE/'PG5594-current-jdbc-review-v1/manifest.json';whole_path=BASE/'PG5588-current3905-cases/qualification.json'
    if sha(old.read_bytes())!='182ec34e330a61e46150de80676da82fa1197ca6b477b954250a17488103dfc9':raise ValueError('immutable original current1647 review')
    whole=json.loads(whole_path.read_bytes());cases=json.loads(whole_path.with_name('cases.json').read_bytes())
    rows,counts=assess(json.loads(old.read_bytes()),facts,whole,cases)
    value={'actualExit':0,'source':SOURCE,'findings':rows,'rawFindings':len(rows),'statusCounts':{s:sum(r['status']==s for r in rows)for s in sorted({r['status']for r in rows})},
      'identityReview':counts,'typedFactsSha256':sha(raw),'previousReviewSha256':sha(old.read_bytes()),'currentWholeSha256':sha(whole_path.read_bytes()),
      'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'productionChanges':0,'vmActions':0,'wholeReplayed':False}
    os.umask(0o077);OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'statusCounts':value['statusCounts'],'reviewedIdentityGuards':counts['individualSelfSuppressionGuards'],'sha256':sha((OUT/'manifest.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
