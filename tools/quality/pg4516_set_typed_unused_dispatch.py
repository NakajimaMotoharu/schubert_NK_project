"""Newv5 same artifact stage/inspect/place; old142 and failed jobs stay immutable."""
import json
import subprocess
import sys
from pyflakes.api import check
import pg4462_failed_unused_dispatch as previous
import pg4498_set_typed_unused_sources as role
from pg4434_current_candidate_admission_read import authenticate_host
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P
from pg4514_metadata_only_recover import complete

TARGET=role.W/role.TOOLS;GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
DESIGN_MAIN='b65d1283e9dc384f761899bc8448cd50b9f572fc'


def stage_source():
    raw=role.role_text(previous.stage_source())
    marker='/home/ubuntu/pg4462-fixed-stage-v1/'
    if raw.count(marker)!=1:raise ValueError('one stage-consumer physical transfer path')
    return raw.replace(marker,'/home/ubuntu/pg4516-fixed-stage-v1/',1)


def source():
    raw=role.role_text(previous.source()).replace('pg4462-','pg4516-').replace('pg4460-frozen-v1.safe.json','pg4500-frozen-v1.safe.json')
    old="if not stage_qualified(json.loads((W/'pg4468-existing-input-stage-v1/manifest.safe.json').read_bytes())):raise ValueError('actual same142 existing-input consumer required; original stage1 preserved')"
    new="if(W/'pg4516-stage-v1.exit').read_bytes()!=b'0\\n':raise ValueError('genuine newv5 stage0 required')"
    if raw.count(old)!=1:raise ValueError('one new stage prerequisite, no original stage replay')
    raw=raw.replace(old,new,1)
    compile(raw,'<newv5 explicit stage-inspect-place>','exec');return raw


def runtime_namespace(candidate):
    namespace=previous.runtime_namespace(candidate)
    namespace.update(__file__=__file__,TARGET=TARGET,GUEST=GUEST,REMOTE=role.REMOTE,STAGE=stage_source(),sources=role.sources)
    return namespace


def main():
    if sys.argv[1:]not in [['stage'],['inspect'],['place']]:raise ValueError('one explicit finite action')
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    recovered=json.loads((role.W/'pg4514-metadata-only-recover-v1/manifest.safe.json').read_bytes())
    if recovered['actualExit']!=0:raise ValueError('original recovery must genuinely finish first')
    complete(recovered['result']);role.qualify();authenticate_host()
    candidate=json.loads((role.W/'pg4432-candidate-build-v1.safe.json').read_bytes());namespace=runtime_namespace(candidate);raw=source()
    if 'management_gate'in raw:raise ValueError('no nested management gate')
    if check("DIGEST='fixed-stage-digest'\nFILES={}\n"+stage_source(),'<complete newv5 stage>'):raise ValueError('all emitted static0')
    exec(compile(raw,'<newv5 explicit finite operator>','exec'),namespace)
    with management_gate(P/'current-management-critical.lock'):return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
