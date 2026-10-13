"""Normal candidate-only host readonly action; no ordinary publication authority."""
import inspect
import pg1870_warning_candidate_ro_dispatch as prior
from pg2152_normal_candidate_ro_sources import sources,TOOLS,CLASS
from pg2153_normal_candidate_ro_compile import TARGET
from pg2132_current_normal_unused_sources import CURRENT,production,BEFORE

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2154-fixed-stage-v1'
STAGE=prior.STAGE.replace('pg1870-fixed-stage-v1','pg2154-fixed-stage-v1').replace('pg1867-warning-candidate-ro-tools-v1',TOOLS)


def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1868-frozen','pg2153-frozen'),('pg1866-warning-unused-independent-post-v1','pg2150-normal-unused-independent-post-v1'),('pg1860-warning-unused-tools-v1','pg2144-current-normal-unused-tools-v1'),('pg1867','pg2152'),('Pg1867','Pg2152'),('pg1870-','pg2154-'),('0.1.0-PG1638','0.1.0-PG1846')]:raw=raw.replace(old,new)
    needle="post=json.loads((W/'pg2150-normal-unused-independent-post-v1/manifest.safe.json').read_bytes())"
    if raw.count(needle)!=1:raise ValueError('one qualified independent post boundary required')
    raw=raw.replace(needle,needle+"\n    if post['actualExit']!=0:raise ValueError('independent actual unused post required')\n    post={**post['guest'],'privateBeforeSha256':BEFORE}")
    compile(raw,'<current normal candidate RO dispatcher>','exec');return raw


def main():
    ns={**prior.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(source(),'<actual isolated normal RO entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
