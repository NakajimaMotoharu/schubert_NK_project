"""New-only ordinary publication compiler on certified current ABI."""
import inspect
import pg1687_completed_candidate_ro_compile as previous
from pg1691_completed_ordinary_publication_sources import sources,TOOLS

TARGET=previous.engine.W/TOOLS


def write(path,raw):
    previous.canonical_relative(str(path.relative_to(TARGET)))
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    previous.engine.write(path,raw)


def compiler():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg1685-unused-candidate-full-post-v1','pg1690-completed-candidate-ro-post-v1'),('pg1682-frozen-v1.safe.json','pg1687-frozen-v1.safe.json'),('pg1681-completed-unused-tools-v4','pg1686-completed-candidate-ro-tools-v1'),("('Pg1640','Pg1660','Pg1681')","('Pg1686',)"),('Pg1686','Pg1691'),('pg1687-','pg1693-')]:raw=raw.replace(a,b)
    raw=raw.replace("('input','Pg1691InputBoundaryTest')", "('input','Pg1691InputBoundaryTest'),('transition','Pg1691TransitionTest')")
    raw=raw.replace("name.startswith(('Pg1691',))","name.startswith(('Pg1686',))")
    raw=raw.replace("prior=json.loads((engine.W/'pg1693-frozen-v1.safe.json').read_bytes())","prior=json.loads((engine.W/'pg1687-frozen-v1.safe.json').read_bytes())")
    compile(raw,'<new current ABI ordinary publication compiler>','exec')
    return raw


def main():
    ns={**previous.__dict__,'TARGET':TARGET,'write':write,'sources':sources}
    exec(compiler(),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
