"""Normal candidate-only hostRO actual graph/ABI freeze; guest changes0."""
import inspect
import pg1868_warning_candidate_ro_compile as prior
from pg2152_normal_candidate_ro_sources import sources,TOOLS
from pg2132_current_normal_unused_sources import CURRENT,production,BEFORE

TARGET=prior.W/TOOLS


def compiler():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1846-candidate-build','pg2126-candidate-build'),('pg1866-warning-unused-independent-post-v1','pg2150-normal-unused-independent-post-v1'),('pg1861-frozen','pg2145-frozen'),('pg1860-warning-unused-tools-v1','pg2144-current-normal-unused-tools-v1'),('Pg1860','Pg2144'),('pg1867','pg2152'),('Pg1867','Pg2152'),('pg1868-','pg2153-'),('pg1638-release-v1','pg1846-release-v1')]:raw=raw.replace(old,new)
    boundary="prior=json.loads((W/'pg2145-frozen-v1.safe.json').read_bytes())"
    if raw.count(boundary)!=1:raise ValueError('one exact actual full post boundary required')
    raw=raw.replace(boundary,boundary+"\n    if post['actualExit']!=0 or post['guest']['currentEpochApprovalUnchanged']is not True:raise ValueError('whole independent current post required')\n    post={**post['guest'],'productionSource':OLD,'privateBeforeSha256':BEFORE}")
    compile(raw,'<normal candidate actual RO compiler>','exec');return raw


def main():
    ns={**prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(prior.write),'<new-only canonical nested writer>','exec'),ns)
    exec(compile(compiler(),'<normal actual RO freeze>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
