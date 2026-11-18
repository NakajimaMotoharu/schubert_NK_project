"""Validate all original JDBC port tests plus cross-thread recovery, raw counters and public ABI."""
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
import gzip
import json
import re
import runpy
import subprocess

HERE=Path(__file__)
P=runpy.run_path(str(HERE.with_name('5236_p00405_service_db_state_lock_checks.py')))
B,R,E=P['B'],P['R'],P['E']
load,save,ref,git=P['read'],P['save'],P['ref'],P['git']
STATE=B['MAIN_LEAF']
ADMIT=STATE.replace('Source','Admission')
OUT=E/'PG39868-p00405-service-db-state-lock-independent-v1'


def results(path):
    root=ET.parse(path).getroot()
    cases=root.findall('testcase')
    assert not any(c.find(key) is not None for c in cases for key in ('failure','error','skipped'))
    keys={(c.get('classname'),c.get('name')) for c in cases}
    assert len(keys)==len(cases)
    return keys


def compare_contract(build,start):
    base=start['values']['productionCoreMain']
    original=git('show',f'{base}:{B["MAIN"]}').decode()
    fixed=git('show',f'{build["sourceCore"]}:{B["MAIN"]}').decode()
    anchor='    if (closed) throw unavailable();'
    lock='    stateLock.unlock();'
    assert original.count(lock.strip())==2 and fixed.count(lock.strip())==1
    assert original.count('stateLock.lock();')==2 and fixed.count('stateLock.lock();')==1
    part=original[original.index('  public Connection getConnection() throws SQLException'):original.index('  private static void discard')]
    a=part.index('  '+anchor)
    b=part.rindex('    } finally {')
    unchanged='\n'.join(line[2:] if line.startswith('  ') else line for line in part[a:b].split('\n'))
    connect=fixed.split('  private Connection connectWhileLocked() throws SQLException {\n',1)[1].split(
        '\n  }\n\n  @FunctionalInterface',1)[0]
    assert unchanged.strip()==connect.strip()
    original_close=original.split('  public void close() {\n',1)[1].split('\n  @Override',1)[0]
    current_close=fixed.split('  public void close() {\n',1)[1].split('\n  @Override',1)[0]
    erase=re.compile(r"if \(!closed\) \{\s*Arrays\.fill\(password, '\\0'\);\s*closed = true;\s*}")
    assert erase.search(original_close) and erase.search(current_close)
    assert original.split('  private static void discard',1)[1].split('  public void close()',1)[0]==fixed.split(
        '  private static void discard',1)[1].split('  public void close()',1)[0]
    assert 'finally {\n      stateLock.unlock();\n    }' in fixed
    assert fixed.count('underStateLock(')==3
    return dict(actualLockAcquisitionsBefore=2,actualLockAcquisitionsAfter=1,
                connectionBodyExact=True,sameCredentialWipeAndClosedOrder=True,sameOtherMethods=True,
                throwAndUnlockSameFinally=True,main=ref(Path(B['MAIN'])))


def public_abi(build,start):
    old=load(Path(start['values']['oracleReferences'][1]['path']))
    paths=[Path(m['cwd'])/'src/schubert-nk-bootstrap/target/classes'/(STATE+'.class') for m in (old,build)]
    assert all(ref(p)['sha256']==m['physicalClassHashes']['bootstrap'][STATE+'.class']
        for m,p in zip((old,build),paths,strict=True))
    javap=P['JDK']/'javap'
    left,right=[subprocess.check_output([str(javap),'-public','-s',str(p)],timeout=10) for p in paths]
    assert left==right
    return dict(previous=ref(paths[0]),current=ref(paths[1]),abiEqual=True,publicAbiSha256=R['shaBytes'](left)) if 'shaBytes' in R else dict(previous=ref(paths[0]),current=ref(paths[1]),abiEqual=True)


