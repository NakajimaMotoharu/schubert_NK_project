"""18 exact standalone lookup spans; source review only, never runs NSS or a process."""
import inspect
import json
import os
from collections import Counter
import pg6284_web_owned_static_reviews as engine
from static_disposition_overlay import apply_decisions,load

G='AvoidCatchingGenericException';I='AvoidInstanceofChecksInCatchClause';T='DoNotUseThreads'
SPEC={'ConfigurationGroupResolver':{
 (45,T):(1,'Standalone batch checks only current caller interrupt before acquisition. This is JavaSE fixed-process ownership, not a Jakarta EE thread container; the premise proves no process/Unit/VM ownership.'),
 (70,T):(1,'Private virtual-thread executor belongs to this one finite NSS lookup scope. It reads bounded stdout only and is closed before wiping the shared buffer. No application-server managed executor is borrowed.'),
 (74,T):(1,'Only the lookup-owned executor Future is borrowed into the nested TERM-before-join scope. Closing executor is distinct from process termination; neither is inferred from daemon or Future existence.'),
 (89,T):(1,'After all owned scopes finish, the current caller interrupt is rechecked before returning canonical GID. It is not an unsolicited mutation of another thread or evidence of successful lookup.'),
 (92,T):(1,'Caught InterruptedException restores the same current-thread interrupt before fixed IOException redaction. Missing/failed lookup never falls back to a target-derived GID.'),
 (113,T):(1,'When interrupted known primary is superseded by unknown cleanup, the current caller interrupt is restored first. This is a local JavaSE notification contract and no managed-thread scheduling policy.'),
 (107,G):(2,'Both unchecked work spans retain original identity while the explicit resource release is attempted once. Known IO/interruption differs from unknown Runtime/Error; nested owned scopes remain responsible for their own stdio/executor/process, not arbitrary external resources.'),
 (110,G):(2,'Both unchecked release-secondary spans preserve unknown-primary identity plus new fixed diagnostic. A known IO/interruption primary may be superseded by unknown cleanup; sameThrowable never becomes its own suppressed node because unavailable() is newly fixed.'),
 (111,I):(4,'Four overlapping predicates distinguish the established checked IOException/InterruptedException primary from unchecked cleanup. This is explicit failure-contract classification, not general business polymorphism; known-only cleanup remains fixed, unknown cleanup propagates.'),
 (112,I):(2,'The two overlapping IOException tests retain checked IO primary when cleanup is also IO. The rule does not authorize raw provider messages to escape the outer fixed lookup-unavailable boundary.'),
 (113,I):(2,'Both overlapping InterruptedException tests ensure interrupt restoration before propagating unknown cleanup. Unknown primary retains its original identity; the branch does not fabricate a canonical group result.')}
}
TESTS={'ConfigurationGroupResolver':['dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest']}
PLAN=engine.BASE/'PG6286-cleanup-static-review-v1/manifest.json'
PLAN_SHA='69276763b5ed88495e10aff8b2d1977aa67823e43beade9e79c5b2057e1593bc'


def calculate():
    scope={**vars(engine),'PLAN':PLAN,'PLAN_SHA':PLAN_SHA,'SPEC':SPEC,'TESTS':TESTS}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix='batch:'"),('src/schubert-nk-web/src/test/java','src/schubert-nk-batch/src/test/java'),
        ('len(decisions)!=33','len(decisions)!=18'),('all33 explicit','all18 explicit'),('reviewed=33','reviewed=18'),
        ('1338 individual ordinary Web','1339 individual standalone lookup')):
        if a not in raw:raise ValueError('explicit reviewed source engine '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<18 standalone lookup spans>','exec'),scope)
    rows,value=scope['calculate']()
    for row in rows:
        if row['rule']==T:row.update(status='CONTEXT_NOT_APPLICABLE',staticContextPremiseOnly=True)
    updated=apply_decisions(load(PLAN,PLAN_SHA,value['source']),rows)
    value['statusCounts']=dict(Counter(r['status']for r in updated))
    value['unresolved']=['source/static-only lookup review executes no NSS/process; actual ownership and remaining findings not certified']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6288-group-lookup-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=18,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
