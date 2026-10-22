"""Finite static checks of the current common four Main, no test/runtime replay."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg6968_chr_adapter_host_v2 as selected


def main(prior=None, slot=None):
    os.umask(0o077)
    slot = slot or host.W/'pg6970-chr-common-static-v1';slot.mkdir()
    prior = prior or host.W/'pg6968-chr-adapter-host-v2'
    receipt = json.loads((prior/'manifest.safe.json').read_bytes())
    begin = json.loads((prior/'begin.safe.json').read_bytes())
    host.require(receipt['actualExit'] == 0 and receipt['source'] == begin['source']
                 and receipt['originalBaselineUnchanged'] and receipt['snapshotInputsUnchanged'], 'genuine current host41 original')
    snapshot = prior/'snapshot';target = snapshot/'program/characterization/target'
    inputs = {p:host.sha(snapshot/p) for p in begin['inputHashes']}
    host.require(inputs == begin['inputHashes'], 'fixed whole source snapshot before static checks')
    preserved = {str(p.relative_to(target)):host.sha(p) for p in target.rglob('*')
                 if p.is_file() and (p.suffix in ('.class','.jar','.exec') or 'surefire-reports' in p.parts or 'jacoco' in p.parts)}
    jdk = host.TC/'jdk-25.0.4/bin';tools = host.TC/'static-gates-20261015'
    files = [snapshot/'program/characterization'/p for p in selected.FILES[:4]]
    filelist = slot/'four-main.txt'
    with filelist.open('x') as f:f.write(''.join(str(p)+'\n' for p in files))
    cp = [tools/'record-fix-v1/pmd-record-1298.jar',*sorted((tools/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    dependency = [host.TC/f'm2/repository/com/fasterxml/jackson/core/{name}/2.19.2/{name}-2.19.2.jar'
                  for name in ('jackson-annotations','jackson-core','jackson-databind')]
    host.require(all(p.is_file() for p in cp+dependency), 'pinned existing tool and qualified Jackson dependencies')
    aux = slot/'aux.txt'
    with aux.open('x') as f:f.write('\n'.join(str(p) for p in [target/'classes',*dependency])+'\n')
    rules = host.ROOT/'tools/quality/static'
    commands = {
      'pmd':[str(jdk/'java'),'-cp',':'.join(str(p) for p in cp),'net.sourceforge.pmd.cli.PmdCli','check',
             '--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5',
             '--aux-classpath','file:'+str(aux),'--no-cache','--format','xml','--report-file',str(slot/'pmd.xml')],
      'checkstyle':[str(jdk/'java'),'-jar',str(tools/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),
                    '-f','xml','-o',str(slot/'checkstyle.xml'),'@'+str(filelist)],
      'spotbugs':[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
                  '-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-pl','program/characterization',
                  '-Dspotbugs.effort=Max','-Dspotbugs.threshold=Low','-Dspotbugs.failOnError=true',
                  '-Dspotbugs.xmlOutput=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']}
    env = dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),MAVEN_USER_HOME=str(host.TC/'m2'),
               MAVEN_SKIP_RC='true',LANG='C.UTF-8',MAVEN_OPTS='-Xmx2g')
    host.write(slot/'begin.safe.json',dict(source=begin['source'],originalHostBeginSha256=host.sha(prior/'begin.safe.json'),
               originalHostExitSha256=host.sha(prior/'exit.safe.json'),commands=commands,
               timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolSha256=host.sha(Path(__file__)),
               inputHashes=inputs,toolJars={str(p):host.sha(p) for p in cp+[tools/'checkstyle-14.3.0-all.jar']},
               rules={p.name:host.sha(p) for p in (rules/'pmd.xml',rules/'checkstyle.xml')}))
    records = {}
    for key,command in commands.items():
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (slot/(key+'.log')).open('xb') as log:
            result = subprocess.run(command,cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT)
            log.flush();os.fsync(log.fileno())
        row = dict(command=command,actualExit=result.returncode,startUTC=started,
                   endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),logSha256=host.sha(slot/(key+'.log')))
        host.write(slot/(key+'-exit.safe.json'),row);records[key]=row
    reports = {'pmd':slot/'pmd.xml','checkstyle':slot/'checkstyle.xml','spotbugs':target/'spotbugsXml.xml'}
    findings = {}
    for key,path in reports.items():
        root = ET.parse(path).getroot()
        nodes = root.findall('.//{*}violation') if key == 'pmd' else root.findall('.//error') if key == 'checkstyle' else root.findall('.//BugInstance')
        findings[key] = [dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in nodes]
        records[key].update(reportSha256=host.sha(path),findings=len(nodes))
        if key == 'pmd':records[key]['processingErrors']=len(root.findall('.//{*}error'))
    host.require({p:host.sha(snapshot/p) for p in inputs} == inputs
                 and all(host.sha(target/p) == h for p,h in preserved.items()), 'all original input/PT/class/coverage bytes preserved')
    value = dict(source=begin['source'],run='PG'+slot.name.removeprefix('pg'),records=records,findings=findings,
                 actualRawStageExitsPreserved=True,newTestsExecuted=0,productionSixChanged=False,
                 originalHostProofUnchanged=True,F03Accepted=False,formalUpdated=False,reviewStatus='PENDING')
    host.write(slot/'manifest.safe.json',value)
    out = host.BASE/('PG'+slot.name.removeprefix('pg'));out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(source=begin['source'],records={k:{x:v[x] for x in ('actualExit','findings')} for k,v in records.items()},
                         publicManifestSha256=host.sha(out/'manifest.json'),review='PENDING')))


if __name__ == '__main__':
    main()
