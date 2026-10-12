"""One frozen exact profile, shared direct runner; no nested main cloning.

All constant strings in the actual run_action are individually bound before
execution. Tool namespaces, not UUID numeric substrings, are substituted.
"""
import ast
import inspect
import os
import sys
import pg1826_state_configuration_owned_stop_dispatch as runner
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
from pg1833_readonly_parent_state_sources import sources,context,SOURCE,TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1835-fixed-stage-v1'
STAGE=runner.STAGE.replace('pg1826','pg1835').replace('PG1826','PG1835').replace('pg1821','pg1833').replace('Pg1821','Pg1833')
PARENT_PREQUAL=runner.PARENT_PREQUAL.replace('pg1821','pg1833').replace("helper.show('schubert-nk-morning-controller.service')",'helper.parent_state()')


def run_action(action):
    raw=inspect.getsource(runner.run_action)
    tree=ast.parse(raw)
    class Profile(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is not str:return node
            v=node.value.replace('pg1825','pg1834').replace('pg1826','pg1835').replace('pg1827','pg1836').replace('pg1828','pg1837').replace('Pg1821','Pg1833')
            return ast.copy_location(ast.Constant(v),node)
    tree=Profile().visit(tree);ast.fix_missing_locations(tree)
    namespace={**runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'W':W}
    exec(compile(tree,'<same direct runner fixed readonly-parent profile>','exec'),namespace)
    return namespace['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('fixed stage/stop only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
