"""Apply the established tool rules to changed definitions and whole executable tool bytecode."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import runpy

HERE=Path(__file__)
R=runpy.run_path(str(HERE.with_name('5227_p020_definition_uniqueness_run.py')))
Q=runpy.run_path(str(HERE.with_name('5224_f03_storage_bootstrap_module_static.py')))
ROOT,TC,JDK,E,B=map(R.get,('ROOT','TC','JDK','E','B'))
read,save,ref=R['read'],R['save'],R['ref']


def main():
    unit_path=E/'PG39830-p020-definition-green144-v3/manifest.json'
    unit=read(unit_path)
    assert unit['expected']==144 and unit['stages']['main']['actualExit']==0
    assert unit['stages']['test']['actualExit']==unit['stages']['unit']['actualExit']==0
    assert unit['source']==R['git']('rev-parse','HEAD').decode().strip()
    begin=read(unit_path.with_name('begin.json'))
    snapshot=Path(begin['snapshot'])
    classes=Path(unit['classesDir'])
    assert R['physical'](classes)==unit['mainPhysical']
    assert len(unit['mainPhysical'])==17
    raw_pmd=next(E.glob('PG36960*/manifest.json'))
    rules=ROOT/'tools/quality/static'
    assert ref(rules/'pmd.xml')['sha256']==read(raw_pmd)['originalFullRulesetSha256']
    tools=TC/'static-gates-20261015'
    paths=sorted(str(snapshot/path) for path in R['PHASE_CHANGES']['qualified'])
    for path in R['PHASE_CHANGES']['qualified']:
        assert ref(snapshot/path)['sha256']==unit['inputHashes'][str(path)]==ref(path)['sha256']
    out=(E/'PG39832-p020-definition-static-v1').resolve()
    out.mkdir()
    listing=out/'sources.txt'
    listing.write_text(''.join(path+'\n' for path in paths))
    mv=[str(R['MAVEN']),'-o','-B','-ntp','-N',f'-Dmaven.repo.local={TC}/m2/repository']
    sb=[*mv,'-f',str(snapshot/B/'pom.xml'),'-Dmaven.test.skip=true','-Dspotbugs.effort=Max',
        '-Dspotbugs.threshold=Low','-Dspotbugs.failOnError=true','-Dspotbugs.xmlOutput=true',
        'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']
    cp=[str(classes),str(JDK.parent/'lib/jrt-fs.jar'),
        *[pin['path'] for name,pin in begin['tools'].items() if 'jacoco' not in name]]
    libs=[tools/'record-fix-v1/pmd-record-1298.jar',*sorted((tools/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    csjar=tools/'checkstyle-14.3.0-all.jar'
    formatter=TC/'google-java-format-1.36.1-all-deps.jar'
    java=str(JDK/'java')
    cmds={
        'spotbugs':sb,
        'format':[java,'-jar',str(formatter),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*paths],
        'checkstyle':[java,'-jar',str(csjar),'-c',str(rules/'checkstyle.xml'),'-f','xml',
                      '-o',str(out/'checkstyle.xml'),'@'+str(listing)],
        'pmd':[java,'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check',
               '--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25',
               '--aux-classpath',':'.join(cp),'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')],
    }
    save(out/'begin.json',dict(source=unit['source'],unit=ref(unit_path),commands=cmds,
        toolAndRulePins=[ref(p) for p in (formatter,csjar,*libs,rules/'pmd.xml',rules/'checkstyle.xml')],
        sourceInputs={p:ref(Path(p))['sha256'] for p in paths},productOrServiceActions=0))
    with ThreadPoolExecutor(max_workers=3) as pool:
        gather=[pool.submit(Q['run'],n,cmd,out,snapshot) for n,cmd in cmds.items()]
        stages=dict(job.result() for job in gather)
    xml=classes.parent/'spotbugsXml.xml'
    local=out/'spotbugs.xml'
    local.write_bytes(xml.read_bytes())
    sources={str(Path(p).relative_to(snapshot)):ref(Path(p))['sha256'] for p in paths}
    physical=set(unit['mainPhysical'])
    result={n:Q['parse_report'](n,out/(n+'.xml'),snapshot,sources,physical)
            for n in ('checkstyle','pmd','spotbugs')}
    assert R['physical'](classes)==unit['mainPhysical']
    save(out/'manifest.json',dict(source=unit['source'],stageExits={k:v['actualExit'] for k,v in stages.items()},
        reports=result,unit=ref(unit_path),terminalAtUTC=R['utc'](),allPhysicalUnchanged=True,
        coverageWaiver=0,productActions=0,whole451Accepted=False,verifier=ref(HERE)))
    print({k:v['actualExit'] for k,v in stages.items()},result)


if __name__=='__main__':
    main()
