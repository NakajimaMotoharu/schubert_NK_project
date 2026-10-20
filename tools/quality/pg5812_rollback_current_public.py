"""Independent final54 XML reader, static Main reauthentication not old PT reuse."""
import inspect
import pg5802_rollback_public as previous
from pg5810_rollback_static_reauth import SOURCE


def reader_source():
    raw=inspect.getsource(previous.main)
    for old,new,count in(('pg5800-rollback-selected54-v4','pg5800-rollback-selected54-v5',1),('pg5804-rollback-static-v1','pg5810-rollback-static-reauth-v1',1),('PG5804-rollback-static-v1','PG5810-rollback-static-reauth-v1',1),('PG5802-rollback54-v1','PG5812-current-rollback54-v1',1)):
        if raw.count(old)!=count:raise ValueError('exact current XML/static reader binding')
        raw=raw.replace(old,new)
    compile(raw,'<original current54 artifacts only>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE}
    exec(compile(reader_source(),'<original current54 artifacts only>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
