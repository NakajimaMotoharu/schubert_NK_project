"""Complete18 failed-data RO ABI against current7bb, with v5 shared provenance."""
import inspect
import types
import pg3996_literal_invariant_ro_compile as previous
import pg3782_hygiene_ro_compile as base
import pg4522_failed_current_ro_sources as role
import pg4498_set_typed_unused_sources as unused

W=role.W;TARGET=W/role.TOOLS;PRIOR=W/unused.TOOLS


def generated():
    ns={**vars(base),'role':role,'PRIOR':PRIOR}
    raw=inspect.getsource(base.generated).replace('pg3780','pg4522')
    exec(compile(raw,'<actual failed-data RO bundle>','exec'),ns);return ns['generated']()


def compiler():
    raw=previous.compiler().replace('pg3996','pg4524').replace('pg3984','pg4500').replace('Pg3982','Pg4444').replace('pg3748-release-v1','pg3976-release-v1')
    old="'genuineParentBeforeSha256':role.BEFORE"
    if raw.count(old)!=1:raise ValueError('one failed data classification boundary')
    return raw.replace(old,"'failedCurrentDataBeforeSha256':role.BEFORE,'oldParentNormal':False,'historicalGenericToolSource':'7fffab57a567914956b66452e5e54388642efdec'",1)


def main():
    ns={**vars(base),'role':role,'TARGET':TARGET,'PRIOR':PRIOR,'generated':generated}
    ns['write']=types.FunctionType(base.write.__code__,ns)
    exec(compile(compiler(),'<complete failed-data RO current ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
