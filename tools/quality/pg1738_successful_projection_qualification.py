"""Independent exact6 XML/current Test+Main/library/fixture/class qualification."""
import inspect
import pg1715_api_configuration_selected_qualification as prior

METHODS={'dev.codex.schubert.nk.batch.repository.MorningSuccessfulBackupProjectionTest:'+name for name in (
 'mdbProj1737001BothSqlOrdersReturnLiteralIdsAndNoMutation',
 'mdbProj1737002EmptyMeansNoReusablePairAndIncompleteOrExtraRowsReject',
 'mdbProj1737003EveryRequiredProjectionNullRejectsWithoutNpeOrLeak',
 'mdbProj1737004EachSemanticFieldCounterexampleRejects',
 'mdbProj1737005PairAttemptStartAndEndMustBeOneBundle',
 'mdbProj1737006EndAtObservationAndPositiveByteBoundaryRemainEligible')}

def server():
    raw=prior.server().replace('PG1715','PG1738').replace('1714','1737')
    raw=raw.replace("fixtures=source/'src/schubert-nk-api/target/test-classes'", "fixtures=source/'src/schubert-nk-batch/target/test-classes'")
    raw=raw.replace("results['1737']['tests']==5", "results['1737']['tests']==6")
    compile(raw,'<independent six SQL projection source qualifier>','exec');return raw

def main():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1715-api-configuration-selected-qualified-v1','pg1738-successful-projection-qualified-v1'),('pg1714-api-configuration-negative-selected-v1','pg1737-successful-backup-projection-selected-v1'),('pg1715-qualification','pg1738-qualification'),('PG1715-selected-qualification','PG1738-selected-qualification'),("{'1714':host['manifestSha256']}","{'1737':host['manifestSha256']}"),('host.get(\'tests\')!=5','host.get(\'tests\')!=6'),("len(expected) != 5","len(expected) != 6")]:
        if a not in raw:raise ValueError('one actual six qualifier join absent')
        raw=raw.replace(a,b)
    ns={**prior.__dict__,'server':server,'METHODS':METHODS}
    exec(compile(raw,'<exact current six independent qualification>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
