"""Current4024/605 grouped whole, original60 v2 prerequisites, no historical PASS import."""
import inspect
import pg6188_native_ownership_whole as base
from pg6193_management_primary_qualification_v2 import original_source

LABEL='PG6196'
SLOT='pg6196-management-ownership-six-v1'


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source}
    for name in ('declared_inventory','server_source','driver_source','prerequisites','main'):
        raw=inspect.getsource(getattr(base,name))
        raw=raw.replace('4023','4024').replace('pg6188','pg6196')
        raw=raw.replace('PG6184-unstarted-management-qualification-v1','PG6193-management-primary-qualification-v2')
        raw=raw.replace('pg6184-unstarted-management-qualification-v1','pg6193-management-primary-qualification-v2')
        raw=raw.replace('PG6186-native-ownership-order-v1','PG6195-management-primary-order-v2')
        raw=raw.replace('(59,20,1667)','(60,20,1667)').replace('original59','original60').replace('Original59','Original60')
        compile(raw,'<current4024 '+name+'>','exec')
        exec(compile(raw,'<current4024 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)
def driver_source(fresh):return definitions()['driver_source'](fresh)
def prerequisites(source):return definitions()['prerequisites'](source)
def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
