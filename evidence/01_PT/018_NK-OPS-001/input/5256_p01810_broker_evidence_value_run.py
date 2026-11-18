"""Run the three detached evidence-value tests from exact current compiled product bytes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import gzip
import platform
import re
import runpy
from xml.etree import ElementTree as ET

HERE=Path(__file__).resolve()
M=runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
SC=runpy.run_path(str(HERE.with_name('5224_f03_storage_bootstrap_module_static.py')))
E,D,ROOT,TC,JDK=(M[n] for n in ('E','D','ROOT','TC','JDK'))
git,ref,read,save,step=(M[n] for n in ('git','ref','read','save','step'))
FIRST=E/'PG40006-p01810-broker-evidence-value-v1'
OUT=E/'PG40008-p01810-broker-evidence-value-v2'
MOD=Path('src/schubert-nk-batch')
PKG=Path('dev/codex/schubert/nk/batch/mq')
TEST=MOD/'src/test/java'/PKG/'ArtemisStartupEvidenceValueTest.java'
TYPE='dev.codex.schubert.nk.batch.mq.ArtemisStartupEvidenceValueTest'
ROLE='ArtemisStartupObservation'
VALUE=ROLE+'$Evidence'
PHYSICAL=(ROLE,VALUE,'ArtemisQueuePressureClient','ArtemisQueuePressureClient$Pressure','ArtemisQueuePressureClient$Value')
METHODS={'ownsAllNestedValueInputsBeforeAndAfterCallerMutatesThem',
         'comparesOwnedValueDataWhileItsGeneralDiagnosticsStayFixed',
         'rejectsMissingNestedInputsWhileTakingOwnership'}


def prepare():
    start=next(D.glob('553_*'))
    v=read(start)['values']
    assert v['run']==FIRST.name and read(FIRST/'manifest.json')['stages']['testcompile']['actualExit']==1
    pins=v['oracleReferences']
    assert all(ref(Path(p['path']))==p for p in pins)
    catalog,build,static,prior=(read(p['path']) for p in pins)
    catalog_row,=[x for x in catalog if x['plannedCaseId']=='PT-P01810-CATALOG-062']
    core=build['sourceCore']
    assert core==static['source']==v['productionCoreMain']
    source=git('rev-parse','HEAD').decode().strip()
    assert git('diff','--name-only',v['source'],source,'--','src').decode().splitlines()==[str(TEST)]
    assert not git('diff','--name-only','HEAD','--','src')
    work=ROOT.parent/'pgpt-runs/PG379'/OUT.name.lower()
    assert not work.exists() and not OUT.exists()
    work.mkdir(mode=0o700)
    OUT.mkdir()
    product=work/'product'
    for owner in (ROLE,'ArtemisQueuePressureClient'):
        loc=MOD/'src/main/java'/PKG/(owner+'.java')
        assert M['sha'](Path(build['cwd'])/loc)==build['sourceInputs'][str(loc)]
        assert git('show',f'{core}:{loc}')==git('show',f'{source}:{loc}')
    product_files={}
    for name in PHYSICAL:
        member=str(PKG/(name+'.class'))
        origin=Path(build['cwd'])/MOD/'target/classes'/member
        record=ref(origin)
        assert record['sha256']==build['physicalClassHashes']['batch'][member]
        dest=product/member
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(origin.read_bytes())
        assert ref(dest)['sha256']==record['sha256']
        product_files[member]=record
    sdk={name:Path(row['path']) for name,row in prior['tools'].items() if name in (
        'junit-platform-console-standalone-1.13.4.jar','org.jacoco.cli-0.8.15-nodeps.jar',
        'org.jacoco.agent-0.8.15-runtime.jar','jspecify-1.0.1.jar')}
    assert len(sdk)==4 and all(ref(p)==prior['tools'][n] for n,p in sdk.items())
    assert ref(JDK/'java')==prior['jdk'] and ref(JDK/'javac')==prior['javaC']
    test=work/TEST
    test.parent.mkdir(parents=True)
    test.write_bytes(git('show',f'{source}:{TEST}'))
    save(OUT/'begin.json',dict(sourceCore=core,testSource=source,testInput=ref(test),knownCompile=pins[1],
         productFiles=product_files,tools={k:ref(p) for k,p in sdk.items()},
         catalog=dict(id=catalog_row['plannedCaseId'],owner=catalog_row['owners'],expect=catalog_row['independentExpected']),
         firstFixtureCompile=ref(FIRST/'manifest.json'),noArtemisSdk=True,hostServicesTouched=0,
         startedAtUTC=M['utc'](),platform=platform.platform()))
    return core,source,work,test,product,sdk,static


def execute(work,test,product,sdk,static):
    junit=sdk['junit-platform-console-standalone-1.13.4.jar']
    jspecify=sdk['jspecify-1.0.1.jar']
    classes=work/'testclasses'
    temp=work/'tmp'
    xml=OUT/'xml'
    for p in (classes,temp,xml):
        p.mkdir()
    classpath=f'{product}:{junit}:{jspecify}'
    javac=[str(JDK/'javac'),'-Xlint:all','-Werror','--release','25','-cp',classpath,'-d',str(classes),str(test)]
    results={'testcompile':step('testcompile',javac,work,OUT,60)}
    if results['testcompile']['actualExit']!=0:
        return results
    agent=sdk['org.jacoco.agent-0.8.15-runtime.jar']
    cli=sdk['org.jacoco.cli-0.8.15-nodeps.jar']
    exec_path=(OUT/'jacoco.exec').resolve()
    session='PG40006-DETACHED-BROKER-VALUE'
    init=work/'class-init.log'
    unit=[str(JDK/'java'),'-Djava.io.tmpdir='+str(temp),'-Xlog:class+init=info:file='+str(init),
          f'-javaagent:{agent}=destfile={exec_path},sessionid={session},append=false',
          '-jar',str(junit),'execute','--disable-banner','--disable-ansi-colors','--fail-if-no-tests',
          '--details=summary','--class-path',f'{classes}:{product}:{jspecify}',
          '--select-class',TYPE,'--reports-dir',str(xml.resolve()),'--config=junit.jupiter.execution.parallel.enabled=false']
    results['unit']=step('unit',unit,work,OUT,60)
    if results['unit']['actualExit']!=0:
        return results
    target=product/PKG/(VALUE+'.class')
    results['execinfo']=step('execinfo',[str(JDK/'java'),'-jar',str(cli),'execinfo',str(exec_path)],work,OUT)
    results['classinfo']=step('classinfo',[str(JDK/'java'),'-jar',str(cli),'classinfo',str(target)],work,OUT)
    static_archive=SC['TOOL']/'static-gates-20261015'
    listing=(OUT/'sources.txt').resolve()
    listing.write_text(str(test)+'\n')
    pmd=list(static['command'])
    for flag,val in (('--file-list',str(listing)),('--report-file',str((OUT/'pmd.xml').resolve())),
                     ('--aux-classpath',f'{JDK.parent}/lib/jrt-fs.jar:{classpath}')):
        pmd[pmd.index(flag)+1]=val
    commands=(
        ('pmd',pmd),
        ('checkstyle',[str(JDK/'java'),'-jar',str(static_archive/'checkstyle-14.3.0-all.jar'),
                       '-c',str(ROOT/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str((OUT/'checkstyle.xml').resolve()),
                       '@'+str(listing)]),
        ('format',[str(JDK/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),
                   '--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(test)]))
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks=[pool.submit(SC['run'],label,command,OUT,work) for label,command in commands]
        results.update(f.result() for f in tasks)
    return results


def post(core,source,work,test,product,results):
    begin=read(OUT/'begin.json')
    statuses={k:v['actualExit'] for k,v in results.items()}
    report=dict(actualExit=1,sourceCore=core,testSource=source,stages=results,passed=0,newAcceptance=0,
                whole451Accepted=False,nativeOrExternalOperations=0,verifier=ref(HERE))
    if statuses.get('pmd') in (0,4) and statuses==dict(testcompile=0,unit=0,execinfo=0,classinfo=0,
                                                      pmd=statuses['pmd'],checkstyle=0,format=0):
        reportxml=OUT/'xml/TEST-junit-jupiter.xml'
        xml=ET.parse(reportxml)
        assert {node.get('name') for node in xml.iter('testcase')}=={name+'()' for name in METHODS}
        assert all(node.get('classname')==TYPE for node in xml.iter('testcase'))
        assert not any(node.tag in ('failure','error','skipped') for node in xml.iter())
        init=work/'class-init.log'
        init_bytes=init.read_bytes()
        assert b"Initializing 'dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation$Evidence'" in init_bytes
        assert not re.search(rb"Initializing '(?:org/apache/activemq/|dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation'|org/postgresql/)",init_bytes)
        init_archive=OUT/'class-init.log.gz'
        init_archive.write_bytes(gzip.compress(init_bytes,mtime=0))
        target=product/PKG/(VALUE+'.class')
        # The exact previously authenticated unfiltered report command uses this same tool and JVM.
        previous=read(E/'PG39994-p020-search-empty-independent-v1'/'manifest.json')['raw']
        command=[*previous['command'][:5], str((OUT/'jacoco.exec').resolve()), str(target)]
        assert command[4]=='--line-deficits'
        raw=step('raw',command,ROOT,OUT,60)
        assert raw['actualExit']==0
        log=Path(raw['log']['path'])
        raw_records=log.read_text().splitlines()
        row,=[x.split('\t') for x in raw_records if x.startswith('CLASS\t')]
        assert row[1]==str(PKG/VALUE) and row[3]=='true' and not any(
            v.startswith(('METHOD_MISS','LINE_MISS')) for v in raw_records)
        counters={name:dict(missed=int(miss),covered=int(hit)) for name,miss,hit in
                  (token.split(':') for token in row[6:])}
        assert all(c['missed']==0 for c in counters.values())
        exec_text=(OUT/'execinfo.log').read_text()
        class_text=(OUT/'classinfo.log').read_text()
        assert exec_text.count('Session "')==1 and 'PG40006-DETACHED-BROKER-VALUE' in exec_text and row[2].lower() in exec_text.lower()
        assert row[2].lower() in class_text.lower()
        notes={}
        raw_pmd=[]
        for kind,tag in (('pmd','violation'),('checkstyle','error')):
            tree=ET.parse(OUT/(kind+'.xml'))
            if kind=='pmd':
                assert not tree.findall('.//{*}error') and not tree.findall('.//{*}configerror')
                raw_pmd=[dict(rule=v.get('rule'),line=int(v.get('beginline')),message=(v.text or '').strip())
                         for v in tree.findall('.//{*}'+tag)]
            else:
                assert not tree.findall('.//{*}'+tag)
            notes[kind]=ref(OUT/(kind+'.xml'))
        # Store the exact tool in stdout without treating uncovered helper classes as target results.
        raw_table=OUT/'raw.tsv'
        raw_table.write_bytes(log.read_bytes())
        report.update(actualExit=0,passed=3,failed=0,errors=0,skipped=0,notRun=0,testXml=ref(reportxml),classInit=ref(init_archive),
                      rawReceipt=raw,raw=ref(raw_table),counters=counters,sourceToPhysical=begin['productFiles'],
                      staticReports=notes,rawPmd=raw_pmd,newTestDefinitions=3,
                      target=str(PKG/VALUE),session='PG40006-DETACHED-BROKER-VALUE')
    report.update(terminalAtUTC=datetime.now(timezone.utc).isoformat())
    save(OUT/'manifest.json',report)
    print(statuses,report['actualExit'],report.get('counters'))
    return report['actualExit']


if __name__=='__main__':
    c,s,w,t,p,k,a=prepare()
    raise SystemExit(post(c,s,w,t,p,execute(w,t,p,k,a)))
