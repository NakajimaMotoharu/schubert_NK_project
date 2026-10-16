"""All eighteen normal RO roles on actual installed ABI; host only."""
import inspect
import types
import pg3996_literal_invariant_ro_compile as old
import pg4714_ssc299_ro_sources as role
import pg4706_ssc299_unused_sources as unused

W=role.W
TARGET=W/role.TOOLS
PRIOR=W/unused.TOOLS
sha=old.sha


def generated():
    ns={**vars(old),'role':role,'PRIOR':PRIOR}
    raw=inspect.getsource(old.generated).replace('pg3994','pg4714')
    exec(compile(raw,'<new RO single exact bundle>','exec'),ns)
    return ns['generated']()


def compiler():
    raw=old.compiler()
    for before,after in [('pg3996','pg4716'),('pg3984','pg4708'),('Pg3982','Pg4706'),
                         ('pg3748-release-v1','pg4432-release-v1')]:raw=raw.replace(before,after)
    return raw


def main():
    ns={**vars(old.previous),'__file__':__file__,'role':role,'TARGET':TARGET,'PRIOR':PRIOR,'generated':generated}
    ns['write']=types.FunctionType(old.previous.write.__code__,ns)
    exec(compile(compiler(),'<normal full18 RO current ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
