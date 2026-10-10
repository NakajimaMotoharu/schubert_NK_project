"""Readonly full current preflight plus actual private schema/oracle join after1062."""
import inspect
import pg1222_completed_retirement_preflight as previous
import pg1223_completed_runtime_contract as contract
from pg847_configuration import FIELDS

def payload():
    s=previous.payload().replace("'run':'PG1222-completed-retirement-preflight-v1'","'run':'PG1227-runtime-schema-preflight-v1'");marker='print(json.dumps(result))'
    if s.count(marker)!=1:raise ValueError('exact actual preflight result insertion required')
    c=inspect.getsource(contract).replace('from pg847_configuration import FIELDS','FIELDS='+repr(FIELDS))
    extra='\nimport copy,types\nretirement=types.ModuleType("actual_current_retirement");exec('+repr(c)+',retirement.__dict__)\n'+SCHEMA
    s=s.replace(marker,extra+'\n'+marker);compile(s,'<actual current runtime schema preflight>','exec');return s

SCHEMA=r'''
b=copy.deepcopy(after);candidate=copy.deepcopy(b)
require(retirement.TARGET not in b['unitFilesActual']and retirement.TARGET in b['runtime'])
candidate['runtime'].pop(retirement.TARGET)
old=candidate['runtime'][retirement.ROOT]['metadata'];old[6]=0
parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
n=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
env={'re':re};exec(compile(ast.Module(body=[n],type_ignores=[]),'<qualified declaration parser>','exec'),env)
parse=env['exec_record'];cfg=candidate['configuration'][retirement.MORNING]
record=parse(cfg['ExecStart']);require(record is not None and record[1].endswith(' --resume '+retirement.RUN))
plain=record[1][:-len(' --resume '+retirement.RUN)]
cfg['ExecStart']='{ path='+record[0]+' ; argv[]='+plain+' ; ignore_errors='+record[2]+' ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
cfg['DropInPaths']=' '.join(cfg['DropInPaths'].split()[:-1])
require(retirement.same_except_runtime(b,candidate,parse))
result.update(actualDisjointScopeOracle=True,unitFileCount=len(b['unitFilesActual']),runtimeEntryMetadataPinned=True,expectedCandidateOnlyNotActualRetired=True,startsStopsReloadsSqlWrites=0)
'''

def main():
    entry=inspect.getsource(previous.main).replace('pg1222-completed-retirement-preflight-v1','pg1227-runtime-schema-preflight-v1')
    env=dict(previous.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only actual disjoint schema preflight>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
