"""Independent 3684/542/1643 six-module qualification for Test-only four-method group."""
import inspect
import pg2800_jdbc_null_fixed_full_qualified as prior
from pg2918_db_failure_group_full_six import SOURCE,validate


def server():
    raw=prior.server().replace('PG2798','PG2918').replace('3680','3684').replace("'batch':(1280,173,568)","'batch':(1284,173,568)")
    if "'batch':(1284,173,568)"not in raw:raise ValueError('exact four new batch methods required')
    compile(raw,'<independent whole3684 same Main>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1','pg2920-db-failure-group-full-qualified-v1').replace('pg2798-server-six-v1','pg2918-server-six-v1').replace('PG2798','PG2918')
    ns={**prior.__dict__,'validate':validate,'server':server,'SOURCE':SOURCE}
    exec(compile(raw,'<all current inputs/source XML static qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
