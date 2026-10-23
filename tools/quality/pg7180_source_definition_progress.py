"""Definition growth is not execution success, WBS acceptance, cost consumption or completion rate."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SOURCE='3b2ef576cf46763d67a9e2914dc547afd2f93ef6'
BASELINE='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
OUT=host.BASE/'PG7180-source-definition-progress-v1'
COMPILE=host.W/'pg7170-observation-clock-six-compile-v1/manifest.safe.json'


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only definition audit')
    compiled=json.loads(COMPILE.read_bytes())
    require(compiled['source']==SOURCE and compiled['actualExit']==0 and compiled['testsExecuted']==0,'exact normal Main/Test compile, not PT pass')
    parts=subprocess.check_output(['git','diff','--name-status','-z',BASELINE,SOURCE,'--','src'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts)%2==0,'source grammar')
    rows=[];test_keys=set();main=metadata=0
    for i in range(0,len(parts),2):
        status,path=parts[i].decode(),parts[i+1].decode()
        if status!='A' or not path.endswith('.java'):continue
        raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        digest=hashlib.sha256(raw).hexdigest()
        require(compiled['begin']['inputHashes'].get(path)==digest,'every counted file is in the normal actual compiled-source snapshot')
        row=dict(path=path,sha256=digest)
        if '/src/main/java/' in path:
            main+=1;metadata+=int(path.endswith('/package-info.java'))
            row.update(kind='MAIN_JAVA_DEFINITION',testMethods=[])
        else:
            require('/src/test/java/' in path,'only Main/Test Java definitions')
            text=raw.decode('utf-8')
            methods=re.findall(r'^\s*@Test\s*\n\s*void\s+([A-Za-z0-9_]+)\s*\(',text,re.MULTILINE)
            require(len(methods)==len(re.findall(r'^\s*@Test\s*$',text,re.MULTILINE))
              and not re.search(r'@(?:ParameterizedTest|RepeatedTest|TestFactory|Nested)\b',text),'only exact ordinary Test definitions counted; unknown schema is not estimated')
            package=re.search(r'^package\s+([^;]+);',text,re.MULTILINE).group(1)
            owner=package+'.'+Path(path).stem
            for name in methods:
                require((owner,name) not in test_keys,'unique definition identity');test_keys.add((owner,name))
            row.update(kind='TEST_JAVA_DEFINITION',className=owner,testMethods=methods)
        rows.append(row)
    tests=[r for r in rows if r['kind']=='TEST_JAVA_DEFINITION']
    require(main==18 and metadata==2 and len(tests)==18 and len(test_keys)==123,'exact declared growth, no execution extrapolation')
    value=dict(actualExit=0,source=SOURCE,baseline=BASELINE,invocation=invocation,normalCompileManifestSha256=host.sha(COMPILE),
      rows=rows,addedMainJavaFiles=main,nonExecutablePackageMetadataFiles=metadata,addedPrimaryExecutableMainSourceFiles=main-metadata,
      addedTestJavaFiles=len(tests),addedOrdinaryTestMethodDefinitions=len(test_keys),
      executedByThisAudit=0,definitionCountIsNotPassCount=True,definitionCountIsNotAcceptedWbsCount=True,
      currentSourceExecutedDomain='Batch monitoring91 only; Web23/config9 are historical execution sources, never summed',
      newOriginal190Accepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,addedPrimaryMainSources=main-metadata,packageMetadata=metadata,
      addedTestClasses=len(tests),addedTestMethodDefinitions=len(test_keys),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
