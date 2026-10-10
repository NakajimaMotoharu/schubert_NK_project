"""Three actual owned host JVMs, explicit late dump retained; exact class only."""
import inspect
import xml.etree.ElementTree as ET
import pg1273_stop_hold_selected_counter as previous
from pg1271_current_native_gap import require


def qualify(raw, lower_ms, upper_ms):
    root=ET.fromstring(raw);sessions=root.findall('sessioninfo')
    require(3<=len(sessions)<=4)
    groups={}
    for s in sessions:
        start=int(s.attrib['start']);dump=int(s.attrib['dump']);require(lower_ms<=start<=dump<=upper_ms)
        groups.setdefault(s.attrib['id'],[]).append((start,dump))
    require(len(groups)==3 and all(len(v)<=2 and len({a for a,b in v})==1 for v in groups.values()))
    classes=[c for p in root.findall('package')for c in p.findall('class')if c.attrib['name']=='dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHold']
    require(len(classes)==1)
    counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in classes[0].findall('counter')}
    require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH']))
    return {'sessionCount':3,'rawSessionRecords':len(sessions),'allSessionBoundsMatched':True,'sameClassByteMatch':True,'classCounters':counters,'wholeBootstrapOrFormalAccepted':False}


def main():
    source=inspect.getsource(previous.main).replace('pg1272-stop-hold-selected-v1','pg1274-stop-hold-selected-v2').replace('pg1273-stop-hold-selected-counter-v1','pg1275-stop-hold-selected-counter-v2').replace("'tests':6","'tests':7").replace('testCount=6','testCount=7')
    env=dict(previous.__dict__);env['qualify']=qualify
    exec(compile(source,'<new-only selected real late capture class qualification>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
