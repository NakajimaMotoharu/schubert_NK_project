"""New-only exact corrected Test source/all3684 independent qualification."""
import inspect
import pg2920_db_failure_group_full_qualified as prior
from pg2930_format_fixed_db_full_six import SOURCE,validate


def server():return prior.server().replace('PG2918','PG2930')


def main():
    raw=inspect.getsource(prior.main).replace('pg2920-db-failure-group-full-qualified-v1','pg2932-format-fixed-full-qualified-v1').replace('pg2918-server-six-v1','pg2930-server-six-v1').replace('PG2918','PG2930')
    ns={**prior.__dict__,'SOURCE':SOURCE,'validate':validate,'server':server}
    exec(compile(raw,'<fresh corrected Test input whole qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
