"""SSC304 exact source selection: literal/TWR oracle plus actual isolated PostgreSQL; no VM."""
import json
import subprocess
import pg4950_backup_retention_selected as previous

ROOT=previous.ROOT
WORK=ROOT.parent/'pgpt-runs/PG379/pg4956-expiry-success-selected-v1'
DEPLOYED=previous.MAIN_SOURCE
REPO='dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository'
MODULES={
 'dev.codex.schubert.nk.storage.ServiceConfigFilesTest':'storage',
 'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest':'bootstrap',
 **{'dev.codex.schubert.nk.batch.repository.'+name:'batch'for name in (
     'ExpirySuccessfulScopeTest','ExpiryAuditRepositoryTest','MorningExpiryObservationInvariantTest','MorningExpirySessionTest')},
 'dev.codex.schubert.nk.batch.file.CleanupExpiryExecutionTest':'batch'}
METHODS={REPO:('verifySuccessfulAudit','usingJdbc','lambda$successful$2')}
MAIN_PATH='src/schubert-nk-batch/src/main/java/'+REPO+'.java'


def validate_selection():
    if len(MODULES)!=7 or set(MODULES.values())!={'storage','bootstrap','batch'}:
        raise ValueError('exact actual required selection')
    changed=subprocess.check_output(['git','diff','--name-only',DEPLOYED,'HEAD','--',
        ':(glob)src/*/src/main/**'],cwd=ROOT,text=True).splitlines()
    if changed!=[MAIN_PATH]:raise ValueError('only SSC304 Main source may differ from deployed')
    for name,module in MODULES.items():
        path=ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
        if not path.is_file()or '@Test'not in path.read_text():raise ValueError('actual physical required tests')
        if '<failIfNoTests>true</failIfNoTests>'not in(ROOT/('src/schubert-nk-'+module+'/pom.xml')).read_text():
            raise ValueError('strict NoTests contract retained')


def verify_main_bytes(snapshot):
    value=json.loads(previous.FULL.read_bytes());q=value['result']
    if value['actualExit']!=0 or q['productionSource']!=DEPLOYED or q['mainClasses']!=1647:
        raise ValueError('actual original deployed reference')
    expected={k:v for k,v in q['allPhysicalMainSha256'].items()if k.split(':',1)[0]in set(MODULES.values())}
    actual={m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix():previous.base.sha(p)
            for m in set(MODULES.values())for p in(snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    changed={k for k in expected.keys()&actual.keys()if expected[k]!=actual[k]}
    added=set(actual)-set(expected);removed=set(expected)-set(actual)
    if changed!={'batch:'+REPO+'.class'}or removed or added!={
        'batch:'+REPO+'$JdbcRelease.class','batch:'+REPO+'$JdbcRead.class'}:
        raise ValueError('exact one changed outer and two declared internal interfaces; no other Main drift')
    return {'deployedSource':DEPLOYED,'candidateSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'selectedPhysicalMain':len(actual),'unchangedPhysicalMain':len(expected)-len(changed),
        'changedPhysicalMain':sorted(changed),'addedPhysicalMain':sorted(added),'removedPhysicalMain':[],
        'deployedSourceUnchanged':True,'oldNativeImported':False}


def source():
    raw=previous.source()
    raw=raw.replace("'test-only selection; signedProduction04bb unchanged'", "'unaccepted SSC304 candidate; signed deployed04bb unchanged'")
    raw=raw.replace("'sameMain':main_bytes", "'mainDelta':main_bytes")
    raw=raw.replace('target retained method conditions incomplete:', 'SSC304 predicate/scope conditions incomplete:')
    raw=raw.replace('one actual retained method required:', 'one actual SSC304 method required:')
    old="                if not {'LINE','METHOD','BRANCH'}<=set(count)or any(count[k]['missed']for k in ('LINE','METHOD','BRANCH')):"
    new="                needed={'LINE','METHOD'}|({'BRANCH'}if name!='usingJdbc'or 'BRANCH'in count else set())\n                if not needed<=set(count)or any(count[k]['missed']for k in needed):"
    if raw.count(old)!=1:raise ValueError('one actual method-counter applicability boundary')
    raw=raw.replace(old,new)
    marker="                count={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in matches[0].findall('counter')}"
    if raw.count(marker)!=1:raise ValueError('one actual lambda signature boundary')
    raw=raw.replace(marker,marker+"\n                if name=='lambda$successful$2'and (not matches[0].get('desc','').startswith('(Ljava/sql/ResultSet;')or count.get('BRANCH',{}).get('covered')!=8):reasons.append('actual eight-condition ResultSet body required')")
    return raw


def main():
    validate_selection()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean frozen SSC304 source first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    ns={**vars(previous.base),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES,
        'MAIN_SOURCE':head,'METHODS':METHODS,'verify_main_bytes':verify_main_bytes}
    exec(compile(source(),'<SSC304 independent late audit and exact lexical JDBC>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
