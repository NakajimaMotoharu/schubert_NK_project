"""New-only current literal/helper compile; no runtime operation/DB/locks acquired here."""
import ast
import inspect
import pg4088_failed_done_owned_compile as previous
import pg4312_current_failed_owned_sources as role
import pg4058_original_read_profile as transport


def payload():
    ns={**vars(previous),'role':role}
    exec(compile(inspect.getsource(previous.payload),'<current source/helper full compile factory>','exec'),ns)
    raw=role.bind_instance(ns['payload']());lines=raw.splitlines(keepends=True)
    # The compile-only prelude inherits read-mode-only imports. Remove only
    # those top-level import statements; never rewrite embedded Java/helpers.
    for node in ast.parse(raw).body:
        if isinstance(node,ast.Import)and any(a.name in {'datetime','selectors'}for a in node.names):
            if node.lineno!=node.end_lineno:raise ValueError('single-line compile import required')
            names=[a for a in node.names if a.name not in {'datetime','selectors'}]
            lines[node.lineno-1]=(ast.unparse(ast.Import(names=names))+'\n')if names else'\n'
    return ''.join(lines)


def main():
    ns={**vars(transport),'SLOT':role.TOOLS,'payload':lambda action:payload()}
    ns['sys']=type('CompileOnlyArguments',(),{'argv':['current-instance-compile','compile']})
    exec(compile(inspect.getsource(transport.main),'<current-only stage transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
