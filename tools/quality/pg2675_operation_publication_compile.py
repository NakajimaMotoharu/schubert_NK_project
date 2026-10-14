"""Whole host publication ABI after independent new candidate host RO."""
import inspect
import pg2533_strict_normal_publication_compile as previous
from pg2674_operation_publication_sources import sources,TOOLS,candidate_bom,bind,BEFORE,CURRENT,production

TARGET=previous.previous.prior.prior.W/TOOLS


def compiler(bom):
    raw=bind(previous.compiler(bom),bom)
    for a,b in [('pg2533-','pg2675-'),('pg2530-strict-candidate-ro-post-v1','pg2672-operation-ro-post-v1'),
      ('pg2517-frozen','pg2659-frozen'),('pg2516-current-strict-candidate-tools-v1','pg2658-operation-unused-tools-v1'),('Pg2516','Pg2658')]:raw=raw.replace(a,b)
    compile(raw,'<whole new operation publication ABI>','exec');return raw


def main():
    bom=candidate_bom();engine=previous.previous.prior.prior
    ns={**engine.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BOM':bom,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(engine.write),'<immutable operation publication writer>','exec'),ns)
    exec(compile(compiler(bom),'<new candidate complete publication ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
