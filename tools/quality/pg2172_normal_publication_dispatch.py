"""Finite ordinary normal publication; no duplicate Unit exchange/reload."""
import inspect
import pg1880_warning_publication_dispatch as prior
from pg2170_normal_publication_sources import sources,TOOLS,CLASS,BOM,BEFORE
from pg2171_normal_publication_compile import TARGET
from pg2132_current_normal_unused_sources import CURRENT,production

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2172-fixed-stage-v1'
STAGE=prior.STAGE.replace('pg1880-fixed-stage-v1','pg2172-fixed-stage-v1').replace('pg1877-warning-publication-tools-v1',TOOLS).replace('0.1.0-PG1638','0.1.0-PG1846')


def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1879-frozen','pg2171-frozen'),('pg1876-warning-candidate-ro-post-v1','pg2168-normal-candidate-ro-post-v1'),('pg1846-candidate-build','pg2126-candidate-build'),('pg1860-warning-unused-tools-v1','pg2144-current-normal-unused-tools-v1'),('pg1877','pg2170'),('Pg1877','Pg2170'),('PG1877','PG2170'),('pg1880-','pg2172-'),('0.1.0-PG1638','0.1.0-PG1846')]:raw=raw.replace(old,new)
    old="'unitExchangeAndReload':changed"
    if raw.count(old)!=1:raise ValueError('one explicit old unconditional Unit report required')
    raw=raw.replace(old,"'unitExchangeAndReload':False")
    compile(raw,'<actual normal finite publication entry>','exec');return raw


def main():
    post=prior.json.loads((prior.W/'pg2168-normal-candidate-ro-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['candidateHostReadonlyVerified']is not True:
        raise ValueError('independent hostRO post required')
    ns={**prior.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BOM':BOM,'BEFORE':BEFORE}
    exec(compile(source(),'<actual isolated normal publication entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
