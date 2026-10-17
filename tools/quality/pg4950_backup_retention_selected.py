"""Test-only current Backup retention negatives: exact reactor/PT/Main bytes, no VM."""
import inspect
import json
import subprocess
import pg4412_shared_manager_selected as base
import wbs_candidate_trace as trace

ROOT=base.ROOT
WORK=ROOT.parent/'pgpt-runs/PG379/pg4950-backup-retention-selected-v1'
MAIN_SOURCE='04bbdb73b532537e3546191d72dee913b17629a0'
FULL=ROOT.parent/'pgpt-runs/PG379/pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json'
MODULES={
 'dev.codex.schubert.nk.storage.ServiceConfigFilesTest':'storage',
 'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest':'bootstrap',
 **{'dev.codex.schubert.nk.batch.file.'+n:'batch'for n in (
 'BackupRetentionRejectionTest','BackupArtifactVerifierTest','BackupManifestReaderTest',
 'BackupManifestPublisherTest','BackupManifestCodecTest','MorningBackupRetentionTest','BackupRetentionBoundaryTest')},
 'dev.codex.schubert.nk.batch.backup.BackupCommitServiceTest':'batch'}
PROJECTS=','.join('src/schubert-nk-'+m for m in ('storage','bootstrap','batch'))
METHODS={
 'dev/codex/schubert/nk/batch/file/BackupManifestReader':('retentionNames','retentionRoot','retentionDirectory'),
 'dev/codex/schubert/nk/batch/file/BackupArtifactVerifier':('lambda$removeRetained$2','lambda$removeRetained$3')}


def validate_selection():
    if set(MODULES.values())!={'storage','bootstrap','batch'}or len(MODULES)!=10:raise ValueError('exact required reactor/suite scope')
    for name,module in MODULES.items():
        path=ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
        if not path.is_file()or '@Test'not in path.read_text():raise ValueError('actual nonempty physical suite')
        if '<failIfNoTests>true</failIfNoTests>'not in (ROOT/('src/schubert-nk-'+module+'/pom.xml')).read_text():raise ValueError('original strict NoTests unchanged')
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    if trace.verify_candidate(inventory)['source']!=MAIN_SOURCE:raise ValueError('unchanged actual current941 Main/resources first')


