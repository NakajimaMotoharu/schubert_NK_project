"""New Main source static preflight after normal compilation, before ordinary JUnit; no PT."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
import pg7770_media_bytes_six_compile as compilation
import pg7032_monitoring_six_artifact_post as steps
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7771-media-bytes-preflight-static-v1'
OUT=host.BASE/'PG7771-media-bytes-preflight-static-v1'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/MediaBytesMetricRecorder.java'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only static preflight')
    normal=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes());snapshot=compilation.SLOT/'snapshot'
    require(normal['actualExit']==normal['terminal']['actualExit']==0 and normal['source']==compilation.SOURCE
      and normal['testsExecuted']==0,'genuine normal compile, not PT')
    require(all(host.sha(snapshot/p)==h for p,h in normal['begin']['inputHashes'].items()),'fixed input source')
    require(host.sha(host.ROOT/MAIN)==normal['begin']['inputHashes'][MAIN],'current new Main exact byte')
    dependencies={**normal['begin']['dependencyJarHashes'],**{r['path']:r['sha256'] for r in normal['jars'].values()}}
    require(all(host.sha(Path(p))==h for p,h in dependencies.items()),'all actual current reactor and SDK bindings')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT
    listing=SLOT/'main.txt'
    with listing.open('x') as stream:stream.write(str(snapshot/MAIN)+'\n')
    static=host.TC/'static-gates-20261015';pmdcp=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    command=[str(host.TC/'jdk-25.0.4/bin/java'),'-cp',os.pathsep.join(str(p) for p in pmdcp),'net.sourceforge.pmd.cli.PmdCli','check',
      '--file-list',str(listing),'--rulesets',str(host.ROOT/'tools/quality/static/pmd.xml'),'--use-version','java-25','--minimum-priority','5',
      '--aux-classpath',os.pathsep.join(dependencies),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')]
    row,_=steps.step('pmd-new-main',command);root=ET.parse(SLOT/'pmd.xml').getroot()
    findings=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in root.findall('.//{*}violation')]
    require(row['actualExit'] in (0,4) and not root.findall('.//{*}error'),'valid actual PMD result, no processing errors')
    value=dict(actualExit=row['actualExit'],source=compilation.SOURCE,invocation=invocation,receipt=row,sourcePath=MAIN,
      sourceSha256=normal['begin']['inputHashes'][MAIN],compileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),
      dependencyHashes=dependencies,reportSha256=host.sha(SLOT/'pmd.xml'),findings=findings,productionPtExecuted=0,
      formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=row['actualExit'],findings=findings,manifestSha256=host.sha(OUT/'manifest.json'))))
    raise SystemExit(row['actualExit'])

if __name__=='__main__':main()
