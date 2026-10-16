"""SSC301 exact API identities and actual helper counters; no VM or native acceptance."""
import inspect
import subprocess
import pg4412_shared_manager_selected as template

ROOT=template.ROOT
WORK=ROOT.parent/'pgpt-runs/PG379/pg4836-api-admitted-config-selected-v1'
TESTS=['dev.codex.schubert.nk.api.bootstrap.'+name for name in ('ApiAdmittedConfigurationTest','ApiProcessMainTest','ApiStartupInputsTest','ApiConfigurationLoaderTest')]
MODULES={name:'api'for name in TESTS}


def source():
    raw=inspect.getsource(template.main)
    raw=raw.replace("module = 'batch' if '.batch.' in name else 'bootstrap'","module = MODULES[name]")
    raw=raw.replace("'-pl', 'src/schubert-nk-batch'","'-pl', 'src/schubert-nk-api'")
    raw=raw.replace("'sourceRole': 'unaccepted candidate; deployed source remains7bb'","'sourceRole': 'unaccepted SSC301 candidate; deployed825e remains unchanged'")
    marker="    if actual != expected: reasons.append('selected identity inventory differs')"
    extra="""    tree=ET.parse(snapshot/'src/schubert-nk-api/target/site/jacoco/jacoco.xml').getroot()
    methods=[m for c in tree.findall('package/class')if c.get('name')=='dev/codex/schubert/nk/api/bootstrap/ApiProcessMain'for m in c.findall('method')if m.get('name')=='admittedConfiguration']
    if len(methods)!=1:reasons.append('one actual admitted configuration helper required')
    else:
        counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in methods[0].findall('counter')}
        if any(counters.get(k,{'missed':0})['missed']!=0 for k in ['LINE','METHOD','BRANCH']):reasons.append('all actual helper lines/method/conditions must be covered')
"""
    if raw.count(marker)!=1:raise ValueError('one actual XML validation boundary')
    return raw.replace(marker,extra+marker)


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed candidate first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(template),'SOURCE':head,'WORK':WORK,'TESTS':TESTS,'MODULES':MODULES}
    exec(compile(source(),'<same actual API helper selected tests>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
