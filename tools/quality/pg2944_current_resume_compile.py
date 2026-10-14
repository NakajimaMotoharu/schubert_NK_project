"""Current twenty-source ABI/independent golden qualification before any guest prepare."""
import inspect
import pg2305_current_completed_resume_compile as prior
from pg2942_current_completed_resume_sources import sources,TOOLS,CLASS,SOURCE,BOM,BEFORE
from pg2890_network_owned_sources import TOOLS as SHARED

TARGET=prior.W/TOOLS


def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg2275-frozen-v1.safe.json','pg2892-frozen-v1.safe.json'),('pg2281-current-signed-owned-post-v2','pg2940-current-resume-before-v1'),
        ('pg2274-current-signed-owned-stop-tools-v1',SHARED),('Pg2274','Pg2890'),('pg2126-release-v1','pg2802-release-v1'),('pg2305','pg2944'),('Pg2304','Pg2942')]:
        raw=raw.replace(old,new)
    compile(raw,'<current actual Jar/ABI complete twenty source>','exec');return raw


def main():
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TARGET':TARGET}
    exec(compile(inspect.getsource(prior.write),'<current new-only generated source writer>','exec'),ns)
    exec(compile(source(),'<current resume compilation all actual phases>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
