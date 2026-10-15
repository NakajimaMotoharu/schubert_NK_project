"""New-only declaration/TAB candidates, fixed format/Checkstyle and all semantic bindings."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from pg3688_import_candidate_stage import ROOT,W,SOURCE,BASE,require
from source_import_expansion_test import parse


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E

    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');prior=b/'runs/PG3690-import-candidate-v1';out=b/'runs/PG3692-hygiene-candidate-v1';transfer=b/'transfer/PG3692-hygiene-candidate-v1'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require(sha(prior/'manifest.safe.json')==data['priorManifestSha256'],'qualified exact import candidate manifest')
    old=json.loads((prior/'manifest.safe.json').read_bytes());require(old['actualExit']==0 and old['candidateOnly']and old['wildcardImportsExpanded']==531,'all six immutable import probes')
    original=prior/'original';imported=prior/'candidate';sources=sorted(original.glob('src/*/src/main/java/**/*.java'))
    require(len(sources)==849 and {str(p.relative_to(original)):sha(p)for p in sources}==data['sourceSha256'],'all original Main byte unchanged')
    for p in sources:
        rel=str(p.relative_to(original));expected=old['changed'].get(rel,{}).get('candidate',data['sourceSha256'][rel]);require(sha(imported/rel)==expected,'exact imported candidate inputs')
    out.mkdir();(out/'tool-classes').mkdir();java=b/'tools/jdk-25.0.4/bin/java';javac=b/'tools/jdk-25.0.4/bin/javac';candidate=out/'candidate'
    for name,digest in data['toolSha256'].items():require(sha(transfer/name)==digest,'fixed source tooling '+name)
    r=subprocess.run([str(javac),'-Xlint:all','-Werror','-d',str(out/'tool-classes'),str(transfer/'SourceImportExpansion.java'),str(transfer/'SourceDeclarationExpansion.java'),str(transfer/'IsolatedSourceOutput.java')],capture_output=True,timeout=30)
    (out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'both compiler tools lint0')
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'startUTC':start,'productionSource':data['source'],'sourceSnapshot':data['head'],'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'MainApplied':False,'vmActions':0}))
    argv=[str(java),'-Xmx1536m','-cp',str(out/'tool-classes'),'SourceDeclarationExpansion',str(imported),str(candidate)]
    r=subprocess.run(argv,capture_output=True,text=True,timeout=90);(out/'declarations.safe.tsv').write_text(r.stdout);(out/'declarations.private.log').write_text(r.stderr);require(r.returncode==0,'parse-only candidate must terminate0')
    counts={'groups':0,'variables':0,'literalTabs':0,'heldGroups':0};declaration_files=[]
    for line in r.stdout.splitlines():
        fields=line.split('\t');require(len(fields)==6 and fields[0]=='CANDIDATE','exact candidate coordinates')
        declaration_files.append(fields[1])
        for key,value in zip(counts,fields[2:]):counts[key]+=int(value)
    formatter=transfer/'google-java-format-1.36.1-all-deps.jar'
    format_argv=[str(java),'-Xmx1536m','-jar',str(formatter),'--skip-reflowing-long-strings','--replace',*map(str,sorted(candidate.glob('src/*/src/main/java/**/*.java')))]
    r=subprocess.run(format_argv,capture_output=True,timeout=120);(out/'format.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'fixed Spotless-compatible GJF0')
    modules={}
    for module,item in old['modules'].items():
        before=prior/(module+'-after.bindings.safe.tsv');require(sha(before)==item['phases']['after']['bindingTsvSha256'],'exact prior semantic proof')
        expected=parse(before.read_text());argv=list(item['phases']['after']['command']);require(argv[4]=='SourceImportExpansion'and argv[5]==str(imported/('src/schubert-nk-'+module+'/src/main/java')),'actual known compiler tuple')
        cp=argv[-1]
        def cp_hash():
            result={}
            for p in map(Path,cp.split(':')):
                require(p.is_absolute()and p.exists(),'all exact original classpath inputs')
                result[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
            return hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
        require(cp_hash()==item['classpathInputsSha256'],'every actual previous qualified classpath byte')
        argv[3]=str(out/'tool-classes');argv[5]=str(candidate/('src/schubert-nk-'+module+'/src/main/java'))
        r=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/(module+'-after.bindings.safe.tsv')).write_text(r.stdout);(out/(module+'-after.private.log')).write_text(r.stderr);require(r.returncode==0,'new actual candidate semantic analysis0')
        actual=parse(r.stdout);require(actual.keys()==expected.keys(),'same full compilation units')
        for name in expected:require(actual[name]['binding']==expected[name]['binding']and actual[name]['declarations']==expected[name]['declarations']and not actual[name]['imports'],'all member/type/constructor bindings and declaration/literal values identical')
        require(cp_hash()==item['classpathInputsSha256'],'classpath inputs unchanged after new candidate')
        modules[module]={'sourceFiles':len(actual),'allBindingsAndDeclarationsIdentical':True,'bindingTsvSha256':sha(out/(module+'-after.bindings.safe.tsv')),'actualExit':r.returncode}
        (out/'progress.safe.json').write_text(json.dumps({'modulesVerified':list(modules),'counts':counts,'mainApplied':False}))
    fixed=json.loads((b/'runs/PG3382-static-gate-v1/result/manifest.safe.json').read_bytes());jar=b/'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar';require(sha(jar)==data['checkstyleJarSha256']and sha(transfer/'checkstyle.xml')==data['checkstyleRuleSha256'],'same pinned Checkstyle and every rule')
    listing=out/'all-java.txt';listing.write_text(''.join(str(p)+'\n'for p in sorted(candidate.glob('src/*/src/main/java/**/*.java'))));argv=list(fixed['checkstyle']['argv']);argv[argv.index('-c')+1]=str(transfer/'checkstyle.xml');argv[argv.index('-o')+1]=str(out/'checkstyle.xml');argv[-1]='@'+str(listing)
    r=subprocess.run(argv,capture_output=True,timeout=90);(out/'checkstyle.private.log').write_bytes(r.stdout+r.stderr)
    findings=E.parse(out/'checkstyle.xml').getroot().findall('.//error');require(r.returncode==len(findings)%256,'genuine Checkstyle exit/findings agree')
    changed={}
    for p in sources:
        rel=str(p.relative_to(original));actual=sha(candidate/rel)
        if actual!=data['sourceSha256'][rel]:changed[rel]={'original':data['sourceSha256'][rel],'candidate':actual}
    require({str(p.relative_to(original)):sha(p)for p in sources}==data['sourceSha256'],'all original sources immutable')
    value={'actualExit':0,'productionSource':data['source'],'sourceSnapshot':data['head'],'sourceFiles':849,'wildcardImportsResolved':531,'candidateChanges':changed,'changedFiles':len(changed),'declarationCounts':counts,'declarationFiles':declaration_files,'modules':modules,'checkstyle':{'actualExit':r.returncode,'findings':len(findings),'ruleCounts':dict(Counter(x.get('source')for x in findings)),'reportSha256':sha(out/'checkstyle.xml'),'ruleSha256':data['checkstyleRuleSha256'],'toolSha256':data['checkstyleJarSha256']},'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mainApplied':False,'vmActions':0,'formalAccepted':False,'PMDRawUnreclassified':2217,'wholeAndNativePending':True}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed operator')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();prior=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes());require(prior['actualExit']==0,'actual original import stage0')
    static=json.loads((W/'pg3422-candidate-static-v1/manifest.safe.json').read_bytes());rule=ROOT/'tools/quality/static/checkstyle.xml'
    tools=[ROOT/'tools/quality/SourceImportExpansion.java',ROOT/'tools/quality/SourceDeclarationExpansion.java',ROOT/'tools/quality/IsolatedSourceOutput.java',Path('/home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar'),rule]
    require(hashlib.sha256(rule.read_bytes()).hexdigest()==static['ruleSha256']['checkstyle.xml'],'all existing fixed rules unchanged')
    data={'head':head,'source':SOURCE,'priorManifestSha256':prior['result']['serverManifestSha256'],'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ROOT.glob('src/*/src/main/java/**/*.java'))},'toolSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in tools},'checkstyleJarSha256':static['pinnedToolSha256']['checkstyle-14.3.0-all.jar'],'checkstyleRuleSha256':static['ruleSha256']['checkstyle.xml']}
    os.umask(0o077);out=W/'pg3692-hygiene-candidate-stage-v1';out.mkdir();payload='\n'.join(inspect.getsource(x)for x in [require,parse,server])+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';compile(payload,'<staged syntax-preserving hygiene>','exec');script=out/'hygiene.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3692-hygiene-candidate-v1 && mkdir -m700 '+BASE+'/transfer/PG3692-hygiene-candidate-v1',timeout=30);require(rc==0,'new-only hygiene stage')
    for p in [*tools,script]:
        rc,_=copy(p,BASE+'/transfer/PG3692-hygiene-candidate-v1/',timeout=60);require(rc==0,'fixed new stage input transfer')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3692-hygiene-candidate-v1/hygiene.private.py'),timeout=1200);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionSource':SOURCE,'sourceSnapshot':head,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if not rc:print(json.dumps({k:v for k,v in value['result'].items()if k not in {'modules','candidateChanges','declarationFiles'}}))
    return rc


if __name__=='__main__':raise SystemExit(main())
