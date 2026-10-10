"""Fixed fresh unused1068 input/tool placement or owned candidate action only."""
import ast
import json
import subprocess
import sys
from pathlib import Path
from pg1064_cold_preparation_native_v2 import source as previous
from pg1041_cold_policy_diagnostic import W,P


def source():
    raw=previous()
    for old,new in [('pg1063-cold-preparation-frozen-v2.safe.json','pg1070-cold-candidate-frozen-v1.safe.json'),
                    ('pg1062-cold-tools-v1','pg1069-cold-tools-v1'),
                    ('Pg1062ColdOwnedPreparation','Pg1069ColdCandidateStage'),
                    ('pg1064-','pg1071-'),('PG1064_','PG1071_'),
                    ("('stage','prepare')","('stage','place')"),
                    ("action=='prepare'and code==0","action=='place'and code==0"),
                    ("'finiteColdPreparation':True","'unusedCandidatePlacement':True"),
                    ("'fullColdPreparationAccepted'","'unusedColdCandidatePlaced'")]:
        if old not in raw:raise ValueError('fixed candidate transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


def main():
    if sys.argv[1:]not in (['stage'],['place']):raise ValueError('fixed candidate action required')
    action=sys.argv[1];base=W/('pg1071-'+action+'-v1')
    if any(Path(str(base)+s).exists()for s in ('.begin.safe.json','.private.log','.exit','.safe.json')):
        raise ValueError('reserved candidate action cannot replay')
    if action=='stage':
        frozen=json.loads((W/'pg1070-cold-candidate-frozen-v1.safe.json').read_bytes())
        if frozen['actualExit']!=0:raise ValueError('normal compile required')
        opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
        remote='/home/ubuntu/pg1071-candidate-input-v1'
        subprocess.run(['ssh',*opts,'-p','22222','ubuntu@127.0.0.1',
            'test ! -e '+remote+' && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG1068 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg1068-manifest.sig && mkdir -m700 '+remote],check=True)
        subprocess.run(['scp',*opts,'-P','22222',str(P/'pg1071-release-v1.tar'),str(P/'pg1068-manifest-v1.sig'),
            str(W/'pg1069-cold-tools-v1/bundle.safe.json'),'ubuntu@127.0.0.1:'+remote+'/'],check=True)
    exec(compile(source(),'<PG1071 fresh owned candidate transport>','exec'),{'__file__':__file__,'__name__':'__main__'})


if __name__=='__main__':main()
