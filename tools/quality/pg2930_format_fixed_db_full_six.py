"""Fresh same four-method group after formatting correction; all six format gates first."""
import inspect
from pyflakes.api import check
import pg2918_db_failure_group_full_six as prior

SOURCE=prior.SOURCE


def validate(snapshot):
    raw=inspect.getsource(prior.validate).replace('pg2912-jdbc-compound-close-selected-v2','pg2926-jdbc-format-selected-v1')
    ns=dict(prior.__dict__)
    exec(compile(raw,'<actual formatted Test byte authority>','exec'),ns);return ns['validate'](snapshot)


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG2918','PG2930')
    marker="    with(OUT/'maven.private.log').open"
    if raw.count(marker)!=1:raise ValueError('one before-whole format boundary required')
    gate="""    format_args=args[:args.index('clean')]+['spotless:check']
    with (OUT/'format-preflight.private.log').open('xb')as format_log:
        format_result=subprocess.run(format_args,cwd=SOURCE,env=env,stdout=format_log,stderr=subprocess.STDOUT,umask=0o027)
        format_log.flush();os.fsync(format_log.fileno())
    if format_result.returncode!=0:raise ValueError('all six exact configured format gates refused before whole PT')
"""
    raw=raw.replace(marker,gate+marker)
    if check(raw,'<whole3684 with format before any module PT>'):raise ValueError('complete full server required')
    compile(raw,'<format first exact four DB method integration>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('PG2918','PG2930').replace('pg2918','pg2930')
    ns={**prior.__dict__,'validate':validate,'server_source':server_source}
    exec(compile(raw,'<fresh format fixed whole>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
