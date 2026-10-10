"""New-only module namespace-safe handoff; old1142 rejected before signal."""
import ast
import inspect
from pg1142_fixed_failed_owner_handoff import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    text=previous().replace('fixed-failed-owner-handoff-v1','fixed-failed-owner-handoff-v2')
    old='before=whole();require(before==PROVEN==whole());SAVE.mkdir(mode=0o700)'
    new='owned_snapshot=whole();require(owned_snapshot==PROVEN==whole());SAVE.mkdir(mode=0o700)'
    if text.count(old)!=1:raise ValueError('fixed current ownership namespace insertion refused')
    text=text.replace(old,new)
    old='json.dump(before,f,sort_keys=True)'
    if text.count(old)!=1:raise ValueError('fixed private ownership snapshot insertion refused')
    text=text.replace(old,'json.dump(owned_snapshot,f,sort_keys=True)')
    tree=ast.parse(text)
    stores=[]
    def module(node):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Lambda)):return
        if isinstance(node,ast.Name)and isinstance(node.ctx,ast.Store)and node.id=='before':stores.append(node)
        for child in ast.iter_child_nodes(node):module(child)
    module(tree)
    if len(stores)!=1:raise ValueError('immutable original before store contract refused')
    return text


def main():
    text=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1143-fixed-failed-owner-handoff-v2').replace('PG1120-current-failed-capture-v1','PG1143-fixed-failed-owner-handoff-v2')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(text,'<new-only namespace-safe fixed handoff>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
