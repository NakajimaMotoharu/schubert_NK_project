"""Independent stopped post of corrected signed-current graph; no replay."""
import inspect
import pg2252_newboot_owned_post as prior
from pg2274_current_signed_owned_sources import TOOLS,SOURCE,BOM

SLOT='pg2281-current-signed-owned-post-v2'


def payload(seals):
    raw=prior.payload(seals).replace(prior.TOOLS,TOOLS)
    for old,new in [('pg2246','pg2274'),('Pg2246','Pg2274'),('PG2246','PG2274'),(prior.TOOLS,TOOLS),(prior.SLOT,SLOT)]:raw=raw.replace(old,new)
    raw=raw.replace('PG2252-newboot-owned-stop-post-v1','PG2281-current-signed-owned-post-v2')
    compile(raw,'<corrected current stopped post>','exec');return raw


def entry():
    raw=inspect.getsource(prior.prior.prior.previous.main)
    for old,new in [('pg2038-stop-v1','pg2276-stop-v1'),('pg2031-frozen-v1','pg2275-frozen-v1'),('pg2030_parent_receipt.py','pg2274_parent_receipt.py'),('pg2030-native-stop-v1','pg2274-native-stop-v1')]:raw=raw.replace(old,new)
    ns={**prior.prior.prior.previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'SOURCE':SOURCE,'BOM':BOM,'payload':payload}
    exec(compile(raw,'<corrected stopped post entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
