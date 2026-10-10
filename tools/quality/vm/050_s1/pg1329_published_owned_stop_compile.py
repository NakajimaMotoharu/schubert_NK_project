"""Fresh current-release ABI/Werror/original18 freeze, no operations."""
import inspect
import pg1248_fresh_owned_stop_compile as previous
from pg1254_fresh_owned_stop_compile_v2 import source as compiler
from pg1328_published_owned_stop_sources import sources,SOURCE,BEFORE


def main():
    code=compiler().replace('Pg1253','Pg1328').replace('pg1254','pg1329').replace('pg1068-release-v1','pg1292-release-v1')
    env=dict(previous.__dict__,sources=sources,SOURCE=SOURCE,BEFORE=BEFORE,TARGET=previous.W/'pg1328-native-tools-v1')
    exec(compile(code,'<new current-release qualified stop compiler>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
