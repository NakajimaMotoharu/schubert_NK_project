"""Required fresh whole after factory manufacture; preserve original six-format/static contract."""
import ast
import inspect
import json
import subprocess
import pg4420_shared_manager_full as driver
import pg5128_root_full as previous
import pg5404_process_query_selected as selected
from pg5406_process_query_bytecode import SOURCE,RUN,OUT

ROOT,W=driver.ROOT,driver.W
LABEL='PG5414'
READONLY=(
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/storage/ApiApplicationPreparation.java',
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/file/InspectorApplication.java',
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain.java',
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java')


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5128',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value in {3814,556,1654}:
                return ast.copy_location(ast.Constant({3814:3896,556:562,1654:1664}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    compile(raw,'<required ownership all3896/562/1664>','exec')
    return raw


def main():
    run=W/RUN;result=json.loads((run/'manifest.safe.json').read_bytes())
    if not(type(result['actualExit']) is int and result['actualExit']==0 and result['phaseExits']==[0,0]
           and result['sourceSnapshot']==SOURCE and result['tests']==1164 and result['suites']==137 and not result['reasons']):
        raise ValueError('current genuine selected1164/137 all gates before fresh whole')
    selected.configure()
    if selected.selected.main_delta(run/'source','factory')!=result['mainDelta']:
        raise ValueError('all current selected767 bytes and exact named growth')
    proof=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/OUT/'manifest.json').read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0 or proof['physicalMain']!=767 or any(
        value['missed'] for counters in proof['targetClassCounters'].values() for value in counters.values()):
        raise ValueError('actual query prefix/null-admission/old-use and all four100 first')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--',*READONLY],cwd=ROOT):
        raise ValueError('readonly candidates changed; require fresh source review before this plan')
    raw=inspect.getsource(driver.main).replace('pg4420','pg5414').replace('shared-manager','ownership-query')
    old="'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(old)!=1:raise ValueError('one original planned whole inventory')
    raw=raw.replace(old,"'tests': 3896, 'suites': 562, 'mainClasses': 1664")
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
        'SSC308 factory ownership manufacture; fresh selected1164/137 qualified; original3814 plus82 exact new methods/no removed method; all1664 physical Main; readonly TWR/preowner actual audit pending; no old native/counters imported')
    namespace={**vars(driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<required ownership whole once>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
