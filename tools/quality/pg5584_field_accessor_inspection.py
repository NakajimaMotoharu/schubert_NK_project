"""Inspect64 field/accessor symbols without relaxing serialized-field rename refusal."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
W=ROOT.parent/'pgpt-runs/PG379'
SOURCE='2fc563a5f2fba4cfaf6f7a5bd56fe8909c1910ad'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5584-field-accessor-inspection-v1'
JDK=ROOT.parent/'toolchain/jdk-25.0.4/bin'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def compile_only_artifacts():
    ns={'m':'http://maven.apache.org/POM/4.0.0'};tc=ROOT.parent/'toolchain/m2/repository'
    for module in('bootstrap','web','batch'):
        tree=ET.parse(ROOT/('src/schubert-nk-'+module+'/pom.xml'))
        declarations=[d for d in tree.findall('m:dependencies/m:dependency',ns)if d.findtext('m:groupId',namespaces=ns)=='com.github.spotbugs'and d.findtext('m:artifactId',namespaces=ns)=='spotbugs-annotations']
        if len(declarations)!=1 or declarations[0].findtext('m:version',namespaces=ns)!='4.10.4'or declarations[0].findtext('m:scope',namespaces=ns)!='provided':raise ValueError('actual fixed provided annotations in all three declaring Main modules')
    pom=tc/'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.pom';tree=ET.parse(pom)
    deps=[d for d in tree.findall('m:dependencies/m:dependency',ns)if d.findtext('m:groupId',namespaces=ns)=='com.google.code.findbugs'and d.findtext('m:artifactId',namespaces=ns)=='jsr305']
    if len(deps)!=1 or deps[0].findtext('m:version',namespaces=ns)!='3.0.2'or deps[0].findtext('m:scope',namespaces=ns)!='compile':raise ValueError('fixed declared annotation transitive compile dependency')
    paths=[tc/'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',tc/'com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar']
    if any(p.is_symlink()or not p.is_file()for p in paths):raise ValueError('actual pinned local compiler artifacts only')
    return paths,[{'path':str(p),'sha256':sha(p.read_bytes()),'scope':'COMPILER_ONLY_NOT_RUNTIME','version':'4.10.4'if p==paths[0]else'3.0.2'}for p in paths]


def requests(baseline):
    rows=[];old_sources={}
    for row in baseline['findings']:
        if row['rule']!='AvoidFieldNameMatchingMethodName':continue
        relative=row['sourcePath'];path=ROOT/relative
        if not path.resolve().is_relative_to(ROOT/'src')or'/src/main/java/'not in relative:raise ValueError('known Main source only')
        current=path.read_bytes();old=current
        if sha(old)!=row['sourceSha256']:
            if relative not in old_sources:old_sources[relative]=subprocess.check_output(['git','show',baseline['source']+':'+relative],cwd=ROOT)
            old=old_sources[relative]
        if sha(old)!=row['sourceSha256']:raise ValueError('original source exact, not inferred declaration')
        line=int(row['beginline'])
        if line!=int(row['endline']):raise ValueError('explicit single-line field contract')
        a=old.decode().splitlines(keepends=True)[line-1];b=current.decode().splitlines(keepends=True)[line-1]
        if a!=b:raise ValueError('old coordinate cannot silently move or change in current source')
        match=re.fullmatch(r'\s*private final [A-Za-z0-9_.$<>?]+ (\w+);\s*',b)
        if not match:raise ValueError('each exact explicit private-final declaration')
        rows.append({k:row[k]for k in('findingId','sourcePath','beginline','endline','priority')}|
            {'field':match[1],'originalSourceSha256':sha(old),'currentSourceSha256':sha(current),'declarationSpanSha256':sha(b.encode()),
                'currentDiagnosticBindingPending':True})
    if len(rows)!=64 or len({(r['sourcePath'],r['beginline'],r['field'])for r in rows})!=64:raise ValueError('all64 unique actual declaration coordinates required')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--version',default='v1');args=parser.parse_args()
    if not re.fullmatch(r'v[1-9][0-9]*',args.version):raise ValueError('bounded explicit new-only attempt')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('current fixed source, no changes during original whole')
    raw=(ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5560-snapshot-static-findings-v1/manifest.json').read_bytes()
    if sha(raw)!='7a7e73525d491875f74685208f07595500c448a9cd380a2f4d6590162f564740':raise ValueError('immutable actual raw diagnostic baseline')
    baseline=json.loads(raw);rows=requests(baseline)
    provided,provided_metadata=compile_only_artifacts()
    private=W/('pg5584-field-accessor-'+args.version);os.umask(0o077);private.mkdir(mode=0o700);mirror=private/'input';mirror.mkdir();classes=private/'toolclasses';classes.mkdir()
    hashes={}
    for path in ROOT.glob('src/*/src/main/java/**/*.java'):
        if path.is_symlink():raise ValueError('physical Main source only')
        relative=path.relative_to(ROOT);target=mirror/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);hashes[relative.as_posix()]=sha(path.read_bytes())
        if sha(target.read_bytes())!=hashes[relative.as_posix()]:raise ValueError('analysis mirror exact')
    if len(hashes)!=849:raise ValueError('complete849 current Main for symbol resolution')
    tsv=private/'request.tsv'
    with tsv.open('x')as f:
        for row in rows:f.write(row['sourcePath']+'\t'+row['beginline']+'\t'+row['field']+'\n')
    release=W/'pg5430-release-v1';bom=(release/'RELEASE-MANIFEST.json').read_bytes()
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('fixed existing third-party dependency inventory')
    jars={}
    for row in json.loads(bom)['artifacts']:
        path=row['path']
        if '/lib/'not in path or not path.endswith('.jar')or Path(path).name.startswith('schubert-nk-'):continue
        target=release/path
        if sha(target.read_bytes())!=row['sha256']:raise ValueError('every third-party classpath artifact fixed')
        jars.setdefault(row['sha256'],target)
    roots=[W/'pg5566-private-monitor-green-v2/source'/('src/schubert-nk-'+m+'/target/classes')for m in('protocol','storage','bootstrap','api','web','batch')]
    classpath=os.pathsep.join(map(str,[*roots,*jars.values(),*provided]))
    compile_command=[str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),*[str(ROOT/'tools/quality'/n)for n in('IsolatedSourceOutput.java','SourcePrivateFieldRename.java','FieldAccessorContractProbe.java')]]
    command=[str(JDK/'java'),'-Xmx768m','-cp',str(classes),'FieldAccessorContractProbe',str(mirror),classpath,str(tsv)]
    with(private/'compile.private.log').open('xb')as f:compiled=subprocess.run(compile_command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
    if compiled.returncode:raise ValueError('public compiler probe tool must compile0')
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    with(private/'observer.private.log').open('x')as f:f.write(result.stdout+result.stderr);f.flush();os.fsync(f.fileno())
    if result.returncode:raise ValueError('typed accessor inspection did not finish0; preserve original, no normality assumption')
    observed={}
    for line in result.stdout.splitlines():
        parts=line.split('\t')
        if parts[0]=='COUNT':
            if parts!=['COUNT','64']:raise ValueError('all64 count')
            continue
        if len(parts)!=9 or parts[0]!='FIELD':raise ValueError('exact field metadata schema')
        key=tuple(parts[1:4])
        if key in observed:raise ValueError('no duplicated field')
        observed[key]={'declaringType':parts[4],'ownerKind':parts[5],'serializable':parts[6]=='true','defaultSerializedField':parts[7]=='true','publicSimpleGetter':parts[8]=='true'}
    for row in rows:
        key=(row['sourcePath'],row['beginline'],row['field'])
        if key not in observed:raise ValueError('each requested field has actual compiler binding')
        row.update(observed.pop(key))
    if observed or any(sha((ROOT/name).read_bytes())!=value or sha((mirror/name).read_bytes())!=value for name,value in hashes.items()):raise ValueError('all source/hash observations immutable')
    counts={kind:sum(row['ownerKind']==kind for row in rows)for kind in sorted({row['ownerKind']for row in rows})}
    value={'actualExit':0,'sourceSnapshot':SOURCE,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'recordedFields':64,'ownerKindCounts':counts,'fields':rows,'compileCommand':compile_command,'actualProbeExit':result.returncode,
        'helperSha256':sha((ROOT/'tools/quality/FieldAccessorContractProbe.java').read_bytes()),'originalRawDiagnosticSource':baseline['source'],'originalRawDiagnosticSha256':sha(raw),
        'all849SourceHashes':hashes,'thirdPartyJarSha256':list(jars),'modelLoadOnlyNoClassInitialization':True,'privateStateInvocations':0,
        'compileOnlyArtifacts':provided_metadata,
        'privateRenamerSerializableGuardUnchanged':True,'productionChanges':0,'ruleSuppressionAdded':False,'currentDiagnosticBindingPending':True,
        'disposition':'INSPECTION_FACTS_ONLY_NO_AUTOMATIC_STYLE_EXEMPTION','F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'vmActions':0}
    OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':SOURCE,'recordedFields':64,'ownerKindCounts':counts,'sha256':sha((OUT/'manifest.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
