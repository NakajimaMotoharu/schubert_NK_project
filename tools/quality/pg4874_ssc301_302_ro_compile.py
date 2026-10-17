"""All18 RO roles use current825e signed ABI; no extraction or guest operation."""
import inspect
import types
import pg3996_literal_invariant_ro_compile as previous
import pg4872_ssc301_302_ro_sources as role
import pg4864_ssc301_302_unused_sources as unused

W=role.W;TARGET=W/role.TOOLS;PRIOR=W/unused.TOOLS;sha=previous.sha


def generated():
    ns={**vars(previous),'role':role,'PRIOR':PRIOR}
    raw=inspect.getsource(previous.generated).replace('pg3994','pg4872')
    exec(compile(raw,'<one exact current bundle RO alias>','exec'),ns);return ns['generated']()


def compiler():
    raw=previous.compiler()
    for a,b in [('pg3996','pg4874'),('pg3984','pg4866'),('Pg3982','Pg4864'),('pg3748-release-v1','pg4702-release-v1')]:raw=raw.replace(a,b)
    return raw


def main():
    ns={**vars(previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':PRIOR,'generated':generated}
    ns['write']=types.FunctionType(previous.previous.write.__code__,ns)
    exec(compile(compiler(),'<all18 RO against825e ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
