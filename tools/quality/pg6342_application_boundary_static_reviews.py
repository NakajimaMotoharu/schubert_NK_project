"""Eleven ordinary API application/borrrowed-TX applicability spans, not runtime acceptance."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine
from pg6326_web_graph_qualification import original_source

G='AvoidCatchingGenericException'
SPEC={
 'QuestionCommandService':{
 (196,G):(1,'Borrowed-Connection cancellation SQL/RTE maps to the fixed infrastructure catalog rather than returning CancelResult. The enclosing application transaction owns rollback/commit/close; this service must not close the borrowed Connection or issue a second command on failure. This catch does not grant a new owner or retry.'),
 (279,G):(1,'Borrowed logical-delete SQL/RTE cannot return the computed successful delete result. Fixed mapping carries no raw SQL/provider text; transaction ownership remains with the enclosing mutation facade. This applicability reason does not certify every compound Throwable graph or actual DB rollback.')},
 'QuestionMutationApplicationService':{
 (102,G):(1,'The outer request boundary preserves the preceding PermanentProtocolException branch and maps other RTE to fixed TemporaryInfrastructureException. No catch emits a fabricated mutation response or repeats commands; normally committed snapshots are replayed through the separate inspector/response path.'),
 (115,G):(1,'Mutation SQL/RTE within the acquired transaction attempts rollback and rethrows before TWR close. The outcome is returned only after commit and owned close. No JDBC ownership is transferred to the borrowed command service; arbitrary cleanup/provider Throwable combinations are not certified by this rule classification.'),
 (123,G):(1,'Outer acquisition/setup/body/commit/close SQL/RTE is a fixed infrastructure failure, not a successful mutation or payload echo. Objects.requireNonNull establishes the acquired Connection boundary; direct Error is not caught by this clause. This reason leaves separate fatal-graph domains and runtime evidence unproved.')},
 'QuestionQueryApplicationService':{
 (105,G):(1,'The public query boundary retains its explicit permanent identity-error branch, mapping only other RTE to fixed infrastructure failure. Responses are built from a completed stage/outcome, never from this exception branch. No query result, principal or authorization is fabricated on failure.'),
 (292,G):(1,'Read/write transaction helper rolls back its SQL/RTE work or commit failure, rethrows, and lets owned TWR close before any value escapes. The two transaction phases and readOnly parameter remain distinct; this review does not turn rollback attempt into observed physical success.'),
 (300,G):(1,'Outer SQL/RTE including setup/close is redacted to a fixed infrastructure type. It does not return a partially obtained list/detail or use old snapshots as current authorization. Direct Error remains outside this generic catch; compound provider semantics are a separate contract, not blanket approval.')},
 'ScenarioApplicationService':{
 (111,G):(1,'The request guard preserves explicit permanent identity violation before generic RTE mapping. A failed guard/run produces fixed infrastructure failure, not a scenario file descriptor or successful response. This exception boundary does not own or close external runtime services.'),
 (293,G):(1,'SQL/RTE in either selected transaction phase attempts existing rollback and rethrows before TWR cleanup. Normally obtained result must be nonnull, committed and closed before return; file preparation occurs in its separate existing stage. No catch starts additional file publication or business retry.'),
 (311,G):(1,'The final generic SQL/RTE clause follows specialized authentication/access and Inbox identity classifications. It redacts remaining uncertain failures rather than returning saved/physical file success; the preceding suppressed-failure checks are not bypassed. Actual file/native/DB postconditions and arbitrary fatal graphs remain separate.')}
}
TESTS={n:['dev.codex.schubert.nk.api.application.'+('scenario.'if n=='ScenarioApplicationService'else'question.')+n+'Test']for n in SPEC}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6338-outbox-graph-static-review-v1/manifest.json',
        'PLAN_SHA':'913d5fb156d4e7c99a679f4699b829bed01cab175fa06427c1769f871929499a',
        'SPEC':SPEC,'TESTS':TESTS,'original_source':original_source}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix='api:'"),('src/schubert-nk-web/src/test/java','src/schubert-nk-api/src/test/java'),
        ('PG6268-outbox-failure-qualification-v1','PG6326-web-graph-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6326-web-graph-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf'),
        ('len(decisions)!=33','len(decisions)!=11'),('all33 explicit','all11 explicit'),('reviewed=33','reviewed=11'),
        ('rawFindings=1350','rawFindings=1356'),('1338 individual ordinary Web','1356 individual ordinary API application')):
        if a not in raw:raise ValueError('one explicit current application/static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<11 current ordinary application spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['actual4048 semantic case binding pending; these four application suites are not part of original89 selected run',
        'all14 prior missing refs remain unresolved','other332/global/F03/native/CHR/451 and compound vendor semantics not certified']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6342-application-boundary-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=11,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
