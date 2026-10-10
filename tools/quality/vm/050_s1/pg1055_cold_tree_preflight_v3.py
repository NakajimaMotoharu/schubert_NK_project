"""New-only IPv4-mapped aware whole cold tree preflight; no live signal authority."""
from pg1051_cold_tree_preflight_v2 import payload as previous,dispatch


def payload():
    raw=previous()
    if raw.count('PG1051-cold-tree-preflight-v2')!=2 or raw.count("/tree-preflight-v2'")!=1:
        raise ValueError('fixed v3 producer labels refused')
    return raw.replace('PG1051-cold-tree-preflight-v2','PG1055-cold-tree-preflight-v3').replace("/tree-preflight-v2'","/tree-preflight-v3'")


if __name__=='__main__':
    dispatch('PG1055-cold-tree-preflight-v3','pg1055-cold-tree-preflight-v3',payload())
