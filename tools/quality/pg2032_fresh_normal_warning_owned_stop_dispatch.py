"""One staged current normal-warning owned stop. Same source, full fresh proof, no replay."""
import ast
import inspect
import os
import sys
import pg1826_state_configuration_owned_stop_dispatch as runner
from pg1835_readonly_parent_owned_stop_dispatch import STAGE as previous_stage,PARENT_PREQUAL as previous_prequal
from pg2025_fresh_resume_full_live_seal import payload as full_payload,SLOT as FULL_SLOT
from pg2030_fresh_normal_warning_owned_stop_sources import sources,context,SOURCE,TOOLS
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2032-fixed-stage-v1'
POST_SLOT=FULL_SLOT
STAGE=previous_stage.replace('pg1835','pg2032').replace('PG1835','PG2032').replace('pg1833','pg2030').replace('Pg1833','Pg2030')
STAGE=STAGE.replace('pg2030-warning-owned-stop-tools-v1',TOOLS)
PARENT_PREQUAL=previous_prequal.replace('pg1833','pg2030')
PARENT_PREQUAL=PARENT_PREQUAL.replace("{'managerFailureRetained':True,'genuinePid1StartDone':False,'stopAuthority':False}","{'currentManagerGc':True,'normalUnit0or10':True,'stopAuthority':False}")
PARENT_PREQUAL=PARENT_PREQUAL.replace("'managerFailureRetained':True,'genuinePid1StartDone':False","'currentManagerGc':True,'normalUnit0or10':True")


def post_payload():
    binding=runner.json.loads((W/'pg2019-fresh-resume-live-binding-complete-v1/manifest.safe.json').read_bytes())['binding']
    return full_payload(binding)


def run_action(action):
    raw=inspect.getsource(runner.run_action)
    old="post['guest']['privateBeforeSha256']!=before"
    if raw.count(old)!=1:raise ValueError('one actual current fullpost envelope boundary required')
    raw=raw.replace(old,"post['privateBeforeSha256']!=before")
    raw=raw.replace("'managerFailureRetained':True","'oldRoot13ManagerFailureRetained':True,'normalUnit0or10':True,'currentManagerGc':True")
    raw=raw.replace('pg1828-state-configuration-fresh-whole-v1','pg2034-fresh-normal-warning-pre-stop-full-v1')
    tree=ast.parse(raw)
    class Profile(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is not str:return node
            value=node.value.replace('pg1825','pg2031').replace('pg1826','pg2032').replace('pg1827','pg2033').replace('Pg1821','Pg2030').replace('PG1638','PG1846')
            return ast.copy_location(ast.Constant(value),node)
    tree=Profile().visit(tree);ast.fix_missing_locations(tree)
    namespace={**runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'W':W,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(tree,'<current normal warning once stop transport>','exec'),namespace);return namespace['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('fixed new stage/stop only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