def raw(unit,build,slot):
    context=load(next(E.glob('PG38642*/begin.json')))
    assert ref(Path(context['tool']['path']))==context['tool']
    m=load(next(E.glob('PG38642*/manifest.json')))
    assert m['optionalNonLineOutputByteExact'] and m['actualExit']==0
    prefix=m['optionalCommand'][:5]
    assert prefix[-1]=='--line-deficits'
    cli=load(next(E.glob('PG39476*/manifest.json')))
    prior=cli['rawClasses']
    roots={name:Path(build['cwd'])/f'src/schubert-nk-{name}/target/classes' for name in ('bootstrap','storage')}
    names=set(prior)|{STATE+'$StateAction'}
    paths=[roots['bootstrap' if '/api/bootstrap/' in n else 'storage']/(n+'.class') for n in sorted(names)]
    for path in paths:
        mod='bootstrap' if path.is_relative_to(roots['bootstrap']) else 'storage'
        key=str(path.relative_to(roots[mod]))
        assert ref(path)['sha256']==build['physicalClassHashes'][mod][key]
    command=[*prefix,str(slot/'jacoco.exec'),*map(str,paths)]
    result=subprocess.run(command,capture_output=True,timeout=90)
    assert result.returncode==0 and not result.stderr
    measures={}
    deficits=[]
    for line in result.stdout.decode().splitlines():
        bits=line.split('\t')
        if bits[0]=='CLASS':
            measures[bits[1]]=dict(crc=bits[2],positive=bits[3]=='true',
                counters={k:dict(missed=int(mis),covered=int(hit)) for k,mis,hit in (a.split(':') for a in bits[6:])})
        elif bits[0]=='DEFICIT':
            deficits.append(bits[1:])
    assert set(measures)==names and len(names)==9
    ex=gzip.decompress((slot/'execinfo.stdout.gz').read_bytes()).decode()
    assert ex.count('Session "')==1 and unit['run'] in ex
    probes={name:cid for cid,hit,_,name in re.findall(r'^([a-f0-9]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M) if int(hit)}
    assert all(probes[name]==record['crc'] for name,record in measures.items() if record['positive'])
    for cls in (STATE,ADMIT):
        assert measures[cls]['positive']
        assert all(c['missed']==0 for c in measures[cls]['counters'].values())
    no_code=measures[STATE+'$StateAction']
    assert not no_code['positive'] and all(c['missed']==c['covered']==0 for c in no_code['counters'].values())
    return command,result.stdout,measures,deficits


def main():
    start=load(B['START'])
    build=load(P['BUILD'])
    slot=P['UNIT']
    unit=load(slot/'manifest.json')
    assert unit['source']==build['sourceCore'] and unit['unitSource']==git('rev-parse','HEAD').decode().strip()
    assert unit['actualExits']==dict(unit=0,execinfo=0)
    assert all(ref(slot/p)['sha256']==pin for p,pin in unit['files'].items())
    assert not re.search(rb"Initializing '(?:org/postgresql/|com/zaxxer/|dev/codex/schubert/nk/.+(?:RootFailed|Linux|FingerprintKeyRing|TemporaryInfrastructureException|ResponseSnapshotCodec|WebStartupException))",
              gzip.decompress((slot/'class-init.log.gz').read_bytes()))
    xml=slot/'xml/TEST-junit-jupiter.xml'
    orig=next(E.glob('PG39464*/TEST-junit-jupiter.xml'))
    first=results(orig)
    current=results(xml)
    assert len(first)==31 and current==first|{(P['PKG']+P['SUITES'][1],P['CASE'])}
    static=load(Path(unit['originalStatic']['path']))
    assert ref(Path(unit['originalStatic']['path']))==unit['originalStatic']
    assert static['operatorExit']==0 and len(static['perSite'])==25
    assert static['mainAndPeerSpotbugsExactReused']
    contract=compare_contract(build,start)
    abi=public_abi(build,start)
    argv,detail,measurements,deficits=raw(unit,build,slot)
    OUT.mkdir()
    raw_path=OUT/'raw.tsv'
    raw_path.write_bytes(detail)
    value=dict(actualExit=0,source=build['sourceCore'],unitSource=unit['unitSource'],run=unit['run'],
        tests=32,oldTests=31,newTests=1,firstSuccess=32,failures=0,errors=0,skipped=0,notRun=0,
        unit=ref(slot/'manifest.json'),sourceContract=contract,abi=abi,raw=ref(raw_path),rawCommand=argv,
        actualWholeCases=ref(xml),originalWholeCases=ref(orig),singleExec=ref(slot/'jacoco.exec'),
        classes=measurements,unfilteredDeficits=deficits,
        targetBinaries=2,otherMeasuresNotTreatedAsPass=True,commentsOrControlFlowExclusions=0,
        currentFourModuleBuild=ref(P['BUILD']),bootstrapSpotBugsCurrentPhysical201=True,
        scopeStaticRaw=25,applicableOrUnclassified=0,noOldExecUnion=True,noRealJdbcOrServiceOperations=True,
        newAcceptance=0,whole451Accepted=False,verifier=ref(HERE),terminalAtUTC=R['utc']())
    save(OUT/'manifest.json',value)
    print(ref(OUT/'manifest.json'),measurements[STATE],measurements[ADMIT])


if __name__=='__main__':
    main()
