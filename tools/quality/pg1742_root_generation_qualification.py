"""Independent current Root generation4 XML/class/byte/resource result join."""
import inspect
import pg1738_successful_projection_qualification as prior

METHODS={'dev.codex.schubert.nk.batch.platform.RootGenerationCounterexampleTest:'+n for n in (
 'rootgen1741001ApiAndWebGenerationControlsAreDataNotNewRootAdmission',
 'rootgen1741002ForeignCapturedTerminalClaimsRejectBeforeMissingProc',
 'rootgen1741003RecheckRejectsForeignBootInitAndSamePidNewTicks',
 'rootgen1741004TwoReadDisappearanceRacesNeverCertifyUnstablePid')}

def server():
    return prior.server().replace('PG1738','PG1742').replace('1737','1741').replace("results['1741']['tests']==6","results['1741']['tests']==4")

def main():
    raw=inspect.getsource(prior.main).replace('pg1738','pg1742').replace('PG1738','PG1742').replace('pg1737-successful-backup-projection-selected-v1','pg1741-root-generation-selected-v1').replace("{'1737':host['manifestSha256']}","{'1741':host['manifestSha256']}")
    raw=raw.replace("host.get(\\'tests\\')!=6", "host.get(\\'tests\\')!=4").replace('len(expected) != 6','len(expected) != 4')
    ns={**prior.__dict__,'METHODS':METHODS,'server':server}
    exec(compile(raw,'<exact current4 generation qualifier>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
