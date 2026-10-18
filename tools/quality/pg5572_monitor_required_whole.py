"""One necessary current shared-owner monitor whole3904, never old3900 confirmation replay."""
import ast
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg5550_snapshot_required_whole as previous
from pg5570_monitor_public import SOURCE

ROOT,W=previous.ROOT,previous.W
LABEL='PG5572'
SLOT='pg5572-monitor-six-v1'


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5550',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3900:return ast.copy_location(ast.Constant(3904),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<monitor3904 complete standalone>'):raise ValueError('all standalone dependencies before output')
    compile(raw,'<one actual3904 fixed source>','exec')
    return raw


def prerequisites():
    selected_path=W/'pg5566-private-monitor-green-v2/manifest.safe.json';proof_path=W/'pg5568-monitor-bytecode-v2/manifest.safe.json'
    import hashlib
    if hashlib.sha256(selected_path.read_bytes()).hexdigest()!='27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50'or hashlib.sha256(proof_path.read_bytes()).hexdigest()!='fb7917b4b9d9944f0cf3a6fb286d173569e31193ab1e8fbc31cf3f2f91d554ec':raise ValueError('immutable selected and independent post')
    selected=json.loads(selected_path.read_bytes());proof=json.loads(proof_path.read_bytes())
    if not(selected['sourceSnapshot']==proof['sourceSnapshot']==SOURCE and selected['greenSelectedQualified']and selected['actualCases']==71
        and selected['physicalMain']['count']==1664 and proof['actualExit']==0 and sum(map(len,proof['privateMonitorMethods'].values()))==14
        and len(proof['allPhysicalDifferenceClassifications'])==11):raise ValueError('all actual71/1664/private14/physical11 first')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean operator before new required whole')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('canonical2fc Main/Test/config fixed')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.preflight()
    os.umask(0o077)
    with(W/'pg5572-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    raw=inspect.getsource(previous.previous.driver.main).replace('pg4420','pg5572').replace('shared-manager','monitor')
    marker="'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(marker)!=1:raise ValueError('one exact original planned inventory')
    raw=raw.replace(marker,"'tests': 3904, 'suites': 563, 'mainClasses': 1664",1)
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
        'BUG1459 shared owner monitor correction; actual selected71/private14/all11 physical classified; old3900 retained plus four new independent methods; no old native imported')
    marker="'archiveSha256': digest, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),"
    if raw.count(marker)!=1:raise ValueError('one actual pre-dispatch identity boundary')
    raw=raw.replace(marker,marker+"'operatorBranch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'serverPreflight':"+repr(fresh)+',',1)
    scope={**vars(previous.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<one fixed2fc whole3904>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
