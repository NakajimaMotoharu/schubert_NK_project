"""Fresh whole readonly cold observation; new fixed pre/post slots only."""
import ast
import sys
from pg1066_cold_prepared_post_v2 import payload as prepared
from pg1051_cold_tree_preflight_v2 import dispatch


def main():
    if sys.argv[1:]not in (['before'],['after']):raise ValueError('fixed observation required')
    run='PG1072-cold-before-unused-placement-v1'if sys.argv[1]=='before'else'PG1073-cold-after-unused-placement-v1'
    script=prepared().replace('PG1066-cold-prepared-post-v2',run)
    ast.parse(script)
    dispatch(run,run.lower().replace('pg1072','pg1072').replace('pg1073','pg1073'),script)


if __name__=='__main__':main()
