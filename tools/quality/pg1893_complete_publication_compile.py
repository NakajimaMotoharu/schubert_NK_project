"""Same direct whole compiler, new source profile/immutable slot after recovery0."""
import inspect
import pg1879_warning_publication_compile as prior
from pg1891_complete_publication_sources import sources,TOOLS,bind

TARGET=prior.W/TOOLS


def main():
    raw=bind(inspect.getsource(prior.main)).replace('pg1879-','pg1893-').replace('pg1876-warning-candidate-ro-post-v1','pg1890-publication-recovery-full-post-v1')
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET}
    exec(compile(inspect.getsource(prior.write),'<new-only nested writer>','exec'),ns)
    exec(compile(raw,'<direct complete publication compiler>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
