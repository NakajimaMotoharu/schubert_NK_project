"""New-only compiler of BUG1213 normal setting graph; no guest mutation."""
import inspect
import types
import pg2133_current_normal_unused_compile as prior
from pg2144_normal_unused_fixed_sources import sources,bind,TOOLS,ARCHIVE as ARCHIVE_NAME

TARGET=prior.engine.W/TOOLS
ARCHIVE=prior.engine.P/ARCHIVE_NAME


def compiler():return bind(prior.compiler()).replace('pg2133-','pg2145-')


def main():
    post=__import__('json').loads((prior.engine.W/'pg2142-current-normal-pair-recovery-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['candidateNotPlaced']is not True:raise ValueError('current recovered full post required')
    ns={**prior.__dict__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':TOOLS,'sources':sources,'compiler':compiler}
    ns['write']=types.FunctionType(prior.write.__code__,ns)
    raw=bind(inspect.getsource(prior.validate_actual_graph))
    exec(compile(raw,'<current fixed normal graph validator>','exec'),ns)
    ns['validate_actual_graph']=ns['validate_actual_graph']
    exec(compile(inspect.getsource(prior.main),'<new-only normal fixed compiler>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
