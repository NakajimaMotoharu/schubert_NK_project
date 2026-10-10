"""One reserved publication, immutable stage; no retries, mount, place or app start."""
import inspect
import sys
import pg1250_fresh_owned_stop_dispatch as previous
from pg1311_ordinary_publication_sources_v3 import sources
from pg1293_completed_unused_stage_sources import BASELINE_SHA

GUEST='/var/lib/pgpt-s1-preservation/pg1311-native-tools-v1'
STAGE=previous.STAGE.replace('pg1250-fixed-stage-v1','pg1314-fixed-stage-v1').replace('pg1247-native-tools-v1','pg1311-native-tools-v1').replace('PG1250','PG1314')
compile(STAGE,'<immutable corrected publication tools>', 'exec')


def source():
    code=inspect.getsource(previous.main)
    replacements=[('pg1248-frozen-v1.safe.json','pg1312-frozen-v1.safe.json'),
      ('pg1249-fresh-stop-preflight-v1.safe.json','pg1313-current-readonly-v1.safe.json'),
      ('pg1247-native-tools-v1','pg1311-native-tools-v1'),('pg1250','pg1314'),
      ("(['stage'],['stop'])","(['stage'],['activate'])"),
      ('Pg1247StopLabelTest','Pg1311StopLabelTest'),('Pg1247NativeArgumentTest','Pg1311NativeArgumentTest'),
      ('Pg1247NativeStop stop','Pg1311OrdinaryPublication activate')]
    for old,new in replacements:
        if old not in code:raise ValueError('fixed publication dispatcher boundary required')
        code=code.replace(old,new)
    code=code.replace("'Pg1311StopLabelTest','Pg1311NativeArgumentTest'",
      "'Pg1311TransitionTest','Pg1311OriginalTupleTest','Pg1311StopLabelTest','Pg1311NativeArgumentTest'")
    code=code.replace("['.private.log','.exit','.safe.json']","['.private.log','.exit','.safe.json','.requested']")
    marker="    if action=='stage':"
    if code.count(marker)!=1:raise ValueError('one reservation boundary required')
    reservation="""    with Path(str(base)+'.requested').open('x')as f:
        json.dump({'action':action,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'requestedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False},f);f.flush();os.fsync(f.fileno())
    fd=os.open(base.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
"""
    code=code.replace(marker,reservation+marker)
    code=code.replace("'starts0':True,'formalAccepted':False","'starts0':True,'formalAccepted':False,'finitePublicationRequested':action=='activate','canonicalEpochWritesExpected':1 if action=='activate'else 0,'candidateSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f'")
    compile(code,'<actual reserved publication dispatcher>','exec')
    return code


def main():
    if sys.argv[1:]not in (['stage'],['activate']):raise ValueError('closed stage or activate required')
    env=dict(previous.__dict__,GUEST=GUEST,STAGE=STAGE,sources=sources,BEFORE=BASELINE_SHA)
    exec(compile(source(),'<actual finite publication dispatcher>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
