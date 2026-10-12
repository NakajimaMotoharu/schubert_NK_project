"""Exact current generation8 independent XML/byte qualification, not old4 reuse."""
import inspect
import pg1742_root_generation_qualification as prior

METHODS=prior.METHODS|{'dev.codex.schubert.nk.batch.platform.RootGenerationCounterexampleTest:'+n for n in (
 'rootgen1741005AuthorityDriftAfterParentRecheckCannotAdmitChild',
 'rootgen1741006PidMinimumInvocationZeroAndChangingTicksReject',
 'rootgen1741007WrongDeadlineRoleCannotBorrowOtherUnitBudget',
 'rootgen1741008KernelStatusDelIsNotAllowedAscii')}

def server():
    return prior.server().replace('PG1742','PG1744').replace('1741','1743').replace("results['1743']['tests']==4","results['1743']['tests']==8")

def main():
    raw=inspect.getsource(prior.main).replace('pg1742','pg1744').replace('PG1742','PG1744').replace('pg1741-root-generation-selected-v1','pg1743-root-generation-boundaries-selected-v1').replace("{'1741':host['manifestSha256']}","{'1743':host['manifestSha256']}")
    raw=raw.replace("host.get(\\'tests\\')!=4", "host.get(\\'tests\\')!=8").replace('len(expected) != 4','len(expected) != 8')
    ns={**prior.__dict__,'METHODS':METHODS,'server':server}
    exec(compile(raw,'<current exact8 generation qualification>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
