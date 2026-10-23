"""Independent original XML/resource/directive/owner join, never a systemd operation."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg6950_c02_scope_matrix as schema
import pg7036_c02_four_template_host as run

OUT = host.BASE/'PG7038-c02-four-template-post-v1'
OLD = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    os.umask(0o077)
    original=json.loads((run.SLOT/'manifest.safe.json').read_bytes())
    begin=json.loads((run.SLOT/'begin.safe.json').read_bytes())
    require(original['actualExit']==0 and [s['actualExit'] for s in original['stages']]==[0,0],
            'actual original format and text-only PT terminal0')
    require(original['begin']==begin and original['suites']=={
      run.SUITE:dict(tests=5,failures=0,errors=0,skipped=0)},'exact original five FES0')
    require({c['name'] for c in original['cases']}==run.METHODS and len(original['cases'])==5
      and all(c['result']=='PASS' for c in original['cases']),'all five original methods no skipped/flaky/rerun')
    snapshot=run.SLOT/'snapshot';target=snapshot/'tools/quality/harnesses/target-deployment-unit'
    require(all(host.sha(snapshot/p)==h for p,h in begin['inputHashes'].items()),'all original snapshot inputs unchanged')
    require(all(host.sha(target/'surefire-reports'/p)==h for p,h in original['xmlHashes'].items()),'actual original XML')
    pmo=host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    owners={a['path']:a for a in json.loads(pmo.read_bytes())['currentPhysicalCandidate']['artifacts']}
    rows=[]
    require(set(original['actualResources'])==set(run.FILES),'four exact actual resources')
    for name in run.FILES:
        path='src/deployment/systemd/'+name
        actual=snapshot/path
        old=subprocess.check_output(['git','show',OLD+':'+path],cwd=host.ROOT)
        require(actual.read_bytes()==old==(host.ROOT/path).read_bytes(),'each old/current/executed source byte fixed')
        require(owners[path]['owner']=='WBS-C02' and owners[path]['sha256']==host.sha(actual),'existing exact C02 ownership')
        require(host.sha(actual)==original['actualResources'][name]
          ==host.sha(target/'test-classes/systemd'/name),'executed classpath resource bytes')
        directives=schema.directives(actual.read_text())
        rows.append(dict(path=path,sha256=host.sha(actual),owner='WBS-C02',orderedDirectives=directives,
          directiveCount=len(directives),testId='PT-OPS-UNIT-SUP00'+str(len(rows)+1),
          declarationOnlyNotEffectiveUnit=True))
    require(not list((target/'classes').rglob('*.class')),'no application classes in this harness')
    test_classes={p.relative_to(target/'test-classes').as_posix():host.sha(p)
      for p in (target/'test-classes').rglob('*.class')}
    require(set(test_classes)=={
      'dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest.class',
      'dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest$Template.class'},'only test/helper classes')
    pom=ET.parse(snapshot/run.POM).getroot()
    deps=[(n.findtext('{*}groupId'),n.findtext('{*}artifactId')) for n in pom.findall('{*}dependencies/{*}dependency')]
    require(deps==[('org.junit.jupiter','junit-jupiter')],'no executable production dependency')
    plugin=next(p for p in pom.findall('.//{*}build/{*}plugins/{*}plugin')
      if p.findtext('{*}artifactId')=='maven-compiler-plugin')
    require([p.text for p in plugin.findall('{*}configuration/{*}compilerArgs/{*}arg')]==['-Xlint:all','-Werror'],
            'actual new harness explicitly enforces Test lint/Werror')
    designs={}
    for name in ('341_朝batch・backup・削除・再実行設計.md',
                 '342_Caddy・systemd・PostgreSQL・Java設定設計.md',
                 '343_設定file・directory・初期data・migration・切戻し設計.md'):
        path='documents/300_SS/340_batch・基盤/'+name
        require(subprocess.check_output(['git','show','origin/main:'+path],cwd=host.ROOT)==(host.ROOT/path).read_bytes(),
                'canonical design/current byte match')
        designs[path]=host.sha(host.ROOT/path)
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      source=original['source'],command='python3 -B tools/quality/pg7038_c02_four_template_post.py',
      toolSha256=host.sha(Path(__file__)),originalManifestSha256=host.sha(run.SLOT/'manifest.safe.json'),
      originalBeginSha256=host.sha(run.SLOT/'begin.safe.json'),archiveSha256=begin['archiveSha256'],
      tests=5,directConfigurationCases=4,oracleCaseCount=1,oracleMutationChecks=12,oracleNullCheck=1,
      suites=1,xmlHashes=original['xmlHashes'],sourceFiles=rows,allDirectivesClassified=True,
      directiveCount=sum(r['directiveCount'] for r in rows),testClassHashes=test_classes,
      testSourceSha256=host.sha(snapshot/run.TEST),harnessPomSha256=host.sha(snapshot/run.POM),
      canonicalDesignHashes=designs,coverage='NOT_APPLICABLE_CONFIGURATION_NOT_JAVA_NO_0_OVER_0_PASS',
      productionMainClasses=0,testLintWerror=True,actualManagerNssKernelAccess=0,
      actualVmActions=0,actualDatabaseActions=0,credentialTargetsRead=False,
      effectiveBaseUnitNotVerified=True,old22CasesReplayed=False,original4222Repeated=False,
      original48Repeated=False,wholeC02Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=5,resources=4,directives=value['directiveCount'],
                         applicationClasses=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
