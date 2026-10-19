"""All current typed catch/approved JDBC shape facts only; no static-rule exemption."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from source_catch_context_inventory_test import facts as catch_facts
from source_jdbc_close_precedence_inventory_test import facts as jdbc_facts
from pg5584_field_accessor_inspection import compile_only_artifacts,JDK
from pg5590_current_static_projection import SOURCE,ROOT,W,BASE,load_fixed,PREPARED

SLOT='pg5592-current-failure-facts-v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def inputs():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('same fixed canonical source')
    field=load_fixed(*PREPARED['fields']);mirror=W/'pg5584-field-accessor-v2/input'
    current={p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    mirrored={p.relative_to(mirror).as_posix():sha(p.read_bytes())for p in mirror.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=849 or current!=mirrored or current!=field['all849SourceHashes']:raise ValueError('every actual current Main and preserved analysis mirror identical, no old result import')
    selected_path=W/'pg5566-private-monitor-green-v3/manifest.safe.json';blob=selected_path.read_bytes()
    if sha(blob)!='9eef40acd5388ebf53737907bb5d664cf60a38430894de07a4a56df31896ca73':raise ValueError('current actual selected73 qualification')
    selected=json.loads(blob)
    if selected['sourceSnapshot']!=SOURCE or selected['actualExit']!=0 or selected['actualCases']!=73:raise ValueError('current selected source, no new whole claim')
    roots=[selected_path.parent/'source'/('src/schubert-nk-'+m+'/target/classes')for m in('protocol','storage','bootstrap','api','web','batch')]
    actual={root.parts[-3].removeprefix('schubert-nk-')+':'+p.relative_to(root).as_posix():sha(p.read_bytes())for root in roots for p in root.rglob('*.class')}
    if len(actual)!=1664 or actual!=selected['physicalMain']['sha256']:raise ValueError('all1664 actual current selected classpath unchanged')
    release=W/'pg5430-release-v1';bom=(release/'RELEASE-MANIFEST.json').read_bytes()
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('immutable third-party inventory authority')
    jars={}
    for row in json.loads(bom)['artifacts']:
        path=row['path']
        if '/lib/'not in path or not path.endswith('.jar')or Path(path).name.startswith('schubert-nk-'):continue
        target=release/path
        if target.is_symlink()or sha(target.read_bytes())!=row['sha256']:raise ValueError('every third-party dependency actual bytes')
        jars.setdefault(row['sha256'],target)
    provided,metadata=compile_only_artifacts()
    paths=[*roots,*jars.values(),*provided]
    tools={name:sha((ROOT/'tools/quality'/name).read_bytes())for name in('SourceCatchContextInventory.java','SourceJdbcClosePrecedenceInventory.java')}
    return mirror,os.pathsep.join(map(str,paths)),{'sourceHashes':current,'physicalMainSha256':actual,'thirdPartyJarSha256':list(jars),'compileOnlyArtifacts':metadata,'helperSha256':tools,'selectedManifestSha256':sha(blob)}


def main():
    mirror,classpath,identity=inputs();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    compile_command=[str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),*[str(ROOT/'tools/quality'/n)for n in identity['helperSha256']]]
    with(out/'compile.private.log').open('xb')as f:compiled=subprocess.run(compile_command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
    if compiled.returncode:raise ValueError('both compiler fact tools lint0 before inspection')
    results={}
    for name,parser in(('SourceCatchContextInventory',catch_facts),('SourceJdbcClosePrecedenceInventory',jdbc_facts)):
        command=[str(JDK/'java'),'-Xmx1536m','-cp',str(classes),name,str(mirror),classpath]
        result=subprocess.run(command,capture_output=True,text=True,timeout=180)
        with(out/(name+'.private.log')).open('x')as f:f.write(result.stdout+result.stderr);f.flush();os.fsync(f.fileno())
        if result.returncode:raise ValueError('every current source/type must resolve; preserve failure, no retry overwrite')
        rows=parser(result.stdout)
        if any(r['path']not in identity['sourceHashes']for r in rows):raise ValueError('only exact current source files')
        results[name]={'actualExit':result.returncode,'command':command,'rows':rows,'outputSha256':sha(result.stdout.encode())}
    if inputs()!=(mirror,classpath,identity):raise ValueError('all source/classes/tools/type dependencies remain fixed')
    value={'actualExit':0,'source':SOURCE,'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compileCommand':compile_command,
        'identity':identity,'results':results,'catchSites':len(results['SourceCatchContextInventory']['rows']),'exactJdbcCloseShapes':len(results['SourceJdbcClosePrecedenceInventory']['rows']),
        'actualWholeClaimed':False,'sourceSymbolsAreNotTestSuccess':True,'dispositions':'FACTS_ONLY_PENDING_ORIGINAL_DIAGNOSTIC_AND_CURRENT_WHOLE_BINDING',
        'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'productionChanges':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','source','catchSites','exactJdbcCloseShapes','F03Accepted','actualWholeClaimed')}|{'manifestSha256':sha((out/'manifest.safe.json').read_bytes())}))


if __name__=='__main__':main()
