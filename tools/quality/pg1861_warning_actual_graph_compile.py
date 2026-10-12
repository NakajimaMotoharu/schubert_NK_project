"""BUG1182: execute actual graph with every declared global before frozen acceptance."""
import ast
import inspect
import re
from pathlib import PurePosixPath
import pg1856_warning_nested_unused_compile as prior
from pg1860_warning_actual_graph_sources import sources,TOOLS,ARCHIVE,bind

TARGET=prior.prior.engine.W/TOOLS
INPUT_ARCHIVE=prior.prior.engine.P/ARCHIVE


def validate_actual_graph(target,hashes):
    raw=(target/'pg1860_input_preflight.py').read_text();tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'canonical','validate_graph'}or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='STANDARD'for t in n.targets)]
    if len(nodes)!=3:raise ValueError('all actual input graph declarations required')
    namespace={'ast':ast,'re':re,'PurePosixPath':PurePosixPath}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual graph complete declared globals>','exec'),namespace)
    return namespace['validate_graph'](hashes,{n:(target/n).read_text()for n in hashes if n.endswith('.py')},INPUT_ARCHIVE.name,{INPUT_ARCHIVE.name,'pg1846-manifest-v1.sig','bundle.safe.json'})


def compiler():return bind(prior.compiler()).replace('pg1856-','pg1861-')


def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'TARGET':TARGET,'ARCHIVE':INPUT_ARCHIVE,'TOOLS':TOOLS,'sources':sources,'validate_actual_graph':validate_actual_graph,'compiler':compiler}
    # prior.write refers to its module TARGET; bind that actual dependency by a
    # fresh function namespace, not by modifying the old module or old slot.
    writer=inspect.getsource(prior.write);exec(compile(writer,'<actual canonical nested writer>','exec'),ns)
    exec(compile(raw,'<new-only actual graph freeze>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
