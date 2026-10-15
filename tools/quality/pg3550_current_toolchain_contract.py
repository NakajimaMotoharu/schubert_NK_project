"""F02 bounded toolchain/build/boundary evidence; cross-SYS leaf remains open."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from pg1446_current_cold_stage import W
from pg3520_outbox_owned_sources_v2 import SOURCE

ROOT=Path(__file__).resolve().parents[2]
TC=ROOT.parent/'toolchain'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3550-current-toolchain-contract'
EXPECTED={'protocol':set(),'storage':set(),'bootstrap':{'storage'},'api':{'protocol','storage','bootstrap'},
          'web':{'protocol','storage','bootstrap'},'batch':{'storage','bootstrap'}}
NS={'m':'http://maven.apache.org/POM/4.0.0'}


def require(value,message):
    if not value:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def verify_graph(graph):
    require(type(graph)is dict and set(graph)==set(EXPECTED),'all six declared modules required')
    require(all(type(graph[n])is set and graph[n]==EXPECTED[n]for n in EXPECTED),'exact SS311 compile/runtime boundary required')
    def walk(node,path):
        require(node not in path,'internal module cycle forbidden')
        for child in graph[node]:walk(child,path|{node})
    for node in graph:walk(node,set())
    return True


def collect():
    f=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())
    v=f['result'];require(f['actualExit']==v['actualExit']==v['FESFlakyNotRun']==v['staticSixModules']==0 and v['productionSource']==SOURCE and(v['tests'],v['suites'],v['mainClasses'])==(3712,545,1643),'actual qualified current six-module build required')
    root=ET.parse(ROOT/'pom.xml').getroot();release=root.findtext('m:properties/m:maven.compiler.release',namespaces=NS)
    require(release=='25','SS/RD Java25 target required')
    modules=[n.text for n in root.findall('m:modules/m:module',NS)]
    require(modules==['program/characterization',*[f'src/schubert-nk-{m}'for m in EXPECTED]],'compatibility separate from six Production modules')
    graph={};test_edges={};poms={'pom.xml':sha((ROOT/'pom.xml').read_bytes())}
    for module in EXPECTED:
        p=ROOT/f'src/schubert-nk-{module}/pom.xml';poms[str(p.relative_to(ROOT))]=sha(p.read_bytes())
        require(subprocess.check_output(['git','show',SOURCE+':'+str(p.relative_to(ROOT))],cwd=ROOT)==p.read_bytes(),'same qualified POM bytes required')
        tree=ET.parse(p).getroot();normal=set();tests=[]
        for d in tree.findall('m:dependencies/m:dependency',NS):
            if d.findtext('m:groupId',namespaces=NS)!='dev.codex.schubert':continue
            target=d.findtext('m:artifactId',namespaces=NS);require(target.startswith('schubert-nk-'),'only explicit internal artifact names')
            target=target[len('schubert-nk-'):];scope=d.findtext('m:scope','compile',NS)
            if scope=='test':tests.append({'module':target,'type':d.findtext('m:type','jar',NS)})
            else:require(scope in {'compile','runtime'},'explicit internal runtime scope required');normal.add(target)
        graph[module]=normal;test_edges[module]=tests
    verify_graph(graph)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owners={a['class'].replace('/','.'):a['module']for a in inventory['artifacts']if a.get('class')}
    relocated={}
    for p in(ROOT/'src/schubert-nk-batch/src/main/java').rglob('*.java'):
        for item in re.findall(r'^import (?:static )?(dev\.codex\.schubert\.nk\.api\.[\w.]+);',p.read_text(),re.M):
            candidates=[k for k in owners if item==k or item.startswith(k+'.')]
            require(candidates,'closed imported type must have physical ownership')
            owner=owners[max(candidates,key=len)];require(owner=='bootstrap','Batch business API artifact/type dependency forbidden')
            relocated[item]=owner
    for module,prefixes in [('storage',('java.sql.','javax.sql.','org.postgresql.','jakarta.jms.')),
                            ('bootstrap',('java.net.http.','jakarta.jms.','org.springframework.web.'))]:
        for p in(ROOT/f'src/schubert-nk-{module}/src/main/java').rglob('*.java'):
            imports=re.findall(r'^import (?:static )?([^;]+);',p.read_text(),re.M)
            require(not any(i.startswith(prefixes)for i in imports),'native-only Storage/pure Bootstrap boundary')
    versions={};commands={};env={k:x for k,x in os.environ.items()if k not in {'JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','MAVEN_OPTS'}}
    env['JAVA_HOME']=str(TC/'jdk-25.0.4')
    executables={'java':TC/'jdk-25.0.4/bin/java','maven':TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'}
    for name,p in executables.items():
        require(p.is_file()and os.access(p,os.X_OK),'existing installed executable only; no install/download')
        command=[str(p),'--version'];r=subprocess.run(command,capture_output=True,env=env,timeout=30,cwd=ROOT)
        require(r.returncode==0,'tool version observation must succeed')
        text=(r.stdout+r.stderr).decode();require(('25.0.4'in text)if name=='java'else('Apache Maven 3.9.12'in text and'Java version: 25.0.4'in text),'pinned observed versions required')
        versions[name]={'output':text,'executableSha256':sha(p.read_bytes()),'path':str(p)}
        commands[name]={'argv':command,'actualExit':0,'outputSha256':sha(r.stdout+r.stderr)}
    wrappers={p:sha((ROOT/p).read_bytes())for p in ['mvnw','.mvn/wrapper/maven-wrapper.properties']}
    docs={p:sha((ROOT/p).read_bytes())for p in ['documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md','documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md','documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md']}
    return {'actualExit':0,'productionSource':SOURCE,'run':'PG3550-current-toolchain-contract','versions':versions,'commands':commands,
            'pomSha256':poms,'wrapperSha256':wrappers,'documentSha256':docs,'reactorModules':modules,
            'runtimeGraph':{k:sorted(x)for k,x in graph.items()},'testOnlyEdges':test_edges,'relocatedApiBinaryNamesOwnedByBootstrap':relocated,
            'actualQualifiedBuild':{'sourceSnapshot':v['sourceSnapshot'],'tests':3712,'suites':545,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'serverManifestSha256':v['serverManifestSha256'],'jarHashes':v['jarHashes']},
            'coverageApplicability':'F02 toolchain contract has no owned Java artifact; this is not global four100/F03 acceptance',
            'verifiedSubset':['Java25 Ubuntu distribution and reproducible Maven3.9.12 wrapper','actual six Production module build/source/package','explicit acyclic compile/runtime and separate test dependency boundary','characterization framework kept outside Production src'],
            'crossSysRequirementsStillNeedEvidence':['SYS-001','SYS-003','SYS-004','SYS-005','SYS-006','SYS-007','SYS-008','SYS-009','SYS-010','SYS-012','SYS-013','SYS-014'],
            'remainingReason':'F02 owns13 SYS requirements, including all business MQ communication, all-screen compatibility, local storage and entry/certificate configuration. Toolchain alone is insufficient; keep the leaf NOT_ACCEPTED until individual cross-scope proofs/exit criteria are joined.',
            'initialReadOnlyPathProbe127NotBuildFailure':'Assumed standalone apache-maven directory was absent; located existing wrapper cache before real Maven execution. No installation or full build was issued.',
            'newPtCredit':0,'acceptedWbsDelta':0,'F02Accepted':False,'F03Accepted':False,'formalUpdated':False,
            'fullMavenReissued':False,'vmActions':0,'installedNewTools':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}


def main():
    result=collect();PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'source':SOURCE,'sixModuleBoundaryVerified':True,'buildReissued':False,'F02Accepted':False,'acceptedWbsDelta':0,'manifestSha256':sha((PUBLIC/'manifest.json').read_bytes())}));return 0


if __name__=='__main__':raise SystemExit(main())
