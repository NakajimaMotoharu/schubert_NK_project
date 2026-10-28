"""Record existing CLI runtime and fresh-source auxiliary bytes before any replacement analysis."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = '6d7f55c22a3ffec8a9013e706282ac845c595492'
OUT = data.BASE/'PG13213-spotbugs-fresh-aux-plan-v2'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13213-spotbugs-fresh-aux-plan-v2'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    n = data.read_checked(data.BASE/'PG13208-resource-db-literal-v1/manifest.json','01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == 0
    repo = runner.TC/'m2/repository';ns = {'m':'http://maven.apache.org/POM/4.0.0'}
    plugin_pom = repo/'com/github/spotbugs/spotbugs-maven-plugin/4.10.4.0/spotbugs-maven-plugin-4.10.4.0.pom'
    plugin = ET.fromstring(plugin_pom.read_bytes());properties = plugin.find('m:properties',ns)
    assert properties.findtext('m:spotbugs.version',namespaces=ns) == '4.10.4'
    assert properties.findtext('m:log4j2.version',namespaces=ns) == '2.26.1' and properties.findtext('m:slf4jVersion',namespaces=ns) == '2.0.18'
    assert properties.findtext('m:io.version',namespaces=ns) == '2.22.0'
    dependency = next(r for r in plugin.findall('m:dependencies/m:dependency',ns) if r.findtext('m:artifactId',namespaces=ns) == 'spotbugs')
    assert [(r.findtext('m:groupId',namespaces=ns),r.findtext('m:artifactId',namespaces=ns)) for r in dependency.findall('m:exclusions/m:exclusion',ns)] == [('org.apache.logging.log4j','log4j-core')]
    pom = repo/'com/github/spotbugs/spotbugs/4.10.4/spotbugs-4.10.4.pom';root = ET.fromstring(pom.read_bytes())
    tools = [repo/'com/github/spotbugs/spotbugs/4.10.4/spotbugs-4.10.4.jar']
    for row in root.findall('m:dependencies/m:dependency',ns):
        group,artifact,version = [row.findtext('m:'+k,namespaces=ns) for k in ['groupId','artifactId','version']]
        if artifact == 'log4j-core':continue # Same explicit exclusion as the existing Maven plugin, not an analyzer filter.
        tools.append(repo/group.replace('.','/')/artifact/version/(artifact+'-'+version+'.jar'))
    tools += [repo/p for p in ['org/apache/logging/log4j/log4j-api/2.26.1/log4j-api-2.26.1.jar',
        'org/apache/logging/log4j/log4j-to-slf4j/2.26.1/log4j-to-slf4j-2.26.1.jar','org/slf4j/slf4j-simple/2.0.18/slf4j-simple-2.0.18.jar',
        'commons-io/commons-io/2.22.0/commons-io-2.22.0.jar','org/xmlresolver/xmlresolver/5.3.3/xmlresolver-5.3.3.jar',
        'org/xmlresolver/xmlresolver/5.3.3/xmlresolver-5.3.3-data.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar']]
    assert len(tools) == len(set(tools)) and all(p.is_file() for p in tools)
    tool_hashes = {str(p):data.sha(p.read_bytes()) for p in [*tools,pom,plugin_pom,runner.TC/'jdk-25.0.4/bin/java']}
    fresh = {r:i['path'] for r,i in n['jars'].items()};jar_hashes = {i['path']:i['sha256'] for i in n['jars'].values()}
    expected = {};old_aux = {};aux = set(fresh.values());missing = {};old_reports = {}
    for role,item in n['jars'].items():
        path = Path(item['path']);assert data.sha(path.read_bytes()) == item['sha256']
        with zipfile.ZipFile(path) as archive:expected[role] = sorted(x for x in archive.namelist() if x.endswith('.class'))
        report = path.parent/'spotbugsXml.xml';raw = report.read_bytes();old_reports[role] = data.sha(raw)
        missing[role] = [node.text for node in ET.fromstring(raw).iter('MissingClass')]
        aux_files = list(path.parent.glob('spotbugsAuxClasspath*.tmp'));assert len(aux_files) == 1
        values = aux_files[0].read_text().splitlines();old_aux[role] = dict(path=str(aux_files[0]),sha256=data.sha(aux_files[0].read_bytes()),staleProjectJars=[])
        for value in values:
            if '/dev/codex/schubert/schubert-nk-' in value:
                old_aux[role]['staleProjectJars'].append(dict(path=value,sha256=data.sha(Path(value).read_bytes())))
            else:aux.add(value)
    assert sum(map(len,expected.values())) == 1843 and sum(map(len,missing.values())) == 18
    assert all(Path(p).is_file() for p in aux)
    aux_hashes = {p:data.sha(Path(p).read_bytes()) for p in sorted(aux)}
    assert not any('/dev/codex/schubert/schubert-nk-' in p for p in aux_hashes)
    for role,items in missing.items():
        for name in items:
            entry = name.replace('.','/')+'.class'
            assert sum(entry in names for names in expected.values()) == 1
    SLOT.mkdir();runner.SLOT = SLOT
    plan = dict(source=SOURCE,invocation=invocation,toolRuntimeHashes=tool_hashes,toolClasspath=[str(p) for p in tools],auxiliaryClasspathHashes=aux_hashes,
        normalManifestSha256='01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4',currentJarHashes=jar_hashes,currentJarsByRole=fresh,
        expectedClasses=expected,expectedMainClasses=1843,oldMissingClasses=missing,oldReportHashes=old_reports,oldAux=old_aux,
        configuration=dict(version='4.10.4',effort='max',threshold='low',excludes=[],onlyAnalyze=None,productTestsExecuted=0),
        oldIncompleteReportsPreserved=True,newAccepted=0,whole451Accepted=False)
    data.write(SLOT/'begin.safe.json',plan)
    stage = runner.step('cli-help',[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',os.pathsep.join(map(str,tools)),'edu.umd.cs.findbugs.FindBugs2','-help'],SLOT,timeout=60)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    help_text = (SLOT/'cli-help.stdout').read_text()+(SLOT/'cli-help.stderr').read_text()
    assert all(flag in help_text for flag in ['-auxclasspath','-effort','-low','-xml','-exitcode'])
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tool_hashes,**aux_hashes}.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(plan,actualExit=0,stages=[stage],helpSha256=data.sha(help_text.encode()),
        analysisExecuted=False,productTestsExecuted=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
