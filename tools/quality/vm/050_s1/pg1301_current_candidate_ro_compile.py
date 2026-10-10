"""Current-D5 ABI frozen hostRO candidate fixture; no candidate rebuild/re-place."""
import inspect
import json
import os
import subprocess
import pg1248_fresh_owned_stop_compile as previous
from pg1300_current_candidate_ro_sources import sources
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST,BASELINE_SHA

TARGET=previous.W/'pg1300-native-tools-v1'


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean operator required')
    placed=json.loads((previous.W/'pg1297-unused-candidate-independent-v1.safe.json').read_bytes())
    if placed['actualExit']!=0 or placed['candidateSource']!=SOURCE or placed['candidateManifestSha256']!=DIGEST or not placed['candidateNotCurrent']:
        raise ValueError('actual unused signed candidate and full current post required')
    code=inspect.getsource(previous.main)
    for old,new in [('Pg1247NativeStop','Pg1300CandidateRo'),('Pg1247','Pg1300'),('pg1248','pg1301'),
      ('pg1217-frozen-v1.safe.json','pg1294-frozen-v1.safe.json'),("name.startswith('Pg1216')","name.startswith('Pg1293')"),
      ('pg1216-native-tools-v1','pg1293-native-tools-v1')]:
        if old not in code:raise ValueError('fixed immutable current compiler boundary required')
        code=code.replace(old,new)
    code=code.replace("'Pg1300StopLabelTest.java']]","'Pg1300StopLabelTest.java','Pg1300OriginalTupleTest.java']]")
    code=code.replace("('label','Pg1300StopLabelTest')","('label','Pg1300StopLabelTest'),('original','Pg1300OriginalTupleTest')")
    code=code.replace("'formalAccepted':False}","'formalAccepted':False,'candidateSource':CANDIDATE_SOURCE,'candidateManifestSha256':CANDIDATE_DIGEST,'candidateReadOnlyOnly':True}")
    env=dict(previous.__dict__,TARGET=TARGET,sources=sources,BEFORE=BASELINE_SHA,CANDIDATE_SOURCE=SOURCE,CANDIDATE_DIGEST=DIGEST)
    exec(compile(code,'<current candidate host RO compile>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
