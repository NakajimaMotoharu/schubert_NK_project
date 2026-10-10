"""New immutable compiler/output; preserve initial failed and old frozen tools."""
import inspect
import pg1307_ordinary_publication_compile as previous
from pg1311_ordinary_publication_sources_v3 import sources


def main():
    env=dict(previous.__dict__);env['sources']=sources;env['TARGET']=previous.previous.W/'pg1311-native-tools-v1'
    code=inspect.getsource(previous.main).replace('Pg1306','Pg1311').replace('pg1307','pg1312')
    exec(compile(code,'<new-only corrected publication compiler>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
