"""Current04bb before-only independent applicability; no Root/clock/DB mutation."""
import types
from pyflakes.api import check
import pg4748_scoped_query_preflight as previous
import pg4888_new_current_readonly as current

SLOT='pg4898-current-query-oracle-preflight-v1'


def payload():
    raw=previous.payload();digest=current.context()
    changes={"/var/lib/pgpt-s1-preservation/pg4728-ssc299-publication-independent-post-v1/after.private.json":current.AFTER,
             'f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601':digest,
             'f1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80':current.BOM}
    for a,b in changes.items():
        if raw.count(a)!=1:raise ValueError('one actual current-before oracle binding '+a)
        raw=raw.replace(a,b,1)
    if check(raw,'<actual04bb independent applicability>'):raise ValueError('all emitted static0')
    return raw


def main():
    previous.authenticate_host()
    execute=types.FunctionType(previous.transport.execute.__code__,{**vars(previous.transport),'SOURCE':current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
