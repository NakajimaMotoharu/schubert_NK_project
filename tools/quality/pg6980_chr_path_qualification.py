"""Qualify completed current green44 bytes/XML/CRC and F02 source-binding only."""
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import pg6966_chr_adapter_host as host

TARGETS = {'ArtifactComparatorTest':5,'GateCliTest':12,'GateContractTest':7,
           'GateContractValidatorNegativeTest':17,'TargetAdapterTest':3}
TYPES = ('LINE','METHOD','CLASS','BRANCH')


def counters(nodes):
    result = {n.get('type'):dict(missed=int(n.get('missed')),covered=int(n.get('covered')))
              for n in nodes if n.get('type') in TYPES}
    host.require(set(result) == set(TYPES) and all(v['missed'] == 0 and v['covered'] > 0 for v in result.values()),
                 'all actual four counters positive100, no missing dimension')
    return result


def main():
    os.umask(0o077)
    slot = host.W/'pg6980-chr-path-qualification-v1';slot.mkdir()
    prior = host.W/'pg6976-chr-path-green-v1'
    begin = json.loads((prior/'begin.safe.json').read_bytes())
    terminal = json.loads((prior/'manifest.safe.json').read_bytes())
    host.require(terminal['actualExit'] == 0 and terminal['beginSha256'] == host.sha(prior/'begin.safe.json')
                 and terminal['originalBaselineUnchanged'] and terminal['snapshotInputsUnchanged'], 'genuine complete immutable green original')
    snapshot = prior/'snapshot';target = snapshot/'program/characterization/target'
    host.require(all(host.sha(snapshot/p) == h for p,h in begin['inputHashes'].items()), 'actual original full input hashes')
    suite_counts,rows,xmls = {},[],{}
    for path in sorted((target/'surefire-reports').glob('TEST-*.xml')):
        xmls[path.name] = host.sha(path);root=ET.parse(path).getroot()
        name = root.get('name').rsplit('.',1)[-1]
        host.require(name not in suite_counts, 'unique original suite')
        suite_counts[name] = len(root.findall('testcase'))
        host.require(all(int(root.get(k,'0')) == 0 for k in ('failures','errors','skipped')),
                     'original F/E/S zero, no unavailable XML treated pass')
        for c in root.findall('testcase'):
            host.require(all(n.tag in ('system-out','system-err') for n in c), 'no flaky/rerun/failure/error/skipped invocation')
            rows.append(dict(clazz=c.get('classname'),method=c.get('name'),xmlSha256=host.sha(path),result='PASS_ORIGINAL_XML'))
    host.require(suite_counts == TARGETS and len(rows) == 44, 'all expected44 original cases/five suites only, no native case')
    report = ET.parse(target/'site/jacoco/jacoco.xml').getroot()
    whole = counters(report.findall('counter'))
    actual_classes = {str(p.relative_to(target/'classes')):host.sha(p) for p in (target/'classes').rglob('*.class')}
    host.require(len(actual_classes) == 8, 'eight physical Main')
    jar = target/'schubert-characterization-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar) as z:
        host.require({n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')} == actual_classes,
                     'packaged Jar and original executed physical classes identical')
    source = host.ROOT/'tools/quality/architecture/CommonHarnessCoverageAudit.java'
    libraries = [host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
                 *[host.TC/f'm2/repository/org/ow2/asm/{s}/9.10.1/{s}-9.10.1.jar' for s in ('asm','asm-tree','asm-commons')]]
    classpath = ':'.join(str(p) for p in libraries)
    output = slot/'classes';output.mkdir()
    commands = [[str(host.TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
                 '-cp',classpath,'-d',str(output),str(source)],
                [str(host.TC/'jdk-25.0.4/bin/java'),'-cp',str(output)+':'+classpath,'CommonHarnessCoverageAudit',
                 str(target/'jacoco.exec'),str(target/'classes')]]
    stages=[];text=''
    for i,command in enumerate(commands):
        result=subprocess.run(command,capture_output=True,text=True)
        host.write(slot/f'stage{i}-exit.safe.json',dict(command=command,actualExit=result.returncode,
                   stdoutSha256=hashlib.sha256(result.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(result.stderr.encode()).hexdigest()))
        host.require(result.returncode == 0,'independent compile and actual CRC/session audit zero')
        stages.append(dict(command=command,actualExit=0,stdout=result.stdout,stderr=result.stderr));text=result.stdout
    physical={}
    for line in text.splitlines():
        parts=line.split('\t')
        if parts[0]=='CLASS':
            values={}
            for chunk in parts[3:]:
                k,m,c=chunk.split(':');values[k]=dict(missed=int(m),covered=int(c))
            physical[parts[1]+'.class']=dict(crc64=parts[2],sha256=actual_classes[parts[1]+'.class'],counters=values)
    host.require(set(physical)==set(actual_classes),'all XML/physical/CRC rows')
    summed={k:dict(missed=sum(v['counters'][k]['missed'] for v in physical.values()),
                  covered=sum(v['counters'][k]['covered'] for v in physical.values())) for k in TYPES}
    host.require(summed == whole,'independent original exec counter sums exactly match XML')
    source_main = {p:h for p,h in begin['inputHashes'].items() if '/src/main/java/' in p and p.endswith('.java')}
    host.require(len(source_main)==4 and all(host.sha(host.ROOT/p)==h for p,h in source_main.items()),'current four Main equal executed source')
    subprocess.run(['git','diff','--exit-code',begin['source'],'--','program/characterization','pom.xml','.mvn','mvnw','src'],cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    # New common component source differs from e7; rebind only needed F02 byte scope,
    # never relabel the old execution as having run on the new commit.
    subprocess.run(['git','diff','--exit-code',host.SOURCE,begin['source'],'--','src','pom.xml','.mvn','mvnw','tools/quality/static'],
                   cwd=host.ROOT,check=True,stdout=subprocess.DEVNULL)
    value = dict(actualExit=0,source=begin['source'],qualifiedProductionSource=host.SOURCE,sourceRun='PG6976-chr-path-green-v1',
                 originalBeginSha256=host.sha(prior/'begin.safe.json'),originalExitSha256=host.sha(prior/'exit.safe.json'),
                 originalManifestSha256=host.sha(prior/'manifest.safe.json'),originalArchiveSha256=host.sha(prior/'source.tar'),
                 sourceInputs=begin['inputHashes'],xmlHashes=xmls,cases=rows,tests=44,suites=5,physicalMain=8,
                 counters=whole,physicalClasses=physical,crcClassMismatch=0,actualSessionCount=1,stages=stages,
                 tools={str(p):host.sha(p) for p in libraries},originalBaselineUnchanged=True,old41Imported=False,
                 production4222Repeated=False,F02SameBytesOfQualifiedSix=True,formalUpdated=False,effortPercent=None)
    out = host.BASE/'PG6980-chr-path-qualification-v1';out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=44,suites=5,source=begin['source'],counters=whole,crcClassMismatch=0,
                         manifestSha256=host.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
