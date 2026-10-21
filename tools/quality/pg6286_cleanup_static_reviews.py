"""32 batch-owned-scope spans, without running cleanup or approving the other transaction catch."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine

G='AvoidCatchingGenericException';I='AvoidInstanceofChecksInCatchClause'
SPEC={
 'StepCleanupService':{
 (100,G):(2,'Both unchecked transaction-body spans retain the primary. Before durable commit, rollback must complete before autoCommit restoration; after committed=true, no fictitious rollback of a durable chunk occurs. Caller owns connection disposal; service does not close/reopen it. Mutation gate precedes transaction and surrounds actual commit.'),
 (105,G):(2,'Both unchecked rollback/restoration-secondary spans implement SS341/BUG193 primary/secondary policy. Unknown primary identity outranks cleanup; known primary with unknown cleanup propagates that unknown identity. Known-only failures become fixed DATABASE_FAILURE. No failed rollback permits restoration/success.'),
 (107,I):(2,'Error primary is unknown and must retain its original identity on SQL/RTE/Error cleanup failure. The two overlapping analyzer occurrences are preserved; a fresh fixed CleanupStoppedException is secondary rather than raw provider diagnostics.'),
 (108,I):(2,'Runtime primary is separated from known BatchRepositoryException/CleanupStoppedException subclasses before exception mapping. Generic Runtime is not always a retryable database error and cannot be blanket-wrapped.'),
 (109,I):(2,'BatchRepositoryException is a known fixed repository failure, excluded from the unknown-Runtime branch. This predicate is the explicit class contract, not polymorphic business behavior requiring visitor substitution.'),
 (110,I):(2,'CleanupStoppedException is a known enumerated stop reason, not arbitrary unknown runtime. The distinct known-vs-unknown classification preserves identity/redaction without claiming that a stopped batch succeeded.'),
 (114,I):(2,'With known primary, cleanup Error remains the same fatal object. It cannot be mapped to ordinary fixed DATABASE_FAILURE; earlier unknown-primary handling has already retained its own identity by contract.'),
 (115,I):(2,'With known primary, only unknown cleanup Runtime propagates as itself. Known repository/stop subclasses are excluded by the following narrow type predicates. Restoration and durable-success claims are withheld.'),
 (116,I):(2,'Cleanup BatchRepositoryException is known by the established fixed contract; its provider diagnostics must not replace the fixed DATABASE_FAILURE summary. This is not catch-all suppression of arbitrary failures.'),
 (117,I):(2,'Cleanup CleanupStoppedException is known and fixed; unknown subclass category is excluded before final mapping. The source still throws non-success and leaves caller responsible for connection disposal.')},
 'LogCleanupService':{
 (110,G):(2,'Both unchecked action spans in owned(release,action) release exactly the acquired scope once before original failure propagates. Success returns only after release normally completes. Borrowed parent connection is not closed by this helper.'),
 (113,G):(2,'Both unchecked release-secondary spans apply the established batch known/unknown and fixed-diagnostic precedence through replace. Unknown primary is retained by identity with a new fixed secondary, including same-Throwable reentry; no raw secondary graph or false success is emitted.'),
 (203,G):(2,'Both unchecked advisory-acquire row-body spans retain primary before direct ResultSet close. Missing/null/duplicate lock projection is non-success; acquired tracks the actual boolean, not success inferred from query execution. Original batch lock gate/SQL remains unchanged.'),
 (213,G):(2,'Both unchecked advisory-acquire statement-body spans retain primary before one direct Statement close, including ResultSet cleanup failure. The acquired session lease remains under the enclosing owner; this source review does not establish actual current advisory ownership.'),
 (241,G):(2,'Both unchecked advisory-release row-body spans retain failure until ResultSet closes. The row must explicitly prove a single true release; empty/false/multiple rows are rejected, not treated as unlocked success.'),
 (251,G):(2,'Both unchecked advisory-release statement-body spans preserve the established fixed/unknown mapping while always closing this Statement. Borrowed connection ownership and failed-transaction disposal requirement remain unchanged; actual DB lock release requires separate runtime evidence.')}
}
TESTS={name:['dev.codex.schubert.nk.batch.cleanup.'+name+'Test']for name in SPEC}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6284-web-owned-static-review-v1/manifest.json',
        'PLAN_SHA':'38fb05f2ed00f927007b1ce1b7093e096838aee5ffbbfeb6694622ffe9ecfb10','SPEC':SPEC,'TESTS':TESTS}
    raw=inspect.getsource(engine.calculate)
    for a,b in (("prefix='web:'","prefix='batch:'"),('src/schubert-nk-web/src/test/java','src/schubert-nk-batch/src/test/java'),
        ('len(decisions)!=33','len(decisions)!=32'),('all33 explicit','all32 explicit'),('reviewed=33','reviewed=32'),
        ('1338 individual ordinary Web','1339 individual ordinary batch')):
        if a not in raw:raise ValueError('explicit reviewed engine substitution '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<32 batch owned scopes>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['LogCleanupService transaction catch line168 remains unreviewed; this owned-resource review does not certify all rollback paths','whole/native/CHR/451/global100/other individual findings pending']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6286-cleanup-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=32,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
