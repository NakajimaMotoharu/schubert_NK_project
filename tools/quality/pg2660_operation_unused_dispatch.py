"""New-only unused stage/place after signed host source; no publication/start."""
import json
import sys
import types
import pg2518_current_strict_candidate_dispatch as previous
from pg2658_operation_candidate_sources import sources, bind, TOOLS, BEFORE, CURRENT, REMOTE, production
from pg2659_operation_candidate_compile import TARGET
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous.STAGE)


def source():
    raw=bind(previous.source()).replace('pg2517-frozen','pg2659-frozen')
    old="['git','diff','--name-only','"+production()+"','--','src','pom.xml']"
    new="['git','diff','--name-only','2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0','HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']"
    if raw.count(old)!=1:raise ValueError('one complete selected candidate source boundary required')
    raw=raw.replace(old,new)
    compile(raw,'<new operation unused placement body>','exec');return raw


def runtime_namespace(candidate,before):
    if before.get('runtimeAlreadyRetired')is not True:raise ValueError('actual current retired required; no retirement replay')
    fn=types.FunctionType(previous.engine.runtime_namespace.__code__,
      {**previous.engine.__dict__,'CURRENT':CURRENT,'BEFORE':BEFORE,'TARGET':TARGET,
       'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'production':production,'sources':sources})
    return {**fn(candidate,before),'__file__':__file__}


def main():
    if sys.argv[1:]not in(['stage'],['place']):raise ValueError('distinct new-only stage/place required')
    candidate=json.loads((W/'pg2654-candidate-build-v1.safe.json').read_bytes())
    before=json.loads((W/'pg2656-current-a79-before-v1/manifest.safe.json').read_bytes())
    ns=runtime_namespace(candidate,before);exec(compile(source(),'<new unused candidate entry>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