def verify_main_bytes(snapshot):
    value=json.loads(FULL.read_bytes());q=value['result']
    if not(type(value['actualExit'])is int and value['actualExit']==0 and q['productionSource']==MAIN_SOURCE
           and q['tests']==3761 and q['mainClasses']==1647 and len(q['allPhysicalMainSha256'])==1647
           and q['allSixFormatBeforeAnyPt']is True and q['staticSixModules']==0 and q['FESFlakyNotRun']==0):raise ValueError('actual original sameMain full qualification')
    modules=set(MODULES.values());expected={k:v for k,v in q['allPhysicalMainSha256'].items()if k.split(':',1)[0]in modules}
    actual={m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix():base.sha(p)
            for m in modules for p in(snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    if actual!=expected:raise ValueError('all selected module Main byte/inventory must equal deployed04bb')
    return {'productionSource':MAIN_SOURCE,'selectedPhysicalMain':len(actual),'classByteMismatch':0,'testSourceIsSeparate':True}


def source():
    raw=inspect.getsource(base.main)
    raw=raw.replace("module = 'batch' if '.batch.' in name else 'bootstrap'","module = MODULES[name]")
    raw=raw.replace("'-pl', 'src/schubert-nk-batch'","'-pl', "+repr(PROJECTS))
    raw=raw.replace("str(TOOLCHAIN / 'postgresql18/usr')",repr('/home/mini/codex/project1/work/characterization-tools/root/usr'))
    raw=raw.replace("'org.jacoco:jacoco-maven-plugin:0.8.15:report']","'org.jacoco:jacoco-maven-plugin:0.8.15:report','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']")
    raw=raw.replace("'sourceRole': 'unaccepted candidate; deployed source remains7bb'","'sourceRole': 'test-only selection; signedProduction04bb unchanged', 'productionSource': MAIN_SOURCE, 'testSourceSnapshot': head")
    marker="            if report.findall('.//failure') or report.findall('.//error') or report.findall('.//skipped'): reasons.append('non-success case')"
    if raw.count(marker)!=1:raise ValueError('one strict original case-result boundary')
    raw=raw.replace(marker,marker+"\n            if any(report.findall('.//'+tag)for tag in ('flakyFailure','flakyError','rerunFailure','rerunError')):reasons.append('flaky/rerun cannot be accepted')")
    marker="    (WORK / 'begin.safe.json').write_text(json.dumps(begin, sort_keys=True))"
    extra="""
    format_command=command[:command.index('-Dtest='+','.join(TESTS))]+['spotless:check']
    with(WORK/'format.private.log').open('xb')as log:
        fmt=subprocess.run(format_command,cwd=snapshot,env=env,stdout=log,stderr=log);log.flush();os.fsync(log.fileno())
    (WORK/'format.safe.json').write_text(json.dumps({'actualExit':fmt.returncode,'command':format_command,'logSha256':sha(WORK/'format.private.log')}))
    if fmt.returncode:
        (WORK/'manifest.safe.json').write_text(json.dumps({'actualExit':1,'actualMavenExit':None,'formatExit':fmt.returncode,'ptNotRun':True,'sourceSnapshot':head,'productionSource':MAIN_SOURCE}))
        return 1
"""
    if raw.count(marker)!=1:raise ValueError('one format-before-PT boundary')
    raw=raw.replace(marker,marker+extra)
    marker="    if actual != expected: reasons.append('selected identity inventory differs')"
    extra="""
    method_counters={}
    cov=snapshot/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
    if not cov.is_file():reasons.append('actual Backup coverage missing, never accepted')
    else:
        tree=ET.parse(cov).getroot()
        for class_name,names in METHODS.items():
            for name in names:
                matches=[m for c in tree.findall('package/class')if c.get('name')==class_name for m in c.findall('method')if m.get('name')==name]
                if len(matches)!=1:reasons.append('one actual retained method required: '+name);continue
                count={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in matches[0].findall('counter')}
                method_counters[class_name+'.'+name]=count
                if not {'LINE','METHOD','BRANCH'}<=set(count)or any(count[k]['missed']for k in ('LINE','METHOD','BRANCH')):reasons.append('target retained method conditions incomplete: '+name)
    static={}
    for module in sorted(set(MODULES.values())):
        path=snapshot/('src/schubert-nk-'+module+'/target/spotbugsXml.xml')
        if not path.is_file():reasons.append('fresh static XML missing: '+module);continue
        issues=len(ET.parse(path).getroot().findall('.//BugInstance'));static[module]=issues
        if issues:reasons.append('static issue: '+module)
    main_bytes=None
    if code==0:
        try:main_bytes=verify_main_bytes(snapshot)
        except ValueError as mismatch:reasons.append(str(mismatch))
    counters={'targetMethods':method_counters,'freshStaticModules':static,'sameMain':main_bytes,'formatExit':fmt.returncode}
"""
    if raw.count(marker)!=1:raise ValueError('one post actual-XML qualification boundary')
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'sourceSnapshot': head, 'startUTC': began, 'endUTC':", "'sourceSnapshot': head, 'testSourceSnapshot': head, 'productionSource': MAIN_SOURCE, 'startUTC': began, 'endUTC':")
    return raw


def main():
    validate_selection()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed test-only snapshot')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(base),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES,'MAIN_SOURCE':MAIN_SOURCE,'METHODS':METHODS,'verify_main_bytes':verify_main_bytes}
    exec(compile(source(),'<exact Backup retained conditions and same physical Main>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
