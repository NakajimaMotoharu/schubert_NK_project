"""New-only source compiler after unimplemented enum fixture error; no old output overwrite."""
import inspect
import pg1307_ordinary_publication_compile as previous
from pg1308_ordinary_publication_sources_v2 import sources


def main():
    env=dict(previous.__dict__);env['sources']=sources;env['TARGET']=previous.previous.W/'pg1308-native-tools-v1'
    code=inspect.getsource(previous.main).replace('Pg1306','Pg1308').replace('pg1307','pg1309')
    exec(compile(code,'<new-only ordinary publication compiler v2>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
