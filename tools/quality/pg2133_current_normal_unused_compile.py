"""Host-only normal-completed current/new candidate ABI + exact whole generated graph freeze."""
import ast
import json
import re
from pathlib import PurePosixPath
import pg1642_completed_candidate_compile as engine
from pg1645_completed_candidate_compile_v2 import canonical_relative,inventory
from pg1861_warning_actual_graph_compile import compiler as previous_compiler
from pg2132_current_normal_unused_sources import sources,TOOLS,ARCHIVE as ARCHIVE_NAME,BEFORE,CURRENT,bind,production

TARGET=engine.W/TOOLS
ARCHIVE=engine.P/ARCHIVE_NAME

def write(path,raw):
    if path.is_relative_to(TARGET):
        canonical_relative(str(path.relative_to(TARGET)))
        path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    engine.write(path,raw)

def validate_actual_graph(target,hashes):
    raw=(target/'pg2132_input_preflight.py').read_text();tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'canonical','validate_graph'}or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='STANDARD'for t in n.targets)]
    if len(nodes)!=3:raise ValueError('exact whole graph declarations required')
    ns={'ast':ast,'re':re,'PurePosixPath':PurePosixPath}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual current complete graph>','exec'),ns)
    return ns['validate_graph'](hashes,{n:(target/n).read_text()for n in hashes if n.endswith('.py')},ARCHIVE.name,{ARCHIVE.name,'pg2126-manifest-v1.sig','bundle.safe.json'})

def compiler():
    raw=bind(previous_compiler())
    pairs=[('pg1861-','pg2133-'),('pg1834-frozen-v1','pg2091-frozen-v1'),('pg1833-warning-owned-stop-tools-v1','pg2090-current-newrun-owned-stop-tools-v1'),('Pg1833','Pg2090'),('pg1833','pg2090')]
    for old,new in pairs:raw=raw.replace(old,new)
    compile(raw,'<host normal-current whole ABI compiler>','exec');return raw

def main():
    before=json.loads((engine.W/'pg2130-current-normal-before-v1/manifest.safe.json').read_bytes())
    normal=before.get('genuineCompletion',{})
    if before.get('actualExit')!=0 or before.get('productionSource')!=CURRENT or before.get('privateBeforeSha256')!=BEFORE or before.get('allTenUnitsKernelEmpty')is not True or normal.get('genuinePid1StartDone')is not True or normal.get('normalUnit0or10')is not True or normal.get('currentManagerGc')is not True:
        raise ValueError('actual separately qualified normal-completed current required')
    ns={**engine.__dict__,'__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':TOOLS,'CURRENT':CURRENT,'PRODUCTION':production(),'BEFORE':BEFORE,'sources':sources,'validate_actual_graph':validate_actual_graph,'write':write,'inventory':inventory}
    exec(compile(compiler(),'<actual isolated whole ABI entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
