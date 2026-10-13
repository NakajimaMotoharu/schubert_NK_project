"""Direct qualified immutable stage/one owned stop, actual current full preflight, no ancestry mutation."""
import ast
import inspect
import os
import sys
import pg1826_state_configuration_owned_stop_dispatch as runner
import pg2038_fresh_current_stage_owned_stop_dispatch as staged
import pg2032_fresh_normal_warning_owned_stop_dispatch as normal
from pg2090_current_newrun_owned_stop_sources import sources,context,SOURCE,TOOLS
from pg2085_native_augmented_newrun_full_seal import payload as full_payload,SLOT as POST_SLOT
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2092-fixed-stage-v1'
ARCHIVE='pg2092-'+TOOLS+'.tar'
STAGE=staged.STAGE.replace(staged.ARCHIVE,ARCHIVE).replace('pg2038','pg2092').replace('PG2038','PG2092').replace(normal.TOOLS,TOOLS).replace('pg2030','pg2090').replace('Pg2030','Pg2090')
PARENT_PREQUAL=normal.PARENT_PREQUAL.replace('pg2030','pg2090')


def post_payload():
    live=runner.json.loads((W/'pg2074-current-newrun-live-binding-v1/manifest.safe.json').read_bytes())
    return full_payload({**live['binding'],'rootPid':live['rootPid']})


def run_source():
    raw=inspect.getsource(runner.run_action)
    old="post['guest']['privateBeforeSha256']!=before"
    if raw.count(old)!=1:raise ValueError('one actual current full envelope boundary required')
    raw=raw.replace(old,"post['privateBeforeSha256']!=before")
    raw=raw.replace("archive=P/(TOOLS+'.tar')","archive=P/ARCHIVE")
    raw=raw.replace("'managerFailureRetained':True","'normalUnit0or10':True,'currentManagerGc':True")
    class Profile(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is not str:return node
            value=node.value
            for old,new in [('pg1825','pg2091'),('pg1826','pg2092'),('pg1827','pg2093'),('pg1828-state-configuration-fresh-whole-v1','pg2094-current-newrun-pre-stop-full-v1'),('Pg1821','Pg2090'),('PG1638','PG1846')]:value=value.replace(old,new)
            return ast.copy_location(ast.Constant(value),node)
    tree=Profile().visit(ast.parse(raw));ast.fix_missing_locations(tree);return ast.unparse(tree)+'\n'


def run_action(action):
    ns={**runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'W':W,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<current newrun actual once stop transport>','exec'),ns);return ns['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('new current stage/stop only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
