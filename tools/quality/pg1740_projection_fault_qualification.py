"""Current exact7 provider fault and literal projection XML/byte qualification."""
import inspect
import pg1738_successful_projection_qualification as prior

METHODS=prior.METHODS|{'dev.codex.schubert.nk.batch.repository.MorningSuccessfulBackupProjectionTest:mdbProj1737007AllowedJdbcFailuresAndUnknownProviderIdentityCloseEveryResource'}

def server():
    return prior.server().replace('PG1738','PG1740').replace('1737','1739').replace("results['1739']['tests']==6","results['1739']['tests']==7")

def main():
    raw=inspect.getsource(prior.main).replace('pg1738','pg1740').replace('PG1738','PG1740').replace('pg1737-successful-backup-projection-selected-v1','pg1739-successful-backup-fault-selected-v1').replace("{'1737':host['manifestSha256']}","{'1739':host['manifestSha256']}")
    raw=raw.replace("host.get(\\'tests\\')!=6", "host.get(\\'tests\\')!=7").replace("len(expected) != 6", "len(expected) != 7")
    # The old definition still builds its join from prior.main (API5), so update
    # both replacement literals and replacement values to exactly seven.
    ns={**prior.__dict__,'METHODS':METHODS,'server':server}
    exec(compile(raw,'<new-only current7 projection fault qualifier>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
