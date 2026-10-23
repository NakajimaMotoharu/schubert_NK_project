"""Independent text-only original XML/resource/owner/canonical-design qualification."""
import datetime
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host
import pg7040_c06_config_template_host as run

OUT = host.BASE/'PG7042-c06-config-template-post-v1'
OLD = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'


def require(value, message):
    if not value:
        raise ValueError(message)


def entries(name, text):
    result={}
    for raw in text.splitlines():
        line=raw.strip()
        if not line or line.startswith('#'):
            continue
        if name.endswith('.yml.template'):
            key,separator,value=line.partition(': ')
            require(separator,'flat declared YAML separator')
            key=json.loads(key);value=json.loads(value)
            require(type(key) is str and type(value) in (str,int),'source scalar kinds only')
        else:
            key,separator,value=line.partition('=')
            require(separator and key,'explicit source env field')
        require(key not in result,'no duplicated source declaration')
        result[key]=value
    return result


def main():
    os.umask(0o077)
    original=json.loads((run.SLOT/'manifest.safe.json').read_bytes())
    begin=json.loads((run.SLOT/'begin.safe.json').read_bytes())
    require(original['actualExit']==0 and [s['actualExit'] for s in original['stages']]==[0,0],
            'genuine original format and text-only PT terminal0')
    require(original['begin']==begin and original['suites']=={
      run.SUITE:dict(tests=4,failures=0,errors=0,skipped=0)},'exact actual four FES0')
    require({c['name'] for c in original['cases']}==run.METHODS and len(original['cases'])==4
      and all(c['result']=='PASS' for c in original['cases']),'all original invocations no flaky/rerun/skipped')
    snapshot=run.SLOT/'snapshot';target=snapshot/'tools/quality/harnesses/target-config-template'
    require(all(host.sha(snapshot/p)==h for p,h in begin['inputHashes'].items()),'all fixed original source inputs')
    require(all(host.sha(target/'surefire-reports'/p)==h for p,h in original['xmlHashes'].items()),'actual original XML hashes')
    inv=host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    owners={a['path']:a for a in json.loads(inv.read_bytes())['currentPhysicalCandidate']['artifacts']}
    require(set(original['actualResources'])==set(run.FILES),'all seven declared actual resources')
    rows=[]
    for name in run.FILES:
        path='src/deployment/config/'+name
        p=snapshot/path
        require(p.read_bytes()==subprocess.check_output(['git','show',OLD+':'+path],cwd=host.ROOT)
          ==(host.ROOT/path).read_bytes(),'old/current/executed template byte exact')
        require(owners[path]['owner']=='WBS-C06' and owners[path]['sha256']==host.sha(p),'old exact C06 ownership')
        require(host.sha(p)==original['actualResources'][name]==host.sha(target/'test-classes/config'/name),
                'all actual classpath resources match source')
        data=entries(name,p.read_text())
        rows.append(dict(path=path,sha256=host.sha(p),owner='WBS-C06',declarations=data,
          declarationCount=len(data),runtimeAuthority=False,
          inspectorUnrenderedPlaceholders=name=='inbox-inspector.env.template'))
    require(sum(r['declarationCount'] for r in rows)==55,'51 YAML scalars and four ENV fields')
    require(not list((target/'classes').rglob('*.class')),'no executable application Main')
    test_classes={p.relative_to(target/'test-classes').as_posix():host.sha(p)
      for p in (target/'test-classes').rglob('*.class')}
    require(set(test_classes)=={
      'dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.class',
      'dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest$Scalar.class'},'only Test and private data helper')
    pom=ET.parse(snapshot/run.POM).getroot()
    require([(n.findtext('{*}groupId'),n.findtext('{*}artifactId'))
      for n in pom.findall('{*}dependencies/{*}dependency')]==[('org.junit.jupiter','junit-jupiter')],
      'no executable application dependency')
    compiler=next(n for n in pom.findall('.//{*}build/{*}plugins/{*}plugin')
      if n.findtext('{*}artifactId')=='maven-compiler-plugin')
    require([a.text for a in compiler.findall('{*}configuration/{*}compilerArgs/{*}arg')]==['-Xlint:all','-Werror'],
            'actual Test compiler warning gate explicit')
    designs={}
    for name in ('341_朝batch・backup・削除・再実行設計.md',
                 '343_設定file・directory・初期data・migration・切戻し設計.md'):
        path='documents/300_SS/340_batch・基盤/'+name
        require(subprocess.check_output(['git','show','origin/main:'+path],cwd=host.ROOT)==(host.ROOT/path).read_bytes(),
                'canonical SS/current bytes identical')
        designs[path]=host.sha(host.ROOT/path)
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=original['source'],
      command='python3 -B tools/quality/pg7042_c06_config_template_post.py',toolSha256=host.sha(Path(__file__)),
      originalManifestSha256=host.sha(run.SLOT/'manifest.safe.json'),originalBeginSha256=host.sha(run.SLOT/'begin.safe.json'),
      archiveSha256=begin['archiveSha256'],tests=4,directSourceContractCases=3,oracleAuxiliaryCases=1,
      oracleMutations=11,oracleNullChecks=1,suites=1,xmlHashes=original['xmlHashes'],sourceFiles=rows,
      sourceDeclarationCount=55,batchDefaultsVerified=11,commonDefaultsVerified=3,
      allResourceBytesMatched=True,allApplicationMainClasses=0,testClassHashes=test_classes,
      testSourceSha256=host.sha(snapshot/run.TEST),harnessPomSha256=host.sha(snapshot/run.POM),
      canonicalDesignHashes=designs,testLintWerror=True,
      coverage='NOT_APPLICABLE_CONFIGURATION_NOT_JAVA_NO_0_OVER_0_PASS',
      realpathSymlinkNssMetadataNotChecked=True,credentialTargetsRead=False,
      actualVmActions=0,actualDatabaseActions=0,ordinaryRuntimeAssemblyNotInvoked=True,
      original48Repeated=False,original5Repeated=False,original4222Repeated=False,
      wholeC06Accepted=False,wholeC05Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=4,resources=7,declarations=55,mainClasses=0,
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
