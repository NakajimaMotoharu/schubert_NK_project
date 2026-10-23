"""Independent original-result/CRC/session/static post for the pure mode component."""
import datetime
import hashlib
import json
import os
import platform
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify
from pg7006_monitoring_pure_host import POM, SLOT, SUITE

OUT = host.BASE/'PG7008-monitoring-mode-post-v1'
PRIVATE = host.W/'pg7008-monitoring-mode-post-v1'
PREFIX = 'dev/codex/schubert/nk/batch/monitoring/'
NAMES = {PREFIX+'MonitoringModePolicy', PREFIX+'MonitoringModePolicy$DetailService'}
METHODS = {
 'monMode001ApprovedLiteralSettings','monMode002MatchingObservationsNotMutated',
 'monMode003AllThirtyTwoServiceStates','monMode004MissingObservationNeverMeansHealthy',
 'monMode005NullContractsAreNotNormalObservations','monMode006UnknownAndAliasedInputIsRedacted',
 'monMode007ConcurrentCallersCannotChangePolicy'}
EXPECTED_SUITES = {SUITE:dict(tests=7,failures=0,errors=0,skipped=0)}
TOTAL_TESTS = 7
SOURCE_FILE_COUNT = 3
SOURCE_ROOT_PREFIX = 'src/schubert-nk-batch/'
RUN = 'PG7006-monitoring-pure-host-v1'


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    os.umask(0o077);PRIVATE.mkdir()
    original = json.loads((SLOT/'manifest.safe.json').read_bytes())
    begin = json.loads((SLOT/'begin.safe.json').read_bytes())
    require(original['actualExit']==0 and [s['actualExit'] for s in original['stages']]==[0,0],
            'genuine prior format and verify terminal zero')
    require(original['source']==begin['source'] and original['begin']==begin,'original identities')
    require(original['suites']==EXPECTED_SUITES,'exact original declared suites and counts FES0')
    require({c['name'] for c in original['cases']}==METHODS and len(original['cases'])==TOTAL_TESTS
            and all(c['result']=='PASS' for c in original['cases']),'all declared original invocations no rerun/flaky')
    snapshot = SLOT/'snapshot';target = snapshot/'tools/quality/harnesses/target'
    require(all(host.sha(snapshot/p)==h for p,h in begin['inputHashes'].items()),'all immutable original source/POM hashes')
    for p,h in original['xmlHashes'].items():
        require(host.sha(target/'surefire-reports'/p)==h,'actual original XML hash')
    source_files = {p:h for p,h in begin['inputHashes'].items() if p.startswith(SOURCE_ROOT_PREFIX) and '/monitoring/' in p and p.endswith('.java')}
    require(len(source_files)==SOURCE_FILE_COUNT and all(host.sha(host.ROOT/p)==h for p,h in source_files.items()),'all declared current Main/Test source files exact')
    physical = {p.relative_to(target/'classes').as_posix():host.sha(p) for p in (target/'classes').rglob('*.class')}
    require(set(physical)=={n+'.class' for n in NAMES}|{PREFIX+'package-info.class'},'all declared executable plus metadata class')
    jdk = host.TC/'jdk-25.0.4/bin'
    libs = [host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
      *[host.TC/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    cp = ':'.join(str(p) for p in libs)
    classes = PRIVATE/'classes';classes.mkdir()
    source = host.ROOT/'tools/quality/architecture/ComponentCoverageAudit.java'
    commands = [('audit-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(source)]),
      ('audit-run',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'ComponentCoverageAudit',str(target/'jacoco.exec'),str(target/'classes'),*sorted(NAMES)])]
    stages=[];output=''
    for name, command in commands:
        done = subprocess.run(command,capture_output=True,text=True)
        row=dict(command=command,actualExit=done.returncode,stdout=done.stdout,stderr=done.stderr)
        host.write(PRIVATE/(name+'-exit.safe.json'),row);stages.append(row)
        require(done.returncode==0,'independent CRC/counter/session read zero')
        output=done.stdout
    independent={}
    for line in output.splitlines():
        parts=line.split('\t')
        if parts[0]=='CLASS':
            counts={}
            for item in parts[3:]:
                key,missed,covered=item.split(':');counts[key]=dict(missed=int(missed),covered=int(covered))
            independent[parts[1]]=dict(crc64=parts[2],counters=counts)
    require(set(independent)==NAMES,'all declared executed CRC identities')
    for name, value in independent.items():
        measured=original['counters'][name]
        for kind,count in value['counters'].items():
            require(count==measured.get(kind,dict(missed=0,covered=0)),'independent exec counters equal XML')
    report = ET.parse(target/'spotbugsXml.xml').getroot()
    spotbugs = report.findall('.//BugInstance')
    require(not spotbugs and not report.findall('.//MissingClass'),'actual component SpotBugs no findings/missing classes')
    tools = host.TC/'static-gates-20261015'
    filelist = PRIVATE/'main.txt'
    main_paths = [snapshot/p for p in source_files if '/src/main/java/' in p]
    with filelist.open('x') as stream:stream.write(''.join(str(p)+'\n' for p in sorted(main_paths)))
    pmdcp = [tools/'record-fix-v1/pmd-record-1298.jar',*sorted((tools/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    require(all(p.is_file() for p in libs+pmdcp),'pinned existing static/audit jars')
    rules = host.ROOT/'tools/quality/static'
    aux = str(target/'classes')+':'+str(host.TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')
    static_commands = [
      ('pmd',[str(jdk/'java'),'-cp',':'.join(str(p) for p in pmdcp),'net.sourceforge.pmd.cli.PmdCli','check',
        '--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5',
        '--aux-classpath',aux,'--no-cache','--format','xml','--report-file',str(PRIVATE/'pmd.xml')]),
      ('checkstyle',[str(jdk/'java'),'-jar',str(tools/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),
        '-f','xml','-o',str(PRIVATE/'checkstyle.xml'),'@'+str(filelist)])]
    raw={}
    for name, command in static_commands:
        done=subprocess.run(command,capture_output=True,text=True)
        host.write(PRIVATE/(name+'-exit.safe.json'),dict(command=command,actualExit=done.returncode,
          stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
        xml=ET.parse(PRIVATE/(name+'.xml')).getroot()
        findings=xml.findall('.//{*}violation') if name=='pmd' else xml.findall('.//error')
        raw[name]=dict(command=command,actualExit=done.returncode,reportSha256=host.sha(PRIVATE/(name+'.xml')),
                      findings=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in findings],
                      processingErrors=len(xml.findall('.//{*}error')) if name=='pmd' else 0)
    totals={kind:dict(missed=sum(v['counters'][kind]['missed'] for v in independent.values()),
      covered=sum(v['counters'][kind]['covered'] for v in independent.values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    require(all(v['missed']==0 and v['covered']>0 for v in totals.values()),'all four real component counters100')
    require(all(host.sha(snapshot/p)==h for p,h in begin['inputHashes'].items()),'all source unchanged after post')
    value=dict(source=begin['source'],sourceRun=RUN,actualExit=0,
      originalManifestSha256=host.sha(SLOT/'manifest.safe.json'),originalBeginSha256=host.sha(SLOT/'begin.safe.json'),
      originalArchiveSha256=host.sha(SLOT/'source.tar'),command=invocation['actualPythonCommand'],
      invocation=invocation,
      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.platform(),
      toolSha256=host.sha(Path(__file__)),harnessPomSha256=host.sha(snapshot/POM),sourceFiles=source_files,
      xmlHashes=original['xmlHashes'],tests=TOTAL_TESTS,suites=len(EXPECTED_SUITES),physicalClasses=physical,executableClasses=independent,
      metadataClasses=[PREFIX+'package-info.class'],actualCrcMismatch=0,actualSessions=1,counters=totals,
      spotbugs=dict(actualExit=0,findings=0,reportSha256=host.sha(target/'spotbugsXml.xml')),
      staticRaw=raw,staticDispositionRequired=any(v['actualExit']!=0 or v['findings'] or v['processingErrors'] for v in raw.values()),
      auditStages=stages,auditLibraries={str(p):host.sha(p) for p in libs},
      formalUpdated=False,wholeSixQualified=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,original4222Repeated=False,original44Repeated=False)
    verify(invocation)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=begin['source'],tests=TOTAL_TESTS,counters=totals,
      static={k:dict(actualExit=v['actualExit'],findings=len(v['findings'])) for k,v in raw.items()},
      manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
