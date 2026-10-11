import inspect
import pg1329_published_owned_stop_compile as previous
from pg1334_published_owned_stop_sources_v2 import sources,SOURCE,BEFORE

def main():
    code=previous.compiler().replace('Pg1253','Pg1334').replace('pg1254','pg1335').replace('pg1068-release-v1','pg1292-release-v1')
    env=dict(previous.previous.__dict__,sources=sources,SOURCE=SOURCE,BEFORE=BEFORE,TARGET=previous.previous.W/'pg1334-native-tools-v1')
    exec(compile(code,'<new-only current stop compiler>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
