"""Existing independent own Web lifecycle fixtures; no actual admission or deployment."""
import argparse
import ast
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6054_expiry_read_qualification as original
from pg5940_private_lock_compile import ROOT,W,BASE

OLD='d549f8855fe1733bdb67543e310048dc271a8a56'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java'
SLOT='pg6780-web-management-result-selected-v1'
EXPECTED=(28,10)


def inventory():
    return profile.inventory({'web':{'web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest','web.bootstrap.WebRuntimeStopTest'}},EXPECTED)


def guard(source):
    changed=subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines()
    if changed!=[MAIN]:raise ValueError('one Web Main only, every old oracle unchanged')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('quality/build/Current fixed')


def runner(total,suites,targets):
    raw=profile.runner(total,suites,targets)
    if raw.count('len(physical)==1667')!=1:raise ValueError('one exact physical1669 guard')
    return raw.replace('len(physical)==1667','len(physical)==1669',1)


def qualification_definition():
    tree=ast.parse(inspect.getsource(original.qualify))
    if sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==1667 for x in ast.walk(tree))!=3:
        raise ValueError('three exact physical1669 count positions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant(1669),node)if type(node.value)is int and node.value==1667 else node
    scope={**vars(original)}
    exec(compile(ast.fix_missing_locations(Counts().visit(tree)),'<existing1669 Web original qualifier>','exec'),scope)
    return scope['qualify']


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source);cases,_=inventory()
    return qualification_definition()(source,run,cases,EXPECTED,{MAIN},
      BASE/'PG6766-transfer-io-original-v2/manifest.json','ca1b4171ac208630189b42c6aa54f4d89b7306e29d73433c8ed55b202ba0535d',
      W/'pg6766-transfer-io-original-v2/manifest.safe.json',W/'pg6766-transfer-io-original-v2/findings.safe.json',
      'pg6782-web-management-result-original-v1','PG6782-web-management-result-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'));action=p.parse_args().action
    if action=='read':return read_original()
    from pg6781_web_stop_result_equivalence import verify_source
    verify_source()
    cases,counts=inventory();scope={**vars(profile),'runner':runner}
    exec(compile(inspect.getsource(profile.execute),'<existing1669 Web finite profile>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'web':['web/bootstrap/WebManagementServer']})


if __name__=='__main__':main()
