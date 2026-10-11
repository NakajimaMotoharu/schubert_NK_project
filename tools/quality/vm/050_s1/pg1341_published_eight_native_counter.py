"""Current769 eight fresh streams + frozen1279 host; no old Inspector import."""
import json
import os
from pathlib import Path
import subprocess
from pg1221_current_eight_native_counter import code as previous_code,catalog as previous_catalog
from pg1293_completed_unused_stage_sources import SOURCE
from pg1257_fresh_independent_terminal_post import W,P,SSH

R=Path(__file__).resolve().parent
BEFORE='00b435fa57c6924e53bff94e410d8a0caa4afab335430947767d868d1ae0762c'
AFTER='8da8ff8624ebebb9b682dc7a868ef61a56b8b809bc5e59e34cc03d3ad10ff6e4'


def catalog():
    code=previous_catalog().replace('pg1216-native-stop-v1','pg1334-native-stop-v1').replace('de28ab9000a6b8c6dbe89ac4589a28b0b36de50655883a768e6fb8d0469d749a',BEFORE)
    compile(code,'<actual current eight catalog>','exec');return code


def code(hashes):
    if type(hashes)is not dict or len(hashes)!=8 or any(type(n)is not str or type(v)is not str or len(v)!=64 or any(c not in '0123456789abcdef'for c in v)for n,v in hashes.items()):raise ValueError('actual eight current SHA required')
    text=previous_code(hashes)
    replacements=[('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE),('pg1216-native-stop-v1','pg1334-native-stop-v1'),
      ('de28ab9000a6b8c6dbe89ac4589a28b0b36de50655883a768e6fb8d0469d749a',BEFORE),('21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36',AFTER),
      ("'81093'","'120359'"),('a14cc600a4fd4f2e9d8c4731ad9d754b','400b2e34105149ff8f3a11c21da0be6a'),('51172132518','73654946447'),('52530445203','75132489604'),
      ('pg1218-stop-v1.exit','pg1336-stop-v1.exit'),('pg1220-full32-terminal-post-v1','pg1340-published-terminal-post-v4'),
      ('pg1018-stream-six-host-v2','pg1279-held-channel-six-host-v1'),('c94cf95cddaef9fae4d3db02d3a732ee17a5ffdcc700714b14b4694fb077aab1','1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b'),
      ("tests']==3563","tests']==3569"),('pg1221-current-eight-native-v1','pg1341-published-eight-native-v1'),('PG1221-current-eight-native-v1','PG1341-published-eight-native-v1')]
    for old,new in replacements:
        if old not in text:raise ValueError('fixed current native/source/run insertion required')
        text=text.replace(old,new)
    compile(text,'<actual newsource eight native/frozen six only>','exec');return text


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed native tools required')
    post=json.loads((W/'pg1340-published-terminal-post-v4.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or post['run']!='PG1340-published-terminal-post-v4' or not post['allClientAdvisoryFlock0'] or post['proofHashes']['before.private.json']['sha256']!=BEFORE or post['proofHashes']['after.private.json']['sha256']!=AFTER:
        raise ValueError('actual current uniform source/run fullpost required')
    available=os.statvfs(W).f_bavail*os.statvfs(W).f_frsize;needed=8*16777216*2+268435456+536870912
    if available<needed:raise ValueError('native/analysis and close cushion capacity required')
    capacity={'availableBytes':available,'requiredBytes':needed,'boundedNativeInputsBytes':134217728,'temporaryBytes':134217728,'analysisAllowanceBytes':268435456,'normalCloseCushionBytes':536870912,'capacityFits':True,'deletions0':True,'extraVmCopies0':True}
    hashes=json.loads(subprocess.check_output(SSH,input=catalog().encode(),timeout=30))
    env={'__name__':'qualified_published_current_native','__file__':str(R/'pg1341_published_eight_native_counter.py'),'CAPACITY':capacity}
    exec(compile(code(hashes),'<actual current eight native and source1279 host>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
