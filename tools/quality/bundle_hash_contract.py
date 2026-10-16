"""Explicit unbound source versus exactly-once materialized bundle hash; never rewrite other data."""
import ast
import re


def assignments(raw):
    tree=ast.parse(raw);bound=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.Assign,ast.AnnAssign,ast.NamedExpr)):
            targets=node.targets if isinstance(node,ast.Assign)else[node.target]
            if any(isinstance(t,ast.Name)and t.id=='BUNDLE_HASH'for t in targets):
                if node not in tree.body or not isinstance(node,ast.Assign)or len(node.targets)!=1:raise ValueError('one explicit top-level bundle binding only')
                bound.append(node)
    return tree,bound


def unbind(raw):
    tree,nodes=assignments(raw)
    if len(nodes)!=1 or not isinstance(nodes[0].value,ast.Constant)or not isinstance(nodes[0].value.value,str)or not re.fullmatch('[a-f0-9]{64}',nodes[0].value.value):raise ValueError('one actual old frozen bundle binding required')
    node=nodes[0];lines=raw.splitlines(keepends=True);result=''.join(lines[:node.lineno-1]+lines[node.end_lineno:]);after=ast.parse(result);expected=ast.Module(body=[n for n in tree.body if n is not node],type_ignores=tree.type_ignores)
    if ast.dump(after,include_attributes=False)!=ast.dump(expected,include_attributes=False):raise ValueError('only explicit bundle prelude may change')
    if assignments(result)[1]:raise ValueError('unbound source still bound')
    return result


def require_bound(raw,expected):
    if type(expected)is not str or not re.fullmatch('[a-f0-9]{64}',expected):raise ValueError('actual bundle digest required')
    _,nodes=assignments(raw)
    if len(nodes)!=1 or not isinstance(nodes[0].value,ast.Constant)or nodes[0].value.value!=expected:raise ValueError('one actual bundle definition without stale override required')
    return True
