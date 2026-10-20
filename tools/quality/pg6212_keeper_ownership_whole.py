"""Necessary grouped current4027 whole after SS318 keeper and same-path PG; not a replay."""
import inspect
import pg6188_native_ownership_whole as base
from pg6208_keeper_faults_qualification import original_source

LABEL='PG6212'
SLOT='pg6212-keeper-ownership-six-v1'


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source}
    for name in ('declared_inventory','server_source','driver_source','prerequisites','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (
            ('4023','4027'),('pg6188','pg6212'),
            ('PG6184-unstarted-management-qualification-v1','PG6208-keeper-faults-qualification-v1'),
            ('pg6184-unstarted-management-qualification-v1','pg6208-keeper-faults-qualification-v1'),
            ('PG6186-native-ownership-order-v1','PG6210-keeper-order-v1'),
            ('(59,20,1667)','(63,20,1667)'),('original59','original63'),('Original59','Original63'),
            ('SS313..317 ownership regression','SS318 keeper/diagnostic/fallback and same-path quality regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.','SSC318 secondary faults retain UNKNOWN; SSC317 unstarted management remains UNKNOWN.')):
            raw=raw.replace(before,after)
        exec(compile(raw,'<current4027 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()
def server_source(head,digest):return definitions()['server_source'](head,digest)
def driver_source(fresh):return definitions()['driver_source'](fresh)
def prerequisites(source):return definitions()['prerequisites'](source)
def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
