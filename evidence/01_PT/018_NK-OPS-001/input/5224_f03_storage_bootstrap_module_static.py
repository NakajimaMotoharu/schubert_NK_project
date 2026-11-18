"""Run unchanged project analyzers over complete Storage and Bootstrap Main inputs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import os
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET

HERE = Path(__file__)
G = runpy.run_path(str(HERE.with_name('5189_wbs66_four_module_delta_handoff.py')))
E, H = G['E'], G['D']
load, ref, sha, save = G['load'], G['ref'], G['sha'], G['write']
ROOT = Path.cwd()
TOOL = ROOT.parent/'toolchain'
JAVA = TOOL/'jdk-25.0.4/bin/java'
MODULES = ('storage','bootstrap')
PEERS = ('protocol',*MODULES)
FORBIDDEN = {'RootFailedStartRecovery','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest',
             'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}


def utc():
    return datetime.now(timezone.utc).isoformat()


def verify_build(build):
    workspace = Path(build['cwd'])
    assert build['actualExit']==build['productTestsExecuted']==0 and build['inputHashesReverified']
    assert workspace.parent==ROOT.parent/'pgpt-runs/PG379'
    assert ref(JAVA)['sha256']==build['tools']['javaSha256']
    sources={p:h for p,h in build['sourceInputs'].items() if p.endswith('.java') and
             any(p.startswith(f'src/schubert-nk-{m}/src/main/java/') for m in MODULES)}
    assert len(sources)==113 and all(Path(p).stem not in FORBIDDEN for p in sources)
    targets={m:workspace/f'src/schubert-nk-{m}/target/classes' for m in PEERS}
    for mod, folder in targets.items():
        pins=build['physicalClassHashes'][mod]
        actual={str(p.relative_to(folder)):p for p in folder.rglob('*.class')}
        assert actual.keys()==pins.keys() and all(p.stem.split('$')[0] not in FORBIDDEN for p in actual.values())
        assert all(not p.is_symlink() and ref(p)['sha256']==pins[k] for k,p in actual.items())
    poms={p:h for p,h in build['sourceInputs'].items() if p=='pom.xml' or
          any(p==f'src/schubert-nk-{m}/pom.xml' for m in PEERS)}
    for name, expected in (sources|poms).items():
        assert sha(G['git']('show',f'{build["sourceCore"]}:{name}'))==expected
        assert ref(workspace/name)['sha256']==expected
    assert len(poms)==4
    root_pom=(workspace/'pom.xml').read_text()
    assert '<arg>-Werror</arg>' in root_pom and '-Xep:NullAway:ERROR' in root_pom
    return workspace,sources,targets,poms


def sdk_paths(qualification):
    pin=next(p for p in qualification['evidence'] if p['path'].endswith('/external-origins.json'))
    origins=G['revalidate_reference'](pin)
    assert len(origins['classOrigins'])==53
    pins={item['archive']['path']:item['archive']['sha256'] for item in origins['classOrigins'].values()}
    assert all(Path(p).is_relative_to(TOOL/'m2/repository') and ref(Path(p))['sha256']==h for p,h in pins.items())
    return pins


def run(label, command, out, workspace):
    begin=utc()
    env={'JAVA_HOME':str(JAVA.parents[1]),'PATH':f'{JAVA.parent}:/usr/bin:/bin',
         'HOME':os.environ['HOME'],'LANG':'C.UTF-8'}
    try:
        result=subprocess.run(command,cwd=workspace,env=env,capture_output=True,timeout=180)
        code,stdout,stderr=result.returncode,result.stdout,result.stderr
    except subprocess.TimeoutExpired as error:
        code,stdout,stderr=124,error.stdout or b'',error.stderr or b''
    streams={}
    for mode,data in (('stdout',stdout),('stderr',stderr)):
        path=out/(label+'.'+mode+'.gz')
        with path.open('xb') as f:f.write(gzip.compress(data,mtime=0))
        streams[mode]=dict(archive=ref(path),exactSha256=sha(data),size=len(data))
    row=dict(actualExit=code,command=command,startedAtUTC=begin,terminalAtUTC=utc(),**streams)
    save(out/(label+'-exit.json'),row)
    return label,row


def configure(out, workspace, sources, peers, pins, prior):
    listpath=out/'sources.txt'
    listpath.write_text(''.join(f'{workspace/name}\n' for name in sorted(sources)))
    cs=ROOT/'tools/quality/static/checkstyle.xml'
    pmd=ROOT/'tools/quality/static/pmd.xml'
    formatted=TOOL/'google-java-format-1.36.1-all-deps.jar'
    static=TOOL/'static-gates-20261015'
    csjar=static/'checkstyle-14.3.0-all.jar'
    pmd_libs=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    sbc=prior['stages']['bootstrap-spotbugs']['command']
    assert sbc[0]==str(JAVA) and sbc[2]=='-cp'
    sb_libs=[Path(path) for path in sbc[3].split(':')]
    aux=[str(p) for p in peers.values()]+sorted(pins)
    sbaux=out/'spotbugs-aux.txt'
    sbaux.write_text(''.join(p+'\n' for p in aux))
    reports={name:out/(name+'.xml') for name in ('pmd','checkstyle','spotbugs')}
    commands={
        'pmd':[str(JAVA),'-cp',':'.join(map(str,pmd_libs)),'net.sourceforge.pmd.cli.PmdCli',
               'check','--file-list',str(listpath),'--rulesets',str(pmd),'--use-version','java-25',
               '--aux-classpath',':'.join([str(JAVA.parents[1]/'lib/jrt-fs.jar'),*aux]),
               '--no-cache','--format','xml','--report-file',str(reports['pmd'])],
        'checkstyle':[str(JAVA),'-jar',str(csjar),'-c',str(cs),'-f','xml','-o',str(reports['checkstyle']),'@'+str(listpath)],
        'formatter':[str(JAVA),'-jar',str(formatted),'--skip-reflowing-long-strings',
                     '--dry-run','--set-exit-if-changed',*(str(workspace/name) for name in sorted(sources))],
        'spotbugs':[str(JAVA),'-Xmx2g','-cp',':'.join(map(str,sb_libs)),'edu.umd.cs.findbugs.FindBugs2',
                    '-effort:max','-low','-xml:withMessages','-exitcode','-auxclasspathFromFile',
                    str(sbaux),'-output',str(reports['spotbugs']),*(str(peers[m]) for m in MODULES)],
    }
    files=[cs,pmd,formatted,csjar,*pmd_libs,*sb_libs]
    return reports,commands,[ref(p) for p in dict.fromkeys(files)]


def parse_report(label, report, workspace, sources, physical):
    if not report.exists():
        return dict(reportMissing=True)
    root=ET.parse(report).getroot()
    if label=='spotbugs':
        observed={x.get('class').replace('.','/')+'.class' for x in root.findall('.//ClassStats')}
        return dict(raw=ref(report),physical=len(observed),exactPhysical=observed==physical,
                    findings=len(root.findall('BugInstance')),errors=len(root.findall('.//Error')),
                    missingClasses=len(root.findall('.//MissingClass')))
    namespace=root.tag.partition('}')[0]+'}' if root.tag.startswith('{') else ''
    files=root.findall(namespace+'file')
    names={str(Path(x.get('name')).relative_to(workspace)) for x in files}
    item='error' if label=='checkstyle' else 'violation'
    findings=sum(len(f.findall(namespace+item)) for f in files)
    errors=sum(len(root.findall(namespace+kind)) for kind in ('error','configerror'))
    return dict(raw=ref(report),filesWithReportRows=len(names),allReportPathsInInput=names<=sources.keys(),
                hasAllInputRows=names==sources.keys(),findings=findings,processingErrors=errors)


def main():
    start=load(next(H.glob('504_*')))
    v=start['values']
    assert G['git']('rev-parse','HEAD').decode().strip()==v['source']
    build,edge,sdk,older,raw_history,prior=map(G['revalidate_reference'],v['oracleReferences'])
    assert build['sourceCore']==v['productionCoreMain']==edge['source']
    assert older['actualExit']==0 and raw_history['sourceCore']!=build['sourceCore']
    assert ref(ROOT/'tools/quality/static/pmd.xml')['sha256']==raw_history['originalFullRulesetSha256']
    workspace,sources,peers,poms=verify_build(build)
    pins=sdk_paths(sdk)
    out=(E/v['run']).resolve()
    reports,cmds,tools=configure(out,workspace,sources,peers,pins,prior)
    physical=set().union(*(build['physicalClassHashes'][m].keys() for m in MODULES))
    assert len(physical)==279
    save(out/'begin.json',dict(event=start['eventId'],scope=MODULES,source=build['sourceCore'],inputs=sources,
                              rootAndPeerPoms=poms,exactCommands=cmds,toolAndRulePins=tools,sdkJars=pins,
                              actualCwd=str(workspace),startedAtUTC=utc()))
    with ThreadPoolExecutor(max_workers=3) as pool:
        plan=[pool.submit(run,label,cmd,out,workspace) for label,cmd in cmds.items()]
        stages=dict(job.result() for job in plan)
    parsed={name:parse_report(name,p,workspace,sources,physical) for name,p in reports.items()}
    verify_build(build)
    result=dict(actualProcessExits={k:v['actualExit'] for k,v in stages.items()},source=build['sourceCore'],
                scope=MODULES,staticMainCount=113,staticPhysicalCount=279,
                executedProcesses=len(stages),reports=parsed,compile=v['oracleReferences'][0],
                werrorNullAwayBuildReused=True,productTests=0,runtimeActions=0,suppressionsAdded=0,
                completeSixModule=False,whole451Accepted=False,newAcceptance=0,
                terminalAtUTC=utc(),verifier=ref(HERE))
    save(out/'manifest.json',result)
    print(result['actualProcessExits'],parsed)


if __name__=='__main__':
    main()
