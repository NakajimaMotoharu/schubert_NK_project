"""JDK disassembly metadata only. Do not persist raw disassembly, literal values or target code."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TC=ROOT.parent/'toolchain'
COMPILE=ROOT.parent/'pgpt-runs/PG379/pg9358-static-companion-compile55-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9360-static-companion-javap-v1'
OUT=BASE/'PG9360-static-companion-javap-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
ENV={'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def family(owner,target):return owner==target or owner.startswith(target+'$')

def parse_metadata(text):
    result=[];row=None
    for line in text.splitlines():
        if line.startswith('Classfile '):
            if row is not None:result.append(row)
            row=dict(header=line[len('Classfile '):],className=None,sourceFile=None,refs=set())
        if row is None:continue
        identity=re.fullmatch(r'\s*this_class:\s*#\d+\s*//\s*([A-Za-z0-9_/$]+)',line)
        if identity:
            if row['className'] is not None:raise ValueError('duplicate class identity')
            row['className']=identity[1]
        source=re.fullmatch(r'SourceFile:\s*"([A-Za-z0-9_$.]+\.java)"',line)
        if source:
            if row['sourceFile'] is not None:raise ValueError('duplicate SourceFile')
            row['sourceFile']=source[1]
        member=re.match(r'^\s*#\d+\s*=\s*(Methodref|InterfaceMethodref|Fieldref)\b.*?//\s*([A-Za-z0-9_/$]+)\.',line)
        if member:row['refs'].add((member[2],member[1]))
        kind=re.match(r'^\s*#\d+\s*=\s*Class\s+.*?//\s*"?([^\s"]+)"?\s*$',line)
        if kind:
            name=kind[1]
            if name.startswith('['):name=name.lstrip('[').removeprefix('L').removesuffix(';')
            if re.fullmatch('[A-Za-z0-9_/$]+',name):row['refs'].add((name,'Class'))
    if row is not None:result.append(row)
    if not result or any(row['className'] is None for row in result):raise ValueError('complete class metadata required')
    if len(result)!=len({row['className'] for row in result}):raise ValueError('duplicate disassembly class')
    return result

def vectors():
    start='Classfile /fixture/p/FixtureTest.class\n  this_class: #1 // p/FixtureTest\n'
    end='SourceFile: "FixtureTest.java"\n'
    samples=[
      ('  #2 = Methodref #3.#4 // p/Target.go:()V\n',True),
      ('  #2 = Fieldref #3.#4 // p/Target.value:I\n',True),
      ('  #2 = Class #3 // p/Target\n',True),
      ('  #2 = String #3 // p/Target\n',False),
      ('  #2 = Utf8 Lp/Target;\n',False),
      ('  #2 = Methodref #3.#4 // other/Target.go:()V\n',False),
      ('  #2 = Methodref #3.#4 // p/TargetOther.go:()V\n',False),
      ('  #2 = InterfaceMethodref #3.#4 // p/Target$Nested.go:()V\n',True)]
    for literal,expected in samples:
        row=parse_metadata(start+literal+end)[0]
        assert any(family(name,'p/Target') for name,_ in row['refs'])==expected
    try:parse_metadata(start+end+end)
    except ValueError:pass
    else:raise AssertionError('duplicate SourceFile accepted')
    return len(samples)+1

def command(label,argv):
    begin=dict(command=argv,startUTC=dt.datetime.now(dt.timezone.utc).isoformat(),environment=ENV)
    write(SLOT/(label+'-begin.safe.json'),begin)
    child=subprocess.Popen(argv,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
    write(SLOT/(label+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=argv,startUTC=begin['startUTC'],cwd=str(SLOT)))
    timed_out=False
    try:stdout,stderr=child.communicate(timeout=180)
    except subprocess.TimeoutExpired:timed_out=True;child.kill();stdout,stderr=child.communicate(timeout=15)
    terminal=dict(actualExit=child.returncode,timedOut=timed_out,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      stdoutBytes=len(stdout),stderrBytes=len(stderr),stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
    write(SLOT/(label+'-exit.safe.json'),terminal)
    if child.returncode!=0:raise ValueError('static disassembly failed; original exit preserved')
    return parse_metadata(stdout.decode()),dict(**begin,**terminal)

def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    compiled_path=BASE/'PG9358-static-companion-compile55-v1/manifest.json'
    assert sha(compiled_path.read_bytes())=='1e6283063e08ae26c4abe5b9cd2d4eb4fce69a45365c4aae14b996641f61d751'
    compiled=json.loads(compiled_path.read_bytes());assert compiled['source']==SOURCE and compiled['actualExit']==0
    assert compiled['selectedTestSourcesStaticallyCompiled']==55 and compiled['freshClassCount']==96
    selected=compiled['begin']['selected55SourceRows'];classes=COMPILE/'fresh-test-classes'
    for path,digest in compiled['freshClassFiles'].items():assert sha((classes/path).read_bytes())==digest
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(normal_path.read_bytes())==compiled['begin']['normalManifestSha256']
    normal=json.loads(normal_path.read_bytes());main_jars=[Path(item['path']) for item in normal['jars'].values()]
    for item in normal['jars'].values():assert sha(Path(item['path']).read_bytes())==item['sha256']
    requested_main=set()
    for row in selected:
        target=row['mainPath'].split('/src/main/java/',1)[1].removesuffix('.java')
        role=row['module'];jar=Path(normal['jars'][role]['path'])
        with zipfile.ZipFile(jar) as archive:
            names={name.removesuffix('.class') for name in archive.namelist() if name.endswith('.class')}
            family_names={name for name in names if family(name,target)}
            assert target in family_names;requested_main.update(family_names)
    os.umask(0o077);SLOT.mkdir();vector_count=vectors()
    javap=str(TC/'jdk-25.0.4/bin/javap')
    test_info,test_receipt=command('fresh-test-metadata',[javap,'-J-Xmx512m','-v','-p',*[str(classes/path) for path in sorted(compiled['freshClassFiles'])]])
    main_info,main_receipt=command('existing-main-source-metadata',[javap,'-J-Xmx512m','-v','-p','-classpath',os.pathsep.join(str(path) for path in main_jars),*[name.replace('/','.') for name in sorted(requested_main)]])
    assert {row['className'] for row in main_info}==requested_main
    main_sources={row['className']:row['sourceFile'] for row in main_info}
    by_source={row['path'].split('/src/test/java/',1)[1]:row for row in selected}
    class_map=[];by_test=defaultdict(list)
    for info in test_info:
        relative=info['className']+'.class';assert relative in compiled['freshClassFiles']
        assert Path(info['header'])==classes/relative
        key=info['className'].rpartition('/')[0]+'/'+str(info['sourceFile'])
        assert key in by_source
        subject=by_source[key];target=subject['mainPath'].split('/src/main/java/',1)[1].removesuffix('.java')
        allowed={name for name in requested_main if family(name,target) and main_sources[name]==Path(subject['mainPath']).name}
        assert target in allowed
        proof=sorted((owner,kind) for owner,kind in info['refs'] if owner in allowed)
        item=dict(classPath=relative,classSha256=compiled['freshClassFiles'][relative],sourceFile=info['sourceFile'],
          className=info['className'],testPath=subject['path'],testSha256=subject['sha256'],mainPath=subject['mainPath'],
          targetInternalName=target,allowedMainFamily=sorted(allowed),javapOwnerReferences=[dict(owner=owner,kind=kind) for owner,kind in proof],
          javapReferenceProved=bool(proof))
        class_map.append(item);by_test[subject['path']].append(item)
    assert len(class_map)==96 and set(by_test)=={row['path'] for row in selected}
    confirmed=sum(any(row['javapReferenceProved'] for row in group) for group in by_test.values())
    for path,digest in compiled['freshClassFiles'].items():assert sha((classes/path).read_bytes())==digest
    assert all(sha((ROOT/row['path']).read_bytes())==row['sha256'] for row in selected)
    verify(invocation);OUT.mkdir();write(OUT/'class-map.json',class_map)
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      compileManifestSha256=sha(compiled_path.read_bytes()),stages=[test_receipt,main_receipt],metadataVectors=vector_count,
      freshClassesMapped=96,sourceFilesMapped=55,javapSourceReferenceCandidates=confirmed,
      classMapSha256=sha((OUT/'class-map.json').read_bytes()),mainFamiliesBySourceFileVerified=True,
      rawDisassemblyPersisted=False,rawLiteralValuesPublished=False,targetRuntimeClassLoading=0,productTestsExecuted=0,
      actualVmActions=0,actualNativeActions=0,coverage=None,newTestIds=0,newMain=0,formalUpdated=False,newAccepted=0,
      wholeG13Accepted=False,whole451Accepted=False,effortPercent=None)
    write(SLOT/'manifest.safe.json',result);write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,freshClasses=96,sourceFiles=55,referenceCandidates=confirmed,metadataVectors=vector_count,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
