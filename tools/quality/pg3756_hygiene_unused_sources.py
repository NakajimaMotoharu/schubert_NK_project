"""Pure new-role factory from pinned successful18; completed tuple is data, never new authority."""
import ast
from functools import lru_cache
import hashlib
import json
import re
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg3434_current_outbox_candidate_sources as previous
import pg3600_current_browser_owned_sources as completed

CURRENT='4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
CURRENT_BOM='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'
SOURCE='7fffab57a567914956b66452e5e54388642efdec'
BOM='652915c694fe6120af81587195150d7df8bcc411b7eb4f5d74cf3f71fd87517b'
BEFORE='c85b34d3b0f5c859db9579d48c2c27a1205dd69d9f671b27407a842da8ac46db'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'
TOOLS='pg3756-hygiene-unused-tools-v1';SAVE='pg3760-hygiene-unused-placement-v1'
ARCHIVE='pg3760-hygiene-release-v1.tar';REMOTE='/home/ubuntu/pg3760-hygiene-input-v1'
BASE=W/previous.TOOLS;LATEST=W/completed.TOOLS
VIEW_LOCAL=W/'pg3754-current-before-view-v1/manifest.safe.json'


def pinned(folder,name):
    expected=json.loads((folder/'payload-sha256.json').read_bytes());raw=(folder/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected[name]:raise ValueError('original successful frozen source changed')
    return raw.decode()


def role_text(raw):
    # Single pass prevents current/candidate collisions; SHA fragments and historical UUIDs are untouched.
    pairs={previous.CURRENT:CURRENT,previous.SOURCE:SOURCE,previous.CURRENT_BOM:CURRENT_BOM,previous.BOM:BOM,previous.BEFORE:BEFORE,'PG3420':'PG3748','pg3420':'pg3748','PG2802':'PG3420','pg2802':'pg3420','pg3432-current-a9-before-view-v2':'pg3754-current-4856-before-view-v1',previous.TOOLS:TOOLS,previous.SAVE:SAVE,previous.ARCHIVE:ARCHIVE,previous.REMOTE:REMOTE,'pg3434':'pg3756','Pg3434':'Pg3756','PG3434':'PG3756','pg3436':'pg3758','PG3436':'PG3758','pg3438':'pg3760','PG3438':'PG3760','pg3440':'pg3762','PG3440':'PG3762'}
    pattern='|'.join(re.escape(k)for k in sorted(pairs,key=len,reverse=True))
    def replace(match):
        old=match.group();a,b=match.span()
        if re.fullmatch('[a-f0-9]{40,64}',old)and ((a>0 and raw[a-1]in '0123456789abcdefABCDEF')or(b<len(raw)and raw[b]in '0123456789abcdefABCDEF')):return old
        return pairs[old]
    return re.sub(pattern,replace,raw)


def qualify():
    ro=json.loads((W/'pg3752-current-preservation-readonly-v1/manifest.safe.json').read_bytes());view=json.loads(VIEW_LOCAL.read_bytes());signed=json.loads((W/'pg3748-candidate-build-v1.safe.json').read_bytes())
    if not(ro['actualExit']==view['actualExit']==signed['actualExit']==0 and ro['result']['deployedSource']==view['result']['productionSource']==CURRENT and ro['result']['BOM']==CURRENT_BOM and view['result']['privateBeforeSha256']==BEFORE and view['result']['dataOnlyNotRuntimeAuthority']and view['result']['nativeCandidateCredit']is False and view['result']['nativePhysicalFilesPreserved']==34 and signed['candidateSource']==SOURCE and signed['manifestSha256']==BOM and signed['signatureVerified']and signed['candidateNotDeployed']):raise ValueError('separate fresh current-data and signed candidate authorities required')


@lru_cache(maxsize=1)
def current_tuple():
    current=previous.binding(pinned(LATEST,'pg3600_parent_receipt.py'));_,_,summary,ended=completed.context()
    if current['boot']!=BOOT.replace('-','')or not summary['genuineParentDone']or summary['completionCode']!=10:raise ValueError('actual latest completed Root tuple required, not live authority')
    return current,summary,ended


def native_refs(raw):
    current,summary,_=current_tuple();tree=ast.parse(raw);hits={'INV':0,'START':0,'END':0,'DONE_PATH':0};old=previous.binding(pinned(BASE,'pg3434_parent_receipt.py'))
    class Positive(ast.NodeTransformer):
        def visit_Assign(self,node):
            node=self.generic_visit(node)
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in {'INV','START','END'}:
                key=node.targets[0].id;replacement={'INV':current['invocation'],'START':current['start'],'END':summary['endMonotonicUs']}[key];node.value=ast.Constant(replacement);hits[key]+=1
            return node
        def visit_Constant(self,node):
            if node.value=='/var/lib/schubert-nk/maintenance/attempts/'+old['activation']+'.done':hits['DONE_PATH']+=1;return ast.copy_location(ast.Constant('/var/lib/schubert-nk/maintenance/attempts/'+current['activation']+'.done'),node)
            return node
    result=ast.unparse(ast.fix_missing_locations(Positive().visit(tree)))
    if hits!={'INV':1,'START':1,'END':1,'DONE_PATH':1}:raise ValueError('four exact latest completed native-ref positive fields')
    return result


def sources(bom=BOM,before=BEFORE):
    qualify()
    if bom!=BOM or before!=BEFORE:raise ValueError('one fixed current/candidate data role')
    names=sorted(p.name for p in BASE.iterdir()if p.suffix in {'.py','.java'});values={role_text(n):role_text(pinned(BASE,n))for n in names}
    if len(values)!=18:raise ValueError('exact pinned original eighteen source roles')
    for suffix in ['parent_receipt','warning_parent_projection']:
        values['pg3756_'+suffix+'.py']=pinned(LATEST,'pg3600_'+suffix+'.py').replace('pg3600','pg3756').replace('PG3600','PG3756')
    raw=pinned(LATEST,'Pg3600NativeStop.java');start=raw.index('  static void verifyOriginalValues(');end=raw.index('\n  static void verifyOriginal()',start);method=raw[start:end]
    java=values['Pg3756UnusedStage.java'];start=java.index('  static void verifyOriginalValues(');end=java.index('\n  static void verifyOriginal()',start);values['Pg3756UnusedStage.java']=java[:start]+method+java[end:]
    # Namespace-only copy leaves every historical/negative UUID test input unchanged.
    values['Pg3756OriginalTupleTest.java']=pinned(LATEST,'Pg3600OriginalTupleTest.java').replace('Pg3600NativeStop','Pg3756UnusedStage').replace('Pg3600','Pg3756').replace('PG3600','PG3756')
    values['pg3756_native_refs.py']=native_refs(values['pg3756_native_refs.py'])
    for name,raw in values.items():
        if previous.CURRENT in raw or previous.BEFORE in raw or previous.CURRENT_BOM in raw:raise ValueError('historical positive current role in '+name)
        if name.endswith('.py'):
            prelude="BUNDLE_HASH='pending-real-bundle'\n"if name in ['pg3756_native_refs.py','pg3756_input_preflight.py']else ''
            if check(prelude+raw,'<new current4856 candidate7fff role>'):raise ValueError('complete whole role namespace')
            compile(prelude+raw,'<new unused graph only>','exec')
    if previous.binding(values['pg3756_parent_receipt.py'])!=current_tuple()[0]:raise ValueError('exact latest current completed data binding')
    return values


if __name__=='__main__':raise SystemExit('factory only; no VM operation')
