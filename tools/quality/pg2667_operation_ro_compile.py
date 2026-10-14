"""Host-only whole candidate read-only assembly ABI after unused placement post."""
import inspect
import pg2525_strict_candidate_ro_compile as previous
from pg2666_operation_ro_sources import sources,TOOLS,bind
from pg2658_operation_candidate_sources import CURRENT,BEFORE,production

TARGET=previous.previous.prior.prior.prior.W/TOOLS


def compiler():
    raw=bind(previous.compiler()).replace('pg2525-','pg2667-').replace('pg2522-current-strict-candidate-post-v1','pg2664-operation-unused-post-v1').replace('pg2517-frozen','pg2659-frozen')
    compile(raw,'<new resource candidate readonly ABI>','exec');return raw


def main():
    engine=previous.previous.prior.prior.prior
    ns={**engine.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(engine.write),'<canonical operation RO writer>','exec'),ns)
    exec(compile(compiler(),'<new candidate readonly ABI entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
