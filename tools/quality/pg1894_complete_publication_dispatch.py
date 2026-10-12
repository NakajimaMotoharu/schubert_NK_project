"""New direct entry only; matched actual exported helper/marker before ownership."""
import inspect
import pg1880_warning_publication_dispatch as prior
from pg1891_complete_publication_sources import sources,TOOLS,CLASS,bind
from pg1893_complete_publication_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1894-fixed-stage-v1'
STAGE=bind(prior.STAGE).replace('pg1880-fixed-stage-v1','pg1894-fixed-stage-v1')


def source():
    raw=bind(inspect.getsource(prior.main)).replace('pg1879-frozen','pg1893-frozen').replace('pg1880-','pg1894-')
    compile(raw,'<new actual complete publication entry>','exec');return raw


def main():
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<direct complete export publication>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
