"""Existing own ordinary API lifecycle plus one default-bind literal Test; no business startup."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6780_web_management_result_selected as prior
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6822_api_stop_result_equivalence import OLD,MAIN,verify_source

TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementDefaultBindTest.java'
SLOT='pg6824-api-management-result-selected-v1'
EXPECTED=(30,11)


def inventory():
    return profile.inventory({'api':{'api.bootstrap.ApiManagementServerTest','api.bootstrap.ApiManagementBindTest','api.bootstrap.ApiManagementStopTest','api.bootstrap.ApiManagementDefaultBindTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={MAIN,TEST}:raise ValueError('one API Main/one new Test only, all old oracles fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('all quality/build/Current inputs fixed')
    verify_source()


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source);cases,_=inventory()
    return prior.qualification_definition()(source,run,cases,EXPECTED,{MAIN},
      BASE/'PG6808-web-correlation-original-v2/manifest.json','ad152991b2814cafd19cd68df220dad45b90d9acc6d9467ab0d3559bfacca31b',
      W/'pg6808-web-correlation-original-v2/manifest.safe.json',W/'pg6808-web-correlation-original-v2/findings.safe.json',
      'pg6826-api-management-result-original-v1','PG6826-api-management-result-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'))
    if p.parse_args().action=='read':return read_original()
    cases,counts=inventory();scope={**vars(profile),'runner':prior.runner}
    exec(compile(inspect.getsource(profile.execute),'<ordinary API1669 finite profile>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'api':['api/bootstrap/ApiManagementServer']})


if __name__=='__main__':main()
