"""Same selected connection byte/XML/static diagnostics. Not full/native/formal acceptance."""
import datetime, hashlib, json, pathlib, subprocess, xml.etree.ElementTree as ET
T = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE = W / 'pg470-checkpoint-selected-v4'
OUT = T / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG470-checkpoint-selected-v4'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists() and BASE.with_suffix('.exit').read_text().strip() == '0'
    start = datetime.datetime.fromisoformat(BASE.with_suffix('.started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat(BASE.with_suffix('.completed').read_text().strip()).timestamp()
    classes = {'protocol':['MessageCodecTest'], 'storage':['ResourceScopeTest','PrivateDirectoryEntryTest'],
               'bootstrap':['FixedServiceIdentityTest','FixedServiceExecArgumentsTest','FixedNativeCoverageProfileTest',
                            'FixedNativeCoverageCheckpointTest','NativeCoveragePrivateFileTest'],
               'api':['ApiProcessMainTest'], 'web':['WebProcessMainTest'], 'batch':['RootServiceLauncherTest']}
    xml = {}; static = {}; counters = {}; count = 0
    for module, names in classes.items():
        target = T / 'src' / ('schubert-nk-' + module) / 'target'
        for name in names:
            matches = list((target/'surefire-reports').glob('TEST-*.'+name+'.xml')); assert len(matches)==1
            path = matches[0]; assert start <= path.stat().st_mtime <= end
            suite = ET.parse(path).getroot()
            assert all(int(suite.get(k,'-1'))==0 for k in ['failures','errors','skipped'])
            assert len(suite.findall('testcase'))==int(suite.get('tests'))
            assert not any(case.find(tag) is not None for case in suite.findall('testcase') for tag in ['failure','error','skipped','flakyFailure','rerunFailure'])
            count += int(suite.get('tests')); xml[name]={'tests':int(suite.get('tests')),'sha256':sha(path)}
        p = target/'spotbugsXml.xml'
        assert start <= p.stat().st_mtime <= end and not ET.parse(p).getroot().findall('BugInstance')
        static[module]=sha(p)
        if module=='bootstrap':
            for clazz in ET.parse(target/'site/jacoco/jacoco.xml').getroot().findall('.//class'):
                if any(clazz.get('name').endswith('/'+n) for n in ['FixedNativeCoverageProfile','FixedNativeCoverageCheckpoint','NativeCoveragePrivateFile']):
                    counters[clazz.get('name')]={c.get('type'):{k:int(c.get(k)) for k in ['missed','covered']} for c in clazz.findall('counter')}
    log = BASE.with_suffix('.log').read_text()
    assert count==72 and len(xml)==11 and '[INFO] BUILD SUCCESS' in log and log.count('BugInstance size is 0')==6
    paths = subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z','src'],cwd=T).decode().split('\0')[:-1]
    hashes = {p:sha(T/p) for p in sorted(set(paths))}
    value={'classification':'PROVISIONAL_SELECTED_NOT_FORMAL','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
           'dirtySource':True,'sourceFiles':len(hashes),'sourceSetSha256':hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),
           'sourceSha256':hashes,'started':BASE.with_suffix('.started').read_text().strip(),'completed':BASE.with_suffix('.completed').read_text().strip(),
           'command':'bash tools/quality/vm/050_s1/pg470_checkpoint_selected_v4.sh','actualExit':0,'PT':count,'suites':len(xml),
           'failed':0,'errors':0,'skipped':0,'xml':xml,'staticModulesZero':6,'staticXmlSha256':static,
           'developmentCumulativeCoverage':counters,'coverage100':False,'formal':False,'fullRegression':False,'nativeConnection':False,
           'privateLogSha256':sha(BASE.with_suffix('.log')),'OS':'Ubuntu26.04','JDK':'25.0.4','Maven':'3.9.12',
           'SSC':['SSC-193'],'BUG':['BUG-752'],'YKT':['YKT-532'],
           'earlierNotAccepted':{'v1':'NullAway generic boundary compile exit1','v2':'static portability3 exit1/API-Web-Batch notrun',
                                 'v3':'API legacy main test checked IO declaration compile exit1/Web-Batch notrun'},
           'rawSecretExported':False,'notAccepted':['same-source native','same-source full','all coverage100','all CHR','all PGPT','ITST']}
    OUT.mkdir(parents=True); (OUT/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'PT':count,'suites':len(xml),'staticZero':6,'developmentCounters':counters,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
if __name__=='__main__': main()
