"""New selection with genuine tests in every required reactor module; NoTests stays fatal."""
import inspect
import subprocess
import pg4412_shared_manager_selected as template

WORK=template.ROOT.parent/'pgpt-runs/PG379/pg4670-root-self-identity-selected-v1'
PREFIX='dev.codex.schubert.nk.'
MODULES={
 PREFIX+'protocol.layout.LayoutMetadataTest':'protocol',
 PREFIX+'storage.ResourceScopeTest':'storage',
 PREFIX+'bootstrap.MaintenanceOwnerFrameTest':'bootstrap',
 PREFIX+'api.bootstrap.ApiStartupInputsTest':'api',
 PREFIX+'web.bootstrap.WebStartupInputsTest':'web',
 **{PREFIX+'batch.file.'+n:'batch'for n in ['RootStartupPendingTest','StartupLaunchRecordTest','MorningStartupLaunchOwnerAdmissionTest']}}


def validate_selection(modules,root):
    required={'protocol','storage','bootstrap','api','web','batch'}
    if type(modules)is not dict or set(modules.values())!=required or any(type(n)is not str or not n.startswith(PREFIX)for n in modules):raise ValueError('all six physical module selections first')
    paths=[]
    for name,module in modules.items():
        path=root/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
        if not path.is_file()or '@Test'not in path.read_text():raise ValueError('actual physical Test path/method required')
        paths.append(path)
    if len(paths)!=len(set(paths)):raise ValueError('unique physical suites first')


def source():
    raw=inspect.getsource(template.main)
    raw=raw.replace("module = 'batch' if '.batch.' in name else 'bootstrap'","module = MODULES[name]")
    first=raw.index("                if entry.get('name') in [");last=raw.index(':\n                    counters[entry.get',first)
    raw=raw[:first]+"                if entry.get('name') == 'dev/codex/schubert/nk/batch/file/RootStartupPending'"+raw[last:]
    raw=raw.replace('actual = {}; xmls = {}; counters = {}; reasons = []','actual = {}; xmls = {}; counters = {}; reasons = []; method_counters = {}')
    marker="    if actual != expected: reasons.append('selected identity inventory differs')"
    extra="""    if counters:
        entry=next(e for e in ET.parse(snapshot/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot().findall('package/class') if e.get('name')=='dev/codex/schubert/nk/batch/file/RootStartupPending')
        methods=[m for m in entry.findall('method')if m.get('name')=='verifySelf']
        if len(methods)!=1:reasons.append('one target method required')
        else:method_counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in methods[0].findall('counter')}
    if not method_counters or any(method_counters.get(k,{}).get('missed')!=0 for k in ['LINE','METHOD','BRANCH']):reasons.append('target identity conditions incomplete')
"""
    if raw.count(marker)!=1:raise ValueError('one inventory qualification boundary')
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'coverage': counters,","'coverage': counters, 'targetMethodCoverage':method_counters,")
    raw=raw.replace("'sourceRole': 'unaccepted candidate; deployed source remains7bb'","'sourceRole': 'test-only fixed snapshot; deployed Main964e unchanged/ordinary stopped'")
    return raw


def main():
    validate_selection(MODULES,template.ROOT)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed selected scope first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(template),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES}
    exec(compile(source(),'<all six actual reactor selections; strict NoTests>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
