"""Current trusted ABI + SSC262 publication/transition/old-new FD host qualification."""
import inspect
import json
import os
import subprocess
import pg1248_fresh_owned_stop_compile as previous
from pg1306_ordinary_publication_sources import sources
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST,BASELINE_SHA

TARGET=previous.W/'pg1306-native-tools-v1'


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean operator required')
    ro=json.loads((previous.W/'pg1303-candidate-ro-independent-v1.safe.json').read_bytes())
    if ro['actualExit']!=0 or ro['candidateSource']!=SOURCE or ro['candidateManifestSha256']!=DIGEST or not ro['candidateHostReadonly']or not ro['candidateNotCurrent']:
        raise ValueError('actual unused RO candidate and full current post required')
    code=inspect.getsource(previous.main)
    for old,new in [('Pg1247NativeStop','Pg1306OrdinaryPublication'),('Pg1247','Pg1306'),('pg1248','pg1307'),
      ('pg1217-frozen-v1.safe.json','pg1301-frozen-v1.safe.json'),("name.startswith('Pg1216')","name.startswith('Pg1300')"),
      ('pg1216-native-tools-v1','pg1300-native-tools-v1')]:
        if old not in code:raise ValueError('fixed publication ABI compiler boundary required')
        code=code.replace(old,new)
    code=code.replace("'Pg1306StopLabelTest.java']]","'Pg1306StopLabelTest.java','Pg1306OriginalTupleTest.java','Pg1306TransitionTest.java']]")
    code=code.replace("('label','Pg1306StopLabelTest')","('label','Pg1306StopLabelTest'),('original','Pg1306OriginalTupleTest'),('transition','Pg1306TransitionTest')")
    code=code.replace("'formalAccepted':False}","'formalAccepted':False,'candidateSource':CANDIDATE_SOURCE,'candidateManifestSha256':CANDIDATE_DIGEST,'finiteOrdinaryPublicationUnissued':True}")
    env=dict(previous.__dict__,TARGET=TARGET,sources=sources,BEFORE=BASELINE_SHA,CANDIDATE_SOURCE=SOURCE,CANDIDATE_DIGEST=DIGEST)
    exec(compile(code,'<actual ordinary publication host compile>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
