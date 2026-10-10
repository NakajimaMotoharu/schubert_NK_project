"""SSC246 corrected finite maintenance layout, new full preflight only."""
from pg1055_cold_tree_preflight_v3 import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    raw=previous()
    if raw.count('PG1055-cold-tree-preflight-v3')!=2 or raw.count("/tree-preflight-v3'")!=1:
        raise ValueError('fixed v4 producer labels refused')
    return raw.replace('PG1055-cold-tree-preflight-v3','PG1059-cold-tree-preflight-v4').replace("/tree-preflight-v3'","/tree-preflight-v4'")


if __name__=='__main__':
    dispatch('PG1059-cold-tree-preflight-v4','pg1059-cold-tree-preflight-v4',payload())
