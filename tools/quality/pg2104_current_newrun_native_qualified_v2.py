"""BUG1208: qualify actual transport AND server CODE under one new run namespace."""
import pg2044_fresh_normal_warning_native_qualification as engine
from pg2102_current_newrun_native_qualification import source as prior_source


def source():return prior_source().replace('pg2102','pg2104').replace('PG2102','PG2104')


def server():
    raw=engine.server().replace('PG2044','PG2104')
    compile(raw,'<actual current newrun server qualifier>','exec');return raw


def entry():
    ns={**engine.previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':engine.SOURCE,'qualify_snapshot':engine.qualify_snapshot}
    exec(compile(source(),'<matched current newrun transport/server>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
