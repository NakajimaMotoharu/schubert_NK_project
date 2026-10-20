"""Necessary grouped SS319/Web/Core regression, current4034/606, not a confirmation replay."""
import inspect
import pg6188_native_ownership_whole as base
from pg6248_normal_phase_qualification import original_source

LABEL='PG6244'
SLOT='pg6244-confirmed-rollback-six-v1'


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source}
    for name in ('declared_inventory','server_source','driver_source','prerequisites','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (
            ('4023','4034'),('605','606'),('pg6188','pg6244'),
            ('PG6184-unstarted-management-qualification-v1','PG6248-normal-phase-qualification-v1'),
            ('pg6184-unstarted-management-qualification-v1','pg6248-normal-phase-qualification-v1'),
            ('PG6186-native-ownership-order-v1','PG6242-confirmed-rollback-order-v1'),
            ('(59,20,1667)','(113,28,1667)'),('original59','original113'),('Original59','Original113'),
            ('SS313..317 ownership regression','SS319 per-delivery rollback plus grouped Web/Core normal and failure contracts'),
            ('SSC317 unstarted management stop remains UNKNOWN.','SS319 attempted/confirmed phases remain distinct; SSC317 unstarted management remains UNKNOWN.')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<current4034 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)
def driver_source(fresh):return definitions()['driver_source'](fresh)
def prerequisites(source):return definitions()['prerequisites'](source)
def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
