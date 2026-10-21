"""Fifteen ordinary question/query/file-owner spans; actual4048 references still pending."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine
from pg6326_web_graph_qualification import original_source

G='AvoidCatchingGenericException';I='AvoidInstanceofChecksInCatchClause'
SPEC={
 'QuestionSubmissionService':{
 (137,G):(1,'The request-owned decoded body closes/wipes before generic SQL/RTE maps to fixed infrastructure failure. The preceding permanent-error branch rejects suppressed cleanup uncertainty instead of claiming permanent valid result. This path returns no accepted question or invented retry receipt.'),
 (202,G):(1,'Submission SQL/RTE attempts the existing rollback and propagates through owned Connection TWR. A created acceptance escapes only after commit/close; subsequent SENT polling is outside that transaction. This applicability does not certify every arbitrary compound provider graph.'),
 (410,I):(1,'Only PostgreSQL23505 with the exact uq_questions_receipt_id server constraint may consume one of the three bounded receipt attempts. PSQLException type and nullable structured error are necessary to distinguish that specific collision from operation/message conflict or unrelated SQL failure; rollback/release of the savepoint precedes retry. Raw provider text is never exposed as a user result.'),
 (477,G):(1,'SENT proof is a separate short readOnly transaction; SQL/RTE attempts rollback and propagates before owned close. This catch cannot publish another QWK, retain a waiting DB transaction, or promote an unconfirmed message to SENT.'),
 (582,G):(1,'Retained-attempt audit SQL/RTE attempts rollback and rethrows through owned close. The fixed conflict/temporary code is not a new business acceptance or evidence that an earlier outbox send completed. No body/session/provider text is emitted by this catch.')},
 'QuestionWorkerService':{
 (138,G):(1,'Provider Runtime failure is deliberately distinct from AnswerBusinessException: before terminal delivery it is temporary; at the configured terminal delivery the existing fail transaction and pending-DLQ/SENT path applies. This generic provider boundary never constructs a successful answer; direct Error is not caught here, and final ACK still requires its separate durable proof.'),
 (150,G):(1,'Outer SQL/RTE maps to a fixed infrastructure failure while finally wipes the event wire. Permanent identity failure with suppressed cleanup uncertainty is handled separately. This does not authorize another business work copy, manufacture final ACK or expose provider body/cause.'),
 (660,G):(2,'Both unchecked work/setup-statement/commit spans must attempt rollback before rethrow and owned TWR close. Direct Error is rethrown, not converted to ordinary successful answer. The transaction and timeout statements are not held around the external provider call; arbitrary nested provider-error policy remains a separate contract.'),
 (663,G):(1,'Rollback RTE remains a secondary failure on the original and is never a committed work result. Original failure then propagates through Connection close; the catch does not repeat rollback, send a new dispatch or claim physical DB cleanup success.')},
 'QuestionQueryRepository':{
 (311,G):(1,'List projection SQL/RTE is mapped to a fixed temporary query error rather than returning partial records. The preceding explicit QuestionQueryException branch preserves a known result only with no suppressed resource failure. Statement/ResultSet are owned locally; the Connection remains borrowed and no repository commit/rollback occurs.'),
 (344,G):(1,'Detail SQL/RTE prevents incomplete/invalid/multiple-row or cleanup failure from becoming Optional.empty/success. Owned result/statement close through TWR; the caller owns the Connection and transaction. This classification does not bypass separate USER/ADMIN SQL binding or turn a temporary query error into authorization.')},
 'ScenarioFileWriter':{
 (134,G):(1,'Owned write/publish/verify StorageIo/RTE failure inspects request-local created/published state. Only an owned unpublished part is eligible for delete; unknown rename/fsync cleanup retains the reservation and returns fixed unavailable. No complete descriptor escapes from this catch.'),
 (145,I):(1,'Only unpublished StorageIoException.COLLISION returns the approved empty collision result. Runtime/unknown/published failures must not trigger another publication or quota release as a clean collision. The type-and-reason predicate distinguishes that exact checked storage contract, not a broad success exemption.'),
 (152,G):(1,'The outer StorageIo/RTE boundary includes directory/compound close failure and emits fixed unavailable without physical paths. A computed descriptor is returned only after owned TWR completion. Existing ready/part reservation retention is not real filesystem deletion or native completion evidence from this review.')}
}
TESTS={
 'QuestionSubmissionService':['dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest'],
 'QuestionWorkerService':['dev.codex.schubert.nk.api.application.question.QuestionWorkerServiceTest'],
 'QuestionQueryRepository':['dev.codex.schubert.nk.api.application.question.QuestionQueryRepositoryTest'],
 'ScenarioFileWriter':['dev.codex.schubert.nk.api.storage.ScenarioFileWriterTest']}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6342-application-boundary-static-review-v1/manifest.json',
        'PLAN_SHA':'632189381e772d0c344f932a0cb4e7c18af7bdb18646602aa7ba4d9dcb3b6498',
        'SPEC':SPEC,'TESTS':TESTS,'original_source':original_source}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix='api:'"),('src/schubert-nk-web/src/test/java','src/schubert-nk-api/src/test/java'),
        ('PG6268-outbox-failure-qualification-v1','PG6326-web-graph-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6326-web-graph-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf'),
        ('len(decisions)!=33','len(decisions)!=15'),('all33 explicit','all15 explicit'),('reviewed=33','reviewed=15'),
        ('rawFindings=1350','rawFindings=1356'),('1338 individual ordinary Web','1356 individual question/query/file owner')):
        if a not in raw:raise ValueError('one explicit current question/static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<15 current ordinary question/query/file spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['actual4048 semantic case binding pending; these suites not part of original89 selection',
        'all14 prior missing semantic refs unresolved','other317/global/F03/native/CHR/451 and arbitrary vendor compound graphs not certified']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6344-question-storage-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=15,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
