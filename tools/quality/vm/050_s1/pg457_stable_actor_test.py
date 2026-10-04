"""Independent interleavings: legacy mixed observation fails; sandwich never asserts it stable."""
import copy
from pg457_stable_actor import stable_actor

manager={'MainPID':'123','InvocationID':'1'*32,'ExecMainStartTimestampMonotonic':'1000'}
ordinary={'startTicks':100,'process':{'Uid':'20 20 20 20','Gid':'21 21 21 21','Groups':'21 22','NoNewPrivs':'1',**{k:'0'*16 for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']}},'entry':'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain','_argv':b'java\0ApiProcessMain\0','_cgroup':b'0::/system.slice/schubert-nk-api.service\n'}
root=copy.deepcopy(ordinary);root['process']['Uid']='0 0 0 0';root['entry']='dev.codex.schubert.nk.batch.file.RootServiceLauncher';root['_argv']=b'java\0RootServiceLauncher\0'
expected={k:v for k,v in ordinary.items() if not k.startswith('_')}
count=0
def check(value):
    global count
    assert value;count+=1
def observe(samples,managers=None):
    sample_iter=iter(samples);manager_iter=iter(managers) if managers else None
    return stable_actor('api',lambda _:next(manager_iter) if manager_iter else manager.copy(),lambda _:next(sample_iter))
check(observe([ordinary,ordinary])=={**manager,**expected})
# A literal race from status(root) then argv(ordinary); not a valid ordinary identity.
mixed=copy.deepcopy(ordinary);mixed['process']['Uid']='0 0 0 0'
check(mixed['entry'].endswith('ApiProcessMain') and mixed['process']['Uid'].split()!=['20']*4)
check(observe([mixed,ordinary,ordinary,ordinary])=={**manager,**expected})
for key in ordinary['process']:
    changed=copy.deepcopy(ordinary);changed['process'][key]='different'
    check(observe([changed,ordinary,ordinary,ordinary])=={**manager,**expected})
for key in ['_argv','_cgroup','startTicks','entry']:
    changed=copy.deepcopy(ordinary);changed[key]=b'different' if key.startswith('_') else 101 if key=='startTicks' else 'other'
    check(observe([changed,ordinary,ordinary,ordinary])=={**manager,**expected})
drift={**manager,'InvocationID':'2'*32}
check(observe([ordinary]*4,[manager,drift,manager,manager])=={**manager,**expected})
check(observe([root,ordinary]*3).get('race') is True)
zero={**manager,'MainPID':'0'};check(observe([], [zero,zero])==zero)
calls=0
def vanished(_):
    global calls
    calls+=1
    if calls==1:raise FileNotFoundError('synthetic vanished')
    return ordinary
check(stable_actor('api',lambda _:manager.copy(),vanished)=={**manager,**expected})
print('PG457_OBSERVER_TOOL_PASS independentAssertions='+str(count)+' productionPt0=true stableRaceRejected=true capturedRootFabricated=false')
