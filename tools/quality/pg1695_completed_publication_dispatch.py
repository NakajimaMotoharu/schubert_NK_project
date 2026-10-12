"""New-only fixed ordinary publication, host gate, no service start/reload."""
import inspect
import pg1688_completed_candidate_ro_dispatch as previous
from pg1691_completed_ordinary_publication_sources import sources,TOOLS,CLASS

TARGET=previous.W/TOOLS
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=previous.STAGE.replace('pg1688-fixed-stage-v1','pg1695-fixed-stage-v1').replace('pg1686-completed-candidate-ro-tools-v1',TOOLS).replace('PG1688','PG1695')


def source():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg1687-frozen-v1.safe.json','pg1693-frozen-v1.safe.json'),('pg1685-unused-candidate-full-post-v1','pg1690-completed-candidate-ro-post-v1'),('pg1688-','pg1695-'),('Pg1686','Pg1691'),('prepare-ro','activate')]:raw=raw.replace(a,b)
    raw=raw.replace("'Pg1691InputBoundaryTest',CLASS+' activate'", "'Pg1691InputBoundaryTest','Pg1691TransitionTest',CLASS+' activate'")
    raw=raw.replace("'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False", "'ordinaryPublicationOnly':True,'currentApprovalEpochChanged':action=='activate'")
    compile(raw,'<new-only ordinary publication dispatcher>','exec')
    return raw


def main():
    ns={**previous.__dict__,'TARGET':TARGET,'GUEST':GUEST,'STAGE':STAGE,'TOOLS':TOOLS,'CLASS':CLASS,'sources':sources}
    exec(source(),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
