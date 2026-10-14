"""Independent all3673/541/1643/static6 qualification; no substituted old source result."""
import inspect
import pg2745_backup_admission_full_qualified as previous
from pg2770_db_contract_group_full_six import validate


def server():
    raw=previous.server().replace('PG2744','PG2770').replace('3669','3673').replace(
        "'batch':(1269,172,568)","'batch':(1273,172,568)")
    if "'batch':(1273,172,568)" not in raw:raise ValueError('exact new DB batch count required')
    compile(raw,'<independent DB whole3673>','exec');return raw


def main():
    engine=previous.previous.previous
    raw=inspect.getsource(engine.main).replace('pg2651-operation-post-full-qualified-v1','pg2772-db-contract-full-qualified-v1').replace(
        'pg2650-server-six-v1','pg2770-server-six-v1').replace('PG2650','PG2770')
    ns={**engine.__dict__,'validate':validate,'server':server}
    exec(compile(raw,'<actual all DB contract qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
