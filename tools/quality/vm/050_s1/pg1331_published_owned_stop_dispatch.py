"""Reserved once reverse owned stop; current source and immutable original18."""
import inspect
import sys
import pg1250_fresh_owned_stop_dispatch as previous
from pg1328_published_owned_stop_sources import sources,SOURCE,BEFORE

GUEST='/var/lib/pgpt-s1-preservation/pg1328-native-tools-v1'
STAGE=previous.STAGE.replace('pg1250-fixed-stage-v1','pg1331-fixed-stage-v1').replace('pg1247-native-tools-v1','pg1328-native-tools-v1').replace('PG1250','PG1331')
compile(STAGE,'<immutable new current stop stage>','exec')


def source():
    code=inspect.getsource(previous.main)
    for old,new in [('Pg1247','Pg1328'),('pg1247','pg1328'),('pg1250','pg1331'),('pg1248','pg1329'),('pg1249-fresh-stop-preflight-v1','pg1330-published-stop-preflight-v1'),('0.1.0-PG1068','0.1.0-PG1292')]:
        if old not in code:raise ValueError('fixed current stop dispatch boundary required')
        code=code.replace(old,new)
    code=code.replace("'Pg1328StopLabelTest','Pg1328NativeArgumentTest'","'Pg1328OriginalTupleTest','Pg1328StopLabelTest','Pg1328NativeArgumentTest'")
    code=code.replace("['.private.log','.exit','.safe.json']","['.private.log','.exit','.safe.json','.requested']")
    marker="    if action=='stage':"
    if code.count(marker)!=1:raise ValueError('one request reservation required')
    reservation="""    with Path(str(base)+'.requested').open('x')as f:
        json.dump({'action':action,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False},f);f.flush();os.fsync(f.fileno())
    fd=os.open(base.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
"""
    code=code.replace(marker,reservation+marker)
    compile(code,'<actual one reserved current reverse stop>','exec');return code


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('closed stage or stop required')
    env=dict(previous.__dict__,GUEST=GUEST,STAGE=STAGE,sources=sources,SOURCE=SOURCE,BEFORE=BEFORE)
    exec(compile(source(),'<actual current stop dispatcher>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
