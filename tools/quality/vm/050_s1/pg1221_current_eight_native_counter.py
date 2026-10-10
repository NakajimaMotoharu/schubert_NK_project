"""Only qualified current D5 eight streams + frozen D5 host; Inspector remains missing."""
import ast
import json
import os
from pathlib import Path
import subprocess
from pg972_current_native_v2 import code as previous
from pg644_native_counter import CATALOG

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='d5b00104280028d9ea81b44c1d1c805f3c2861ed'
BEFORE='de28ab9000a6b8c6dbe89ac4589a28b0b36de50655883a768e6fb8d0469d749a'
AFTER='21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36'


def catalog():
    s=CATALOG.replace('pg642-native-stop-v1','pg1216-native-stop-v1').replace('c9da5fd175734ba356629295d5ef96818e14dd3d4c997381dcf246a291cd1d65',BEFORE)
    compile(s,'<actual current catalog>','exec');return s


def code(hashes):
    s=previous(hashes,BEFORE,AFTER,52530445203)
    for a,b in [('40ef6e894573d2ffab1d1732124960f9c98d5f97',SOURCE),('pg963-native-stop-v1','pg1216-native-stop-v1'),('pg963-stop-v1.exit','pg1218-stop-v1.exit'),('pg968-terminal-final-v1','pg1220-full32-terminal-post-v1'),
                ('213904','81093'),('0bb4d6f3b9e74cdc91c553748a4cd018','a14cc600a4fd4f2e9d8c4731ad9d754b'),('201380374989','51172132518'),('cc9ed8747f4f450ea1888de1e42c8441','cbca87383b244090b77cbf029677cdd6'),
                ('pg926-body-six-host-v1','pg1018-stream-six-host-v2'),('4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf','c94cf95cddaef9fae4d3db02d3a732ee17a5ffdcc700714b14b4694fb077aab1'),
                ("tests']==3560","tests']==3563"),('pg972-current-eight-native-v2','pg1221-current-eight-native-v1'),('PG972-current-eight-native-v2','PG1221-current-eight-native-v1')]:
        if a not in s:raise ValueError('fixed current-only native source insertion refused')
        s=s.replace(a,b)
    s=s.replace("'currentNativeStreams':8,", "'currentNativeStreams':8,'requiredPlannedStreams':9,'missingCurrentStreams':['ordinary-inspector196 actual current generation terminal'],'wholeNativeAccepted':False,")
    s=s.replace("'formalAccepted':False,'rawExported':False", "'formalAccepted':False,'capacityBefore':CAPACITY,'rawExported':False")
    compile(s,'<current D5 actual native counter>','exec');return s


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean source required')
    post=json.loads((W/'pg1220-full32-terminal-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']:raise ValueError('actual same-source independent terminal post required')
    st=os.statvfs(W);available=st.f_bavail*st.f_frsize
    # Eight16MiB bounded inputs, equal temporary allowance,256MiB analysis/
    # report allowance and512MiB normal close cushion. No VM clone/new heap.
    needed=8*16777216*2+268435456+536870912
    if available<needed:raise ValueError('insufficient bounded native capture and normal close capacity')
    capacity={'availableBytes':available,'boundedNativeInputsBytes':134217728,'temporaryBytes':134217728,'analysisAllowanceBytes':268435456,'normalCloseCushionBytes':536870912,'requiredBytes':needed,'capacityFits':True,'deletions0':True,'extraVmCopies0':True}
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    hashes=json.loads(subprocess.check_output(ssh,input=catalog().encode(),timeout=30))
    if len(hashes)!=8:raise ValueError('complete current eight subcampaign required; missing Inspector not synthesized')
    env={'__name__':'qualified_current_d5_native','__file__':str(R/'pg1221_current_eight_native_counter.py'),'CAPACITY':capacity}
    exec(compile(code(hashes),'<same current eight native and exact D5 host only>','exec'),env);env['main']()


if __name__=='__main__':main()
