"""Current seventeen-source retirement ABI using current qualified shared classes/Jars."""
import pg3036_current_runtime_retirement_compile as template
from pg3662_current_browser_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS


def main():
    engine=template.previous.previous.previous.prior.prior.prior.old.prior.prior
    raw=engine.compiler_source()
    for old,new in [('Pg1609','Pg3662'),('pg1610','pg3664'),('pg1544-release-v1','pg3420-release-v1'),
                    ('pg1217-frozen-v1.safe.json','pg3602-frozen-v1.safe.json'),('Pg1216','Pg3600'),
                    ('pg1216-native-tools-v1','pg3600-current-browser-owned-stop-tools-v1')]:raw=raw.replace(old,new)
    ns={**engine.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':SHA,'TARGET':engine.prior.prior.W/TOOLS}
    exec(compile(raw,'<current full17 held-FD retirement ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
