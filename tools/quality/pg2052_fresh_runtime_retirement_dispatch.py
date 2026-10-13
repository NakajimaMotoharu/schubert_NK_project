"""One held canonical entry retirement/reload in all terminal scopes, no Root/service starts/stops."""
import ast
import inspect
import os
import sys
import pg1826_state_configuration_owned_stop_dispatch as runner
from pg2038_fresh_current_stage_owned_stop_dispatch import STAGE as old_stage
from pg2032_fresh_normal_warning_owned_stop_dispatch import PARENT_PREQUAL as old_prequal
from pg2040_fresh_normal_warning_terminal_post import payload as stopped_payload
from pg2050_fresh_completed_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2052-fixed-stage-v1'
STAGE=old_stage.replace('pg2038-fixed-stage-v1','pg2052-fixed-stage-v1').replace('pg2038-pg2030-fresh-normal-warning-owned-stop-tools-v1.tar',TOOLS+'.tar').replace('pg2030-fresh-normal-warning-owned-stop-tools-v1',TOOLS)
PARENT_PREQUAL=old_prequal.replace('pg2030','pg2050')
POST_SLOT='pg2040-fresh-normal-warning-terminal-post-v1'


def context():return SHA,None,None,None


def post_payload():
    post=runner.json.loads((W/'pg2040-fresh-normal-warning-terminal-post-v1/manifest.safe.json').read_bytes())
    build=runner.json.loads((W/'pg2031-frozen-v1.safe.json').read_bytes())
    receipt=(W/'pg2030-fresh-normal-warning-owned-stop-tools-v1/pg2030_parent_receipt.py').read_text()
    seals={name:value['sha256']for name,value in post['proofHashes'].items()}
    return 'HASHES='+repr(build['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+stopped_payload(seals)


def run_action(action):
    raw=inspect.getsource(runner.run_action)
    raw=raw.replace("('stage','stop')","('stage','retire')").replace("post['guest']['privateBeforeSha256']!=before","post['proofHashes']['after.private.json']['sha256']!=before")
    raw=raw.replace('pg1828-state-configuration-fresh-whole-v1','pg2054-stopped-runtime-pre-retire-fresh-v1')
    raw=raw.replace('Pg1821NativeStop stop','Pg2050NativeStop retire')
    tree=ast.parse(raw)
    class Profile(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is not str:return node
            value=node.value.replace('pg1825','pg2051').replace('pg1826','pg2052').replace('pg1827','pg2053').replace('Pg1821','Pg2050').replace('PG1638','PG1846')
            return ast.copy_location(ast.Constant(value),node)
    tree=Profile().visit(tree);ast.fix_missing_locations(tree)
    ns={**runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'W':W,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(tree,'<exact current runtime stage/retire transport>','exec'),ns);return ns['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['retire']):raise ValueError('fixed new stage/retire only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
