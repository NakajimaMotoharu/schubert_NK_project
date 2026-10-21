"""Twelve application failure-boundary spans; no business request or transaction is run."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine

G='AvoidCatchingGenericException'
SPEC={
 'UserMutationApplicationService':{
 (92,G):(1,'PermanentProtocolException has the preceding dedicated passthrough; other RTE becomes the fixed TemporaryInfrastructureException at the JMS business boundary. No raw provider text/cause is exposed or mutation success returned; direct Error is not caught. This applicability does not certify every compound TWR failure.'),
 (106,G):(1,'Owned short user-mutation SQL/RTE transaction rolls back before rethrow; commit is only after execute normally returns. Authentication/ADMIN gate, Inbox idempotency, audit and mutation remain in the same transaction, not retried directly here.'),
 (114,G):(1,'After owned connection TWR finishes, SQL/RTE becomes the fixed unconfirmed infrastructure boundary, never a success wire response. It does not acquire another connection or issue a second mutation; broker retry has separate Inbox rules.')},
 'UserQueryApplicationService':{
 (105,G):(1,'Saved request identity mismatch remains PermanentProtocolException via prior catch; other RTE becomes fixed temporary infrastructure failure. The outer query response cannot expose provider details or manufacture authorized/successful data.'),
 (273,G):(1,'Each own query/capture transaction handles SQL/RTE by rollback and original rethrow, then TWR closes the connection. readOnly is selected by the existing phase; no JDBC transaction spans response/file work. Direct Error is not converted by this catch.'),
 (281,G):(1,'Owned SQL/RTE failure after short transaction/cleanup becomes fixed TemporaryInfrastructureException, not an empty query or successful replay. Existing read-only authentication and completion identity checks precede result return.')},
 'LogQueryApplicationService':{
 (105,G):(1,'Permanent request identity mismatch is isolated before generic RTE mapping. Other application/response failures become fixed temporary transport failure rather than empty logs, success, or raw diagnostics. Direct Error is outside this catch.'),
 (263,G):(1,'Log query/capture SQL/RTE triggers rollback before rethrow; own TWR connection closes afterward. Only normal operation and commit can return value; read-only selection/ADMIN audit/idempotency stays unchanged.'),
 (271,G):(1,'Final SQL/RTE boundary withholds successful log reply and emits only fixed infrastructure exception. It neither logs payload nor performs business retry in this catch. All compound vendor failures remain separately testable and are not certified by rule applicability.')},
 'MediaApplicationService':{
 (92,G):(1,'PermanentProtocolException is explicitly rethrown before RTE classification. Media provider/response RTE becomes fixed TemporaryInfrastructureException; no invalid media/file capability, fallback successful body or raw path is emitted.'),
 (228,G):(1,'Owned short media inspection/completion transaction rolls back SQL/RTE before rethrow and TWR close. File preparation is between transactions, not under a database lock over I/O. Error is not caught by this clause and no compensating media transaction is issued.'),
 (245,G):(1,'Authentication/AccessRejected and Inbox identity mismatch have preceding dedicated branches that reject suppressed unknown cleanup as infrastructure. Remaining SQL/RTE becomes fixed temporary failure, not authorized media or a successful empty result.')}
}
TESTS={
 'UserMutationApplicationService':['dev.codex.schubert.nk.api.application.admin.UserMutationApplicationServiceTest'],
 'UserQueryApplicationService':['dev.codex.schubert.nk.api.application.admin.UserQueryApplicationServiceTest'],
 'LogQueryApplicationService':['dev.codex.schubert.nk.api.application.log.LogQueryApplicationServiceTest'],
 'MediaApplicationService':['dev.codex.schubert.nk.api.application.media.MediaApplicationServiceTest']}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6288-group-lookup-static-review-v1/manifest.json',
        'PLAN_SHA':'11a530449d3c3f1967a63be5c3a0ca090363555225dbf32aef72c08250e47d32','SPEC':SPEC,'TESTS':TESTS}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix='api:'"),('src/schubert-nk-web/src/test/java','src/schubert-nk-api/src/test/java'),
        ('len(decisions)!=33','len(decisions)!=12'),('all33 explicit','all12 explicit'),('reviewed=33','reviewed=12'),
        ('1338 individual ordinary Web','1339 individual ordinary API application')):
        if a not in raw:raise ValueError('explicit reviewed engine '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<12 ordinary API application spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['Rule applicability is not proof of every TWR compound cleanup/fatal outcome','remaining findings/current whole/native/CHR/451/global100/formal pending']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6290-application-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=12,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
