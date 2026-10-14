"""Host-only whole unused candidate ABI; current a79 and042 resources separate."""
import inspect
import types
import pg2517_current_strict_candidate_compile as previous
from pg2658_operation_candidate_sources import sources, bind, TOOLS, ARCHIVE as ARCHIVE_NAME, CURRENT, BEFORE, production

TARGET=previous.graph.engine.W/TOOLS
ARCHIVE=previous.graph.engine.P/ARCHIVE_NAME


def compiler():
    raw=bind(previous.compiler()).replace('pg2517-','pg2659-')
    for a,b in [('pg2459-frozen-v1','pg2555-frozen-v1'),('pg2458-question-current-owned-stop-tools-v1','pg2554-strict-current-owned-stop-tools-v1'),('Pg2458','Pg2554'),('pg2458','pg2554')]:raw=raw.replace(a,b)
    compile(raw,'<new unused whole ABI compiler>','exec');return raw


def validate_actual_graph(target,hashes):
    raw=inspect.getsource(previous.graph.validate_actual_graph).replace('pg2132','pg2658').replace('pg2126-manifest-v1.sig','pg2654-manifest-v1.sig')
    ns={**previous.graph.__dict__,'ARCHIVE':ARCHIVE}
    exec(compile(raw,'<new actual whole graph>','exec'),ns);return ns['validate_actual_graph'](target,hashes)


def main():
    graph=previous.graph
    ns={**graph.engine.__dict__,'__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,
      'TOOLS':TOOLS,'CURRENT':CURRENT,'PRODUCTION':production(),'BEFORE':BEFORE,
      'sources':sources,'validate_actual_graph':validate_actual_graph,'inventory':graph.inventory}
    ns['write']=types.FunctionType(graph.write.__code__,{**graph.__dict__,'TARGET':TARGET})
    exec(compile(compiler(),'<new host ABI entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
