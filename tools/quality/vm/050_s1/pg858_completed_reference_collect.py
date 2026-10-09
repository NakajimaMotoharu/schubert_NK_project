"""Independent same frozen source/full run XML, main bytes, static and session qualifier.
Host-only qualification: new native/global100/formal acceptance remains separate.
"""
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from pg831_manager_collect import classes,sha,verify_sessions,MODULES
T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def main():
    os.umask(0o077);run=W/'pg857-completed-reference-six-host-v1'
    assert (run/'exit').read_bytes()==b'0\n'
    source=(run/'source').read_text().strip()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=T)
    log=(run/'build.private.log').read_text();assert log.count('BUILD SUCCESS')==1 and 'BUILD FAILURE' not in log
    entries=[x.split('  ',1)for x in(run/'source-files.sha256').read_text().splitlines()]
    # Every source/tool blob is bound to the recorded Git source, not today's worktree.
    raw=subprocess.check_output(['git','cat-file','--batch'],cwd=T,input=''.join(source+':'+p+'\n'for _,p in entries).encode())
    offset=0
    for expected,path in entries:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();assert len(header)==3 and header[1]==b'blob'
        size=int(header[2]);offset=end+1;assert hashlib.sha256(raw[offset:offset+size]).hexdigest()==expected
        assert raw[offset+size:offset+size+1]==b'\n';offset+=size+1
    assert offset==len(raw)
    start=datetime.datetime.fromisoformat((run/'started').read_text().strip()).timestamp()
    end=datetime.datetime.fromisoformat((run/'completed').read_text().strip()).timestamp()
    selected=W/'pg854-completed-reference-selected-v4';s=json.loads((selected/'run.safe.json').read_bytes())
    # Historical selected run is byte-comparison/diagnostic only. All counted PT, coverage,
    # sessions and static below come exclusively from this new same-source whole run.
    assert s['actualExit']==0 and not s['formalAccepted']
    old=W/'pg830-manager-six-host-v1'
    assert sha(old/'manifest.safe.json')=='85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede'
    results={};tests=suites=total_classes=0;changed=[]
    for module in MODULES:
        base=run/module;current=T/'src'/('schubert-nk-'+module)/'target';jar='schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'
        actual=classes(base/jar);assert actual==classes(current/jar);total_classes+=len(actual)
        reference=classes((selected/'batch' if module=='batch' else old/module)/jar)
        assert actual==reference
        previous=classes(old/module/jar);assert actual.keys()==previous.keys()
        for name,data in actual.items():
            if data!=previous[name]:
                assert module=='batch' and any(name.startswith('dev/codex/schubert/nk/batch/file/'+n)for n in ('MaintenanceRunFiles','MorningNewRunAdmission','MorningResumeAdmission'))
                changed.append(name)
        reports=list((base/'surefire-reports').glob('TEST-*.xml'));assert reports
        sums={k:0 for k in ('tests','failures','errors','skipped')};hashes={}
        for p in reports:
            root=ET.parse(p).getroot();assert root.tag=='testsuite'
            assert not any(x.tag.lower()in ('flakyfailure','flakyerror','rerunfailure','rerunerror')for x in root.iter())
            for k in sums:sums[k]+=int(root.get(k,'0'))
            hashes[p.name]=sha(p)
        assert sum(sums[k]for k in ('failures','errors','skipped'))==0
        bugs=ET.parse(base/'spotbugsXml.xml').getroot();assert not bugs.findall('.//BugInstance') and not bugs.findall('.//Error')
        assert sha(base/'jacoco.xml')==sha(current/'site/jacoco/jacoco.xml')
        root=ET.parse(base/'jacoco.xml').getroot();sessions=[dict(x.attrib)for x in root.findall('sessioninfo')]
        topology=verify_sessions(sessions,start,end,module)
        counts={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in root.findall('counter')}
        results[module]={'tests':sums['tests'],'suites':len(reports),'FESFlakyNotRun':0,'staticIssues':0,'hostCounters':counts,'xmlHashes':hashes,'jarSha256':sha(base/jar),'execSha256':sha(base/'jacoco.exec'),'coverageSha256':sha(base/'jacoco.xml'),'staticSha256':sha(base/'spotbugsXml.xml'),'sessions':sessions,'sessionTopology':topology}
        tests+=sums['tests'];suites+=len(reports)
    assert tests==3541 and suites==522 and total_classes==1632
    missed={k:sum(x['hostCounters'][k]['missed']for x in results.values())for k in ('LINE','METHOD','CLASS','BRANCH')}
    result={'actualExit':0,'run':run.name,'candidateSource':source,'collectorOperator':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'sourceQualification':'FRESH_SIX_HOST_ONLY','tests':tests,'suites':suites,'mainClasses':total_classes,'FESFlakyNotRunIndicators':0,'staticModules':6,'staticIssues':0,'moduleResults':results,'changedClassNames':changed,'selectedManifestSha256':sha(selected/'run.safe.json'),'remainingHostOnly':missed,'elapsedSeconds':end-start,'installedVmSource':'2a0d5aa392c85a1dc12a1cdb423978e8500895b8','candidateNotDeployed':True,'oldNativeStreamsNotImported':True,'global100':all(v==0 for v in missed.values()),'newNativePending':True,'formalAccepted':False,'wholeWbsAccepted':False,'rawExported':False}
    with(run/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps({k:v for k,v in result.items()if k not in ('moduleResults','changedClassNames')}))
if __name__=='__main__':main()
