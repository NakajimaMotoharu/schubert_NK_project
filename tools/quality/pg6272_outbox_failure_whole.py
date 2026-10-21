"""One necessary source4040 whole after SS320 two Main and six independent fault cases."""
import inspect
import pg6188_native_ownership_whole as base
from pg6268_outbox_failure_qualification import original_source

LABEL='PG6272'
SLOT='pg6272-outbox-failure-six-v1'


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source}
    for name in ('declared_inventory','server_source','driver_source','prerequisites','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (
            ('4023','4040'),('605','607'),('pg6188','pg6272'),
            ('PG6184-unstarted-management-qualification-v1','PG6268-outbox-failure-qualification-v1'),
            ('pg6184-unstarted-management-qualification-v1','pg6268-outbox-failure-qualification-v1'),
            ('PG6186-native-ownership-order-v1','PG6270-outbox-failure-order-v2'),
            ('(59,20,1667)','(51,11,1667)'),('original59','original51'),('Original59','Original51'),
            ('SS313..317 ownership regression','SS320 ordinary Outbox fatal cleanup and JDBC unreturned setup ownership regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.','SS320 Error stays fatal and setup/rollback close is once; prior native/management UNKNOWN contracts unchanged.')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<current4040 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)
def driver_source(fresh):return definitions()['driver_source'](fresh)
def prerequisites(source):return definitions()['prerequisites'](source)
def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
