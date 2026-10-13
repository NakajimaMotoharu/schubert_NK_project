"""Whole finite ordinary publication compiler with existing normal Unit unchanged."""
import inspect
import pg1879_warning_publication_compile as prior
from pg2170_normal_publication_sources import sources,TOOLS,BOM,BEFORE
from pg2132_current_normal_unused_sources import CURRENT,production

TARGET=prior.W/TOOLS


def compiler():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1876-warning-candidate-ro-post-v1','pg2168-normal-candidate-ro-post-v1'),('pg1846-candidate-build','pg2126-candidate-build'),('pg1861-frozen','pg2145-frozen'),('pg1860-warning-unused-tools-v1','pg2144-current-normal-unused-tools-v1'),('Pg1860','Pg2144'),('pg1877','pg2170'),('Pg1877','Pg2170'),('pg1879-','pg2171-'),('pg1638-release-v1','pg1846-release-v1')]:raw=raw.replace(old,new)
    needle="post=json.loads((W/'pg2168-normal-candidate-ro-post-v1/manifest.safe.json').read_bytes())"
    raw=raw.replace(needle,needle+"\n    if post['actualExit']!=0:raise ValueError('actual whole readonly candidate post required')\n    post={**post['guest'],'productionSource':OLD,'privateBeforeSha256':BEFORE}")
    compile(raw,'<whole normal publication compiler>','exec');return raw


def main():
    ns={**prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BOM':BOM,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(prior.write),'<normal publication canonical writer>','exec'),ns)
    exec(compile(compiler(),'<actual normal publication freeze>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
