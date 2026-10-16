"""SSC301/302 exact related six-module scope, both real helper predicates and original DB PT."""
import ast
import subprocess
import pg4840_api_config_complete_selection as previous

ROOT=previous.ROOT
WORK=ROOT.parent/'pgpt-runs/PG379/pg4842-expiry-audit-selected-v1'
MODULES={**previous.MODULES,
 'dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest':'web',
 'dev.codex.schubert.nk.batch.file.CleanupExpiryExecutionTest':'batch',
 'dev.codex.schubert.nk.batch.file.RetainedExpiryAuditTest':'batch'}
PROJECTS=','.join('src/schubert-nk-'+name for name in ('protocol','storage','bootstrap','api','web','batch'))


def validate_selection():
    previous.validate_selection()
    if set(MODULES.values())!={'protocol','storage','bootstrap','api','web','batch'}or len(MODULES)!=10:raise ValueError('exact all-six related suite set')
    for name,module in MODULES.items():
        p=ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
        if not p.is_file()or '@Test'not in p.read_text():raise ValueError('actual nonempty physical test required')


def source():
    raw=previous.source()
    if raw.count("'-pl', 'src/schubert-nk-api'")!=1:raise ValueError('one exact project selection')
    raw=raw.replace("'-pl', 'src/schubert-nk-api'","'-pl', "+repr(PROJECTS))
    tree=ast.parse(raw);main=tree.body[0]
    at=next(i for i,n in enumerate(main.body)if isinstance(n,ast.If)and ast.unparse(n.test)=='actual != expected')
    extra=ast.parse("""
combined={'api.admittedConfiguration':counters}
batch_cov=snapshot/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
if not batch_cov.exists():reasons.append('batch helper coverage absent, never accepted')
else:
    batch=ET.parse(batch_cov).getroot()
    for name in ['verifyPriorAudit','verifyPriorExpiry']:
        methods=[m for c in batch.findall('package/class')if c.get('name')=='dev/codex/schubert/nk/batch/file/CleanupExpiryExecution'for m in c.findall('method')if m.get('name')==name]
        if len(methods)!=1:reasons.append('one actual '+name+' required')
        else:
            count={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in methods[0].findall('counter')}
            combined['batch.'+name]=count
            if any(count.get(k,{'missed':0})['missed']!=0 for k in ['LINE','METHOD','BRANCH']):reasons.append('actual '+name+' conditions incomplete')
counters=combined
""").body
    main.body[at:at]=extra
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    validate_selection()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed related candidate')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.previous.previous.template),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES}
    exec(compile(source(),'<exact all-six related API/Expiry real methods>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
