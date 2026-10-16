"""Unexecuted current completed-resume graph from pinned bytes and latest completed tuple."""
import ast
import json
from pyflakes.api import check
import pg3564_current_browser_resume_sources as previous
import pg3822_hygiene_owned_sources as owned
from pg3756_hygiene_unused_sources import pinned
from pg1446_current_cold_stage import W

SOURCE=owned.SOURCE;BOM=owned.BOM;BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'
RUN='f29290f8-69ed-49fe-9f2f-33b4efdea422'
BEFORE='3459bd3d705f463c006b0bb3ffafb47ea7896c5c226f3f067e18600dd1e9aec3'
BASELINE='/var/lib/pgpt-s1-preservation/pg3842-current-full11-native-baseline-v1/before.private.json'
TOOLS='pg3844-current-resume-tools-v1';SAVE='pg3848-current-resume-preparation-v1';CLASS='Pg3844FreshResumePreparation'
BASE=W/previous.TOOLS;CURRENT=W/owned.TOOLS


def bind(raw):
    for a,b in [(previous.TOOLS,TOOLS),(previous.SAVE,SAVE),(previous.BASELINE,BASELINE),(previous.BEFORE,BEFORE),(previous.SOURCE,SOURCE),(previous.BOM,BOM),('PG3420','PG3748'),('pg3420','pg3748'),('pg3564','pg3844'),('Pg3564','Pg3844'),('PG3564','PG3844'),('pg3566','pg3846'),('pg3568','pg3848'),('pg3570','pg3850'),('PG3570','PG3850')]:raw=raw.replace(a,b)
    return raw


def sources():
    proof=json.loads((W/'pg3842-current-full11-native-baseline-v1/manifest.safe.json').read_bytes());result=proof.get('result',{})
    if proof.get('actualExit')!=0 or result.get('source')!=SOURCE or result.get('privateBeforeSha256')!=BEFORE or result.get('snapshotKeys')!=11 or result.get('nativeExecs')!=40 or result.get('newTenRefsReturnedNormally')is not True or result.get('runtimeOnlyOriginalEmptyParent')is not True:raise ValueError('fresh strict full11/native40 current data required')
    live=json.loads((W/'pg3804-hygiene-current-live-binding-v1/manifest.safe.json').read_bytes());term=json.loads((W/'pg3808-hygiene-current-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or term['actualExit']!=0 or live['binding']['run']!=RUN or term['productionSource']!=SOURCE or not term['genuineParentDone']:raise ValueError('actual current completed Root data required')
    names=sorted(n for n in json.loads((BASE/'payload-sha256.json').read_bytes())if n.endswith(('.java','.py')))
    values={bind(n):bind(pinned(BASE,n))for n in names}
    for suffix in ['parent_receipt','warning_parent_projection','configuration','configuration_capture','row_bound','stable_journal']:
        values['pg3844_'+suffix+'.py']=pinned(CURRENT,'pg3822_'+suffix+'.py').replace('pg3822','pg3844').replace('PG3822','PG3844')
    values['Pg3844OriginalTupleTest.java']=pinned(CURRENT,'Pg3822OriginalTupleTest.java').replace('Pg3822NativeStop',CLASS).replace('Pg3822','Pg3844').replace('PG3822','PG3844')
    actual=pinned(CURRENT,'Pg3822NativeStop.java');a=actual.index('  static void verifyOriginalValues(');b=actual.index('\n  static void verifyOriginal()',a)
    raw=values[CLASS+'.java'];start=raw.index('  static void verifyOriginalValues(');end=raw.index('\n  static void verifyOriginal()',start);values[CLASS+'.java']=raw[:start]+actual[a:b]+raw[end:]
    # Only positive selected-run constants in these three non-fixture files.
    for name in [CLASS+'.java','pg3844_runtime_writer.py','pg3844_resume_contract.py']:
        values[name]=values[name].replace(previous.RUN,RUN)
    raw=values['pg3844_native_refs.py'];tree=ast.parse(raw);binding=live['binding'];hits={key:0 for key in ['INV','START','END','DONE']}
    class Positive(ast.NodeTransformer):
        def visit_Assign(self,node):
            node=self.generic_visit(node)
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in {'INV','START','END'}:
                key=node.targets[0].id;node.value=ast.Constant({'INV':binding['invocation'],'START':binding['start'],'END':term['endMonotonicUs']}[key]);hits[key]+=1
            return node
        def visit_Constant(self,node):
            if node.value=='/var/lib/schubert-nk/maintenance/attempts/225691a3-e748-42c4-8972-5ffda5de893d.done':hits['DONE']+=1;return ast.copy_location(ast.Constant('/var/lib/schubert-nk/maintenance/attempts/'+binding['activation']+'.done'),node)
            if node.value=='/proc/321930':return ast.copy_location(ast.Constant('/proc/'+str(live['rootPid'])),node)
            return node
    values['pg3844_native_refs.py']=ast.unparse(ast.fix_missing_locations(Positive().visit(tree)))
    if hits!={'INV':1,'START':1,'END':1,'DONE':1}or len(values)!=20:raise ValueError('exact twenty roles and positive Root fields')
    for name,raw in values.items():
        if name.endswith('.py'):
            if check(raw,'<whole new current resume source>'):raise ValueError('complete new graph namespace')
            compile(raw,'<unexecuted current resume graph>','exec')
    return values
