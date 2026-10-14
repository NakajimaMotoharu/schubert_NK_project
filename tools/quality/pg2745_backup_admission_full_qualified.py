"""Independent all3669/541/1643/static6 with three immutable Backup Test methods."""
import inspect
import pg2695_expiry_fixed_full_qualified as previous
from pg2744_backup_admission_group_full_six import validate


def server():
    raw=previous.server().replace('PG2694','PG2744').replace('3666','3669').replace(
        "'batch':(1266,172,568)","'batch':(1269,172,568)")
    if "'batch':(1269,172,568)"not in raw:raise ValueError('exact new batch count required')
    compile(raw,'<independent Backup whole3669>','exec');return raw


def main():
    raw=inspect.getsource(previous.previous.main).replace('pg2651-operation-post-full-qualified-v1',
        'pg2745-backup-admission-full-qualified-v1').replace('pg2650-server-six-v1',
        'pg2744-server-six-v1').replace('PG2650','PG2744')
    ns={**previous.previous.__dict__,'validate':validate,'server':server}
    exec(compile(raw,'<all current Backup integration qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
