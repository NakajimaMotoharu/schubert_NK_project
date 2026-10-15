"""Read-only actual compiler bindings, new-only candidate copies; no Production/VM mutation."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from source_import_expansion_test import parse,replace_imports

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
BASE='/home/mini/schubert-nk-pgpt'


def require(value,reason):
    if not value:raise ValueError(reason)


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import shutil
    import subprocess
    import tarfile
    import xml.etree.ElementTree as E

    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3688-import-candidate-v1';original=out/'original';candidate=out/'candidate'
    require(shutil.disk_usage(b).free>12*1024**3,'capacity before isolated compiler copies')
    out.mkdir();original.mkdir();candidate.mkdir();(out/'tool-classes').mkdir()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    transfer=b/'transfer/PG3688-import-candidate-v1';archive=transfer/'source.tar'
    require(sha(archive)==data['archiveSha256'],'actual fixed archive')
    with tarfile.open(archive)as t:t.extractall(original,filter='data')
    files=sorted(original.glob('src/*/src/main/java/**/*.java'));require(len(files)==849,'all Production Java')
    require({str(p.relative_to(original)):sha(p)for p in files}==data['sourceSha256'],'all Main exact current source')
    for p in files:
        target=candidate/p.relative_to(original);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    tool=transfer/'SourceImportExpansion.java';require(sha(tool)==data['toolSha256'],'fixed compiler probe')
    java=b/'tools/jdk-25.0.4/bin/java';javac=b/'tools/jdk-25.0.4/bin/javac'
    command=[str(javac),'-Xlint:all','-Werror','-d',str(out/'tool-classes'),str(tool)]
    r=subprocess.run(command,capture_output=True,timeout=30);(out/'probe-compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'actual compiler probe full lint0')
    full=b/'runs/PG3412-six-v1/manifest.safe.json';require(sha(full)==data['fullManifestSha256'],'actual original3712 full')
    modules={};all_changed={};all_replacements=0;start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out/'begin.safe.json').write_text(json.dumps({'startUTC':start,'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'sourceSnapshot':data['head'],'productionSource':data['source'],'archiveSha256':data['archiveSha256'],'scope':'READONLY_ORIGINAL_AND_NEW_ONLY_CANDIDATES','vmActions':0}))
    for module,item in data['modules'].items():
        xml_name=sorted(item['xmlHashes'])[0];xml=b/('source-full-PG3412/src/schubert-nk-'+module+'/target/surefire-reports')/xml_name
        require(sha(xml)==item['xmlHashes'][xml_name],'genuine qualified module classpath XML')
        cp=E.parse(xml).getroot().find("./properties/property[@name='java.class.path']").get('value')
        def classpath_hashes():
            result={}
            for raw_path in cp.split(os.pathsep):
                path=Path(raw_path);require(path.is_absolute()and path.exists(),'qualified classpath path')
                if path.is_dir():result[str(path)]={str(p.relative_to(path)):sha(p)for p in path.rglob('*')if p.is_file()}
                else:result[str(path)]=sha(path)
            return result
        cp_before=classpath_hashes();phase={};parsed={}
        for name,root in [('before',original),('after',candidate)]:
            scope=root/('src/schubert-nk-'+module+'/src/main/java')
            argv=[str(java),'-Xmx1536m','-cp',str(out/'tool-classes'),'SourceImportExpansion',str(scope),cp]
            actual=subprocess.run(argv,capture_output=True,text=True,timeout=180)
            (out/(module+'-'+name+'.bindings.safe.tsv')).write_text(actual.stdout)
            (out/(module+'-'+name+'.private.log')).write_text(actual.stderr)
            require(actual.returncode==0,'actual '+module+' '+name+' compiler bindings0')
            phase[name]={'actualExit':actual.returncode,'command':argv,'bindingTsvSha256':sha(out/(module+'-'+name+'.bindings.safe.tsv'))}
            parsed[name]=parse(actual.stdout)
            if name=='before':
                for relative,entry in parsed[name].items():
                    source=scope/relative;target=candidate/source.relative_to(original);raw=source.read_text()
                    changed=replace_imports(raw,entry['imports'])
                    if changed!=raw:
                        target.write_text(changed);all_replacements+=len(entry['imports'])
                        all_changed[str(source.relative_to(original))]={'before':sha(source),'candidate':sha(target),'imports':len(entry['imports'])}
        require(parsed['before'].keys()==parsed['after'].keys(),'same all module compilation units')
        for name in parsed['before']:
            before,after=parsed['before'][name],parsed['after'][name]
            require(before['binding']==after['binding']and before['declarations']==after['declarations']and not after['imports'],'every resolved binding and non-import declaration/literal unchanged')
        require(cp_before==classpath_hashes(),'every qualified classpath input stable')
        modules[module]={'phases':phase,'sourceFiles':len(parsed['before']),'qualifiedClasspathXmlSha256':item['xmlHashes'][xml_name],'classpathInputsSha256':hashlib.sha256(json.dumps(cp_before,sort_keys=True).encode()).hexdigest(),'allBindingsAndDeclarationsIdentical':True}
    require(all_replacements==531 and len(all_changed)>0,'all original531 wildcard declarations handled')
    require({str(p.relative_to(original)):sha(p)for p in files}==data['sourceSha256'],'original immutable after all compiler analysis')
    value={'actualExit':0,'productionSource':data['source'],'sourceSnapshot':data['head'],'sourceArchiveSha256':data['archiveSha256'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceFiles':849,'wildcardImportsExpanded':all_replacements,'changedFiles':len(all_changed),'changed':all_changed,'modules':modules,'originalsUnchanged':True,'candidateOnly':True,'mainApplied':False,'newAuthority':False,'vmActions':0,'formalAccepted':False,'fixedCheckstylePending':True,'multipleDeclarationsPending':True,'literalTabPending':True,'wholeRegressionPending':True}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed tool/source snapshot')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    full=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes());f=full['result']
    require(full['actualExit']==0 and f['tests']==3712 and f['productionSource']==SOURCE,'actual fixed baseline')
    require(not subprocess.check_output(['git','diff',f['sourceSnapshot'],head,'--','src/*/src/main'],cwd=ROOT),'all Main unchanged before staging')
    os.umask(0o077);out=W/'pg3688-import-candidate-stage-v1';out.mkdir()
    archive=out/'source.tar';archive.write_bytes(subprocess.check_output(['git','archive','--format=tar',head,'src'],cwd=ROOT))
    tool=ROOT/'tools/quality/SourceImportExpansion.java'
    data={'head':head,'source':SOURCE,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'toolSha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ROOT.glob('src/*/src/main/java/**/*.java'))},'fullManifestSha256':f['serverManifestSha256'],'modules':f['modules']}
    payload='\n'.join(inspect.getsource(x)for x in [require,parse,replace_imports,server])+'\nserver('+repr(data)+')\n';compile(payload,'<new-only import candidates>','exec')
    script=out/'candidate.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3688-import-candidate-v1 && mkdir -m700 '+BASE+'/transfer/PG3688-import-candidate-v1',timeout=30);require(rc==0,'unique finite stage namespace')
    for p in [archive,script,tool]:
        rc,_=copy(p,BASE+'/transfer/PG3688-import-candidate-v1/',timeout=60);require(rc==0,'fixed candidate tool/source transfer')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3688-import-candidate-v1/candidate.private.py'),timeout=1200)
    (out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionSource':SOURCE,'sourceSnapshot':head,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalUpdated':False}
    if rc==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if not rc:print(json.dumps({k:v for k,v in value['result'].items()if k not in {'changed','modules'}}))
    return rc


if __name__=='__main__':raise SystemExit(main())
