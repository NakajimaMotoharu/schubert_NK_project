"""Immutable new RO-only tools and one owned candidate mount/verifier; no re-place."""
import inspect
import sys
import pg1250_fresh_owned_stop_dispatch as previous
from pg1300_current_candidate_ro_sources import sources
from pg1293_completed_unused_stage_sources import BASELINE_SHA

GUEST='/var/lib/pgpt-s1-preservation/pg1300-native-tools-v1'
STAGE=previous.STAGE.replace('pg1250-fixed-stage-v1','pg1302-fixed-stage-v1').replace('pg1247-native-tools-v1','pg1300-native-tools-v1').replace('PG1250','PG1302')
compile(STAGE,'<current fixed readonly tools>', 'exec')


def source():
    code=inspect.getsource(previous.main)
    for old,new in [('pg1248-frozen-v1.safe.json','pg1301-frozen-v1.safe.json'),
      ('pg1249-fresh-stop-preflight-v1.safe.json','pg1297-unused-candidate-independent-v1.safe.json'),
      ("pre['privateBeforeSha256']","pre['stageAfterSha256']"),
      ('pg1247-native-tools-v1','pg1300-native-tools-v1'),('pg1250','pg1302'),
      ("(['stage'],['stop'])","(['stage'],['prepare-ro'])"),
      ('Pg1247StopLabelTest','Pg1300StopLabelTest'),('Pg1247NativeArgumentTest','Pg1300NativeArgumentTest'),
      ('Pg1247NativeStop stop','Pg1300CandidateRo prepare-ro')]:
        if old not in code:raise ValueError('fixed current RO dispatcher boundary refused')
        code=code.replace(old,new)
    code=code.replace("'Pg1300StopLabelTest','Pg1300NativeArgumentTest'","'Pg1300OriginalTupleTest','Pg1300StopLabelTest','Pg1300NativeArgumentTest'")
    compile(code,'<actual current RO-only complete dispatcher>', 'exec');return code


def main():
    if sys.argv[1:]not in (['stage'],['prepare-ro']):raise ValueError('closed stage or prepare-ro action required')
    env=dict(previous.__dict__,GUEST=GUEST,STAGE=STAGE,sources=sources,BEFORE=BASELINE_SHA)
    exec(compile(source(),'<actual current candidate RO dispatcher>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
