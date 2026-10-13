"""Current-boot ten native points; zero oldboot files, actual Root/Inspector/Backup PID1 windows."""
import ast
import inspect
import json
from pyflakes.api import check
import pg2100_current_newrun_native_catalog as template
import pg2042_fresh_normal_warning_native_catalog as transport
from pg2246_newboot_owned_sources import SOURCE,TOOLS
from pg2208_current_newboot_cold_sources import BOOT
from pg1446_current_cold_stage import W

SLOT='pg2254-newboot-native-catalog-v1'


def inspector_window(rows,boot,root_start,root_end):
    import re
    if type(boot)is not str or re.fullmatch('[a-f0-9]{32}',boot)is None or type(root_start)is not int or type(root_end)is not int or not 0<root_start<=root_end<=root_start+1800000000:raise ValueError('exact current Root budget boundary required')
    if type(rows)is not list or not rows:raise ValueError('same current Root Inspector journal required')
    fixed={'_BOOT_ID':boot,'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-inbox-inspector.service'}
    inv=set();cursors=set()
    for row in rows:
        if type(row)is not dict or any(row.get(k)!=v for k,v in fixed.items()):raise ValueError('current Inspector identity required')
        generation=row.get('INVOCATION_ID');stamp=row.get('__MONOTONIC_TIMESTAMP');cursor=row.get('__CURSOR')
        if type(generation)is not str or re.fullmatch('[a-f0-9]{32}',generation)is None:raise ValueError('one exact generation required')
        inv.add(generation)
        if type(stamp)is not str or not stamp.isdecimal() or not root_start<=int(stamp)<=root_end:raise ValueError('original current Root budget required')
        if type(cursor)is not str or not cursor or cursor in cursors or row.get('JOB_RESULT')not in(None,'done'):raise ValueError('unique genuine normal journal required')
        cursors.add(cursor)
    if len(inv)!=1:raise ValueError('only sameRoot Inspector generation allowed')
    groups=[[r for r in rows if r.get('MESSAGE_ID')==message and all(r.get(k)==v for k,v in extra.items())]for message,extra in [
      ('7d4958e842da4a758f6c1cdc7b36dcc5',{'JOB_TYPE':'start'}),('39f53479d3a045ac8e11786248231fbf',{'JOB_TYPE':'start','JOB_RESULT':'done'}),('7ad2d189f7e94e70a38c781354912448',{}),('9d1aaa27d60140bd96365438aad20286',{'JOB_TYPE':'stop','JOB_RESULT':'done'})]]
    if any(len(g)!=1 for g in groups):raise ValueError('four unique Inspector normal events required')
    start_job=groups[0][0].get('JOB_ID');stop_job=groups[3][0].get('JOB_ID')
    if any(type(v)is not str or not v.isdecimal()or int(v)<=0 for v in [start_job,stop_job]) or groups[1][0].get('JOB_ID')!=start_job or stop_job==start_job:raise ValueError('actual distinct normal jobs required')
    times=[int(g[0]['__MONOTONIC_TIMESTAMP'])for g in groups]
    if times!=sorted(times):raise ValueError('Inspector event order required')
    return times[0],times[2],next(iter(inv))


def catalog_source(receipt,binding,end):
    stub="def completed(*args):raise ValueError('body-only source placeholder; never executed')\n"
    raw=template.catalog_source(stub)[len(stub)+1:]
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='inspector_window')
    raw=raw.replace(ast.get_source_segment(raw,node),inspect.getsource(inspector_window))
    pairs=[('pg2090-native-stop-v1','pg2246-native-stop-v1'),('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-','')),('9026b2ab-bb42-49cd-a2bd-4c661049dce3',binding['activation']),('113070840714',str(binding['start'])),('114755353173',str(end)),("r.get('JOB_ID')=='204748'","r.get('JOB_ID')=="+repr(binding['job']))]
    for old,new in pairs:raw=raw.replace(old,new)
    first=raw.index("archive=base/'pg2072-current-noargs-newrun-once-v1'");last=raw.index("native=pathlib.Path",first)
    raw=raw[:first]+"frozen=json.loads((base/'pg2227-newboot-fresh-day-once-v1/before.private.json').read_bytes());require(frozen['ordinaryNoargs']and frozen['existingSuccessfulInspectorStepsForDate']==0 and frozen['current']['boot']=="+repr(BOOT)+" and frozen['current']['source']=="+repr(SOURCE)+")\nrequire(set(frozen['runtime']['children'])=={'backup','cleanup','expiry','inspector','ordinary-api193','ordinary-bootstrap196','ordinary-inspector196','ordinary-web193','parent','root-api','root-api193','root-web193'}and all(v[5]==2 for v in frozen['runtime']['children'].values()))\nold={} # current boot was qualified empty in actual finite-before/start, not an oldnative import\n"+raw[last:]
    first=raw.index('inspector_rows=[json.loads');last=raw.index('require(closing not in old',first)
    raw=raw[:first]+"inspector_rows=[json.loads(l)for l in inspector_raw.splitlines()];inspector_rows=[r for r in inspector_rows if ROOT_START<=int(r['__MONOTONIC_TIMESTAMP'])<=ROOT_END]\ninspector_start,inspector_end,INSPECTOR_INV=inspector_window(inspector_rows,"+repr(BOOT.replace('-',''))+",ROOT_START,ROOT_END)\nclosing='ordinary-inspector196/'+INSPECTOR_INV+'.closing.exec'\nearlier='ordinary-inspector196/'+INSPECTOR_INV+'.terminal.exec'\n"+raw[last:]
    raw=raw.replace("'oldThirtyTwoArchiveUnchanged':True","'currentBootHadNoHistoricalNative':True,'oldNativeImported':False")
    raw=receipt+'\n'+raw
    if check('SEALS={}\n'+raw,'<actual whole currentboot catalog>'):raise ValueError('whole native exports required')
    compile(raw,'<actual current native point eligibility>','exec');return raw


def main():
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or term['actualExit']!=0 or live['binding']['boot']!=BOOT.replace('-',''):raise ValueError('actual current source/run/terminal required')
    raw=inspect.getsource(transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2252-newboot-owned-stop-post-v1').replace('pg2030_parent_receipt.py','pg2246_parent_receipt.py')
    ns={**transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<current newboot native catalog transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
