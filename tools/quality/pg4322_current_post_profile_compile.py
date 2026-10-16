"""New current original-only profile class for independent post; never reuse old-run Java literals."""
import ast
import base64
import inspect
import pg4060_original_profile_dual_stack as previous
import pg4058_original_read_profile as transport
import pg4312_current_failed_owned_sources as role
from pg4060_original_profile_dual_stack import once

SLOT='pg4322-current-post-profile-v1'


def java():
    return role.bind_instance((transport.ROOT/'tools/quality/RootOriginalReadProfile.java').read_text())


def payload():
    raw=previous.payload('compile').replace(previous.SLOT,SLOT)
    line=next(l for l in raw.splitlines()if l.startswith('JAVA_B64='))
    raw=once(raw,line,'JAVA_B64='+repr(base64.b64encode(java().encode()).decode()))
    raw=role.bind_instance(raw);lines=raw.splitlines(keepends=True)
    for n in ast.parse(raw).body:
        if isinstance(n,ast.Import)and any(a.name in {'datetime','selectors'}for a in n.names):
            if n.lineno!=n.end_lineno:raise ValueError('compile-only imports required')
            names=[a for a in n.names if a.name not in {'datetime','selectors'}]
            lines[n.lineno-1]=(ast.unparse(ast.Import(names=names))+'\n')if names else'\n'
    return ''.join(lines)


def main():
    ns={**vars(transport),'SLOT':SLOT,'payload':lambda action:payload()}
    ns['sys']=type('CompileOnlyArguments',(),{'argv':['current-post-profile-compile','compile']})
    exec(compile(inspect.getsource(transport.main),'<current original-only compile transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
