"""Frozen SSC261 fresh six XML/static/source qualification; native/formal separate."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from pg618_collect_candidate_full import classes

T=Path('/home/mini/codex/project1/work/pgpt-foundation')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
TOPOLOGY={'protocol':(1,1),'storage':(1,1),'bootstrap':(7,6),'api':(7,6),'web':(6,6),'batch':(1,1)}
COUNTERS=('LINE','METHOD','CLASS','BRANCH')


def require(value):
    if not value:raise ValueError('frozen fresh six qualification refused')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def qualify_sessions(rows,start,end,module):
    require(module in TOPOLOGY and type(rows)is list and rows)
    seen={};tuples=set()
    for row in rows:
        require(type(row)is dict and set(row)=={'id','start','dump'}and all(type(v)is str for v in row.values())and 0<len(row['id'])<=128)
        require(all(re.fullmatch('[0-9]{1,19}',row[k])for k in ['start','dump']))
        begin,dump=int(row['start']),int(row['dump']);require(start*1000-1000<=begin<=dump<=end*1000+1000)
        identity=(row['id'],begin,dump);require(identity not in tuples);tuples.add(identity)
        if row['id']in seen:require(seen[row['id']][0]==begin and dump>seen[row['id']][1])
        seen[row['id']]=(begin,dump)
    require((len(rows),len(seen))==TOPOLOGY[module])
    return {'dumpRecords':len(rows),'distinctSessions':len(seen)}


def source_guard(run):
    entries=[line.split('  ',1)for line in (run/'source-files.sha256').read_text().splitlines()]
    raw=subprocess.check_output(['git','cat-file','--batch'],cwd=T,input=''.join(SOURCE+':'+p+'\n'for h,p in entries).encode())
    offset=0
    for expected,path in entries:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();require(len(header)==3 and header[1]==b'blob')
        size=int(header[2]);offset=end+1;require(hashlib.sha256(raw[offset:offset+size]).hexdigest()==expected and raw[offset+size:offset+size+1]==b'\n');offset+=size+1
    require(offset==len(raw))
    return len(entries)


def main():
    os.umask(0o077)
    run=W/'pg1279-held-channel-six-host-v1';require((run/'source').read_text().strip()==SOURCE and(run/'exit').read_bytes()==b'0\n'and not os.path.lexists(run/'manifest.safe.json'))
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=T))
    require(not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=T))
    source_entries=source_guard(run);log=(run/'build.private.log').read_text();require(log.count('BUILD SUCCESS')==1 and 'BUILD FAILURE'not in log)
    start=datetime.datetime.fromisoformat((run/'started').read_text().strip()).timestamp();end=datetime.datetime.fromisoformat((run/'completed').read_text().strip()).timestamp();require(end>start)
    results={};total_classes=tests=suites=0;selected_class_counters={}
    for module in TOPOLOGY:
        base=run/module;current=T/('src/schubert-nk-'+module+'/target');jar='schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'
        actual=classes(base/jar);require(actual and actual==classes(current/jar));total_classes+=len(actual)
        sums={k:0 for k in ['tests','failures','errors','skipped']};hashes={};reports=sorted((base/'surefire-reports').glob('TEST-*.xml'));require(reports)
        for p in reports:
            original=current/'surefire-reports'/p.name;require(sha(p)==sha(original)and start<=original.stat().st_mtime<=end+1)
            root=ET.parse(p).getroot();cases=root.findall('testcase');require(len(cases)==int(root.attrib['tests'])and cases)
            require(all(all(c.find(k)is None for k in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'])for c in cases))
            for k in sums:sums[k]+=int(root.attrib[k])
            hashes[p.name]=sha(p)
        require(sums['failures']==sums['errors']==sums['skipped']==0 and not ET.parse(base/'spotbugsXml.xml').getroot().findall('.//BugInstance'))
        require(sha(base/'jacoco.xml')==sha(current/'site/jacoco/jacoco.xml'))
        root=ET.parse(base/'jacoco.xml').getroot();sessions=[dict(s.attrib)for s in root.findall('sessioninfo')];topology=qualify_sessions(sessions,start,end,module)
        counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in root.findall('counter')}
        results[module]={'tests':sums['tests'],'suites':len(reports),'FESFlakyNotRun':0,'staticIssues':0,'hostCounters':counters,'xmlHashes':hashes,'jarSha256':sha(base/jar),'execSha256':sha(base/'jacoco.exec'),'coverageSha256':sha(base/'jacoco.xml'),'staticSha256':sha(base/'spotbugsXml.xml'),'sessions':sessions,'sessionTopology':topology}
        if module=='bootstrap':
            for c in root.findall('package/class'):
                if c.attrib['name'].rsplit('/',1)[-1]in ['NativeCoveragePrivateFile','NativeCoveragePrivateFile$NativeFileCalls','FixedNativeCoverageStopHold']:
                    selected_class_counters[c.attrib['name']]={n.attrib['type']:{'missed':int(n.attrib['missed']),'covered':int(n.attrib['covered'])}for n in c.findall('counter')}
        tests+=sums['tests'];suites+=len(reports)
    require(tests==3569 and suites==523 and total_classes==1635 and results['bootstrap']['tests']==298)
    remaining={k:sum(r['hostCounters'][k]['missed']for r in results.values())for k in COUNTERS}
    value={'actualExit':0,'run':run.name,'candidateSource':SOURCE,'collectorOperator':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),'sourceQualification':'FRESH_SIX_HOST_ONLY','sourceEntries':source_entries,'tests':tests,'suites':suites,'mainClasses':total_classes,'FESFlakyNotRunIndicators':0,'staticModules':6,'staticIssues':0,'moduleResults':results,'selectedClassCounters':selected_class_counters,'remainingHostOnly':remaining,'oldNativeStreamsNotImported':True,'oldOrSelectedExecAdded':False,'candidateNotDeployed':True,'installedVmSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','global100':all(n==0 for n in remaining.values()),'formalAccepted':False,'wholeWbsAccepted':False,'rawExported':False,'started':(run/'started').read_text().strip(),'completed':(run/'completed').read_text().strip(),'elapsedSeconds':end-start,'logSha256':sha(run/'build.private.log'),'sourceFilesSha256':sha(run/'source-files.sha256')}
    with(run/'manifest.safe.json').open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':tests,'suites':suites,'mainClasses':total_classes,'staticIssues':0,'remainingHostOnly':remaining,'selectedClassCounters':selected_class_counters,'manifestSha256':sha(run/'manifest.safe.json'),'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
