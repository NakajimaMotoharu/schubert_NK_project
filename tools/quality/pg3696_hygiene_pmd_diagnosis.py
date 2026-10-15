"""Fixed PMD on exact applied hygiene source; static-only, no repeated PT or VM action."""
import hashlib
import inspect
import json
import os
import shlex
import subprocess
from pg3688_import_candidate_stage import ROOT,W,BASE,require
from lan_server import copy,run
from git_source_contract import last_main_source


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E

    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/('runs/'+data.get('staticJob','PG3696-hygiene-pmd-v1'));candidate=b/('runs/'+data.get('candidateJob','PG3692-hygiene-candidate-v1')+'/candidate');out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    stage=candidate.parent/'manifest.safe.json';require(sha(stage)==data['candidateManifestSha256'],'actual all849 Checkstyle0/binding proof')
    files=sorted(candidate.glob('src/*/src/main/java/**/*.java'));actual={str(p.relative_to(candidate)):sha(p)for p in files};require(len(actual)==849 and actual==data['sourceSha256'],'exact applied current source bytes, not relabelled old inputs')
    fixed=json.loads((b/'runs/PG3382-static-gate-v1/result/manifest.safe.json').read_bytes());old_path=b/'runs/PG3422-candidate-static-v1/manifest.safe.json';require(sha(old_path)==data['originalStaticManifestSha256'],'actual original fixed diagnostic')
    old=json.loads(old_path.read_bytes());rules=b/'runs/PG3382-static-gate-v1/result/source/tools/quality/static';require(all(sha(rules/n)==h for n,h in old['ruleSha256'].items()),'all category rules unchanged')
    for p,h in old['auxJarSha256'].items():require(sha(Path(p))==h,'all original typed auxiliaries fixed')
    overlay=b/'runs/PG3386-pmd-record-after-v1/pmd-record-1298.jar';require(sha(overlay)==old['recordOverlaySha256'],'exact existing Java25 record fix, no suppression')
    distribution=b/'runs/PG3382-static-gate-v1/pmd-dist-7.28.0-bin.zip';require(sha(distribution)==old['pinnedToolSha256']['pmd-dist-7.28.0-bin.zip'],'original pinned PMD7.28.0')
    listing=out/'all-java.txt';listing.write_text(''.join(str(p)+'\n'for p in files));aux=out/'aux-classpath.txt';aux.write_text('\n'.join(old['auxJarSha256'])+'\n')
    argv=list(fixed['pmd']['argv']);argv[2]=str(overlay)+':'+argv[2];argv[argv.index('--file-list')+1]=str(listing);argv[argv.index('--aux-classpath')+1]='file:'+str(aux);argv[argv.index('--report-file')+1]=str(out/'pmd.xml')
    env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'productionCandidateSource':data['source'],'sourceSnapshot':data['head'],'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'startUTC':start,'command':argv,'vmActions':0}))
    with(out/'pmd.private.log').open('xb')as log:r=subprocess.run(argv,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    root=E.parse(out/'pmd.xml').getroot();findings=root.findall('.//{*}violation');errors=root.findall('.//{*}error');require(not errors and r.returncode==(4 if findings else 0),'actual findings and processing errors separated, no false pass')
    counts=dict(Counter(v.get('rule')for v in findings));oldcounts=old['results']['pmd']['ruleCounts'];rule_delta={k:counts.get(k,0)-oldcounts.get(k,0)for k in set(counts)|set(oldcounts)if counts.get(k,0)!=oldcounts.get(k,0)}
    require(actual=={str(p.relative_to(candidate)):sha(p)for p in files}and all(sha(Path(p))==h for p,h in old['auxJarSha256'].items()),'all source and typed auxiliary inputs stable')
    value={'actualExit':0,'productionCandidateSource':data['source'],'sourceSnapshot':data['head'],'sourceFiles':849,'candidateManifestSha256':data['candidateManifestSha256'],'pmd':{'actualExit':r.returncode,'processingErrors':len(errors),'rawFindings':len(findings),'ruleCounts':counts,'ruleCountDeltaFrom3422':rule_delta,'reportSha256':sha(out/'pmd.xml'),'logSha256':sha(out/'pmd.private.log')},'ruleSha256':old['ruleSha256'],'pinnedToolSha256':old['pinnedToolSha256'],'all849AppliedSourceExact':True,'wholeTypedBindingEquivalenceRef':'PG3690/3692 all six actual compiler proofs','auxMeaning':'Original current4856 typed auxiliaries only for semantic-equivalent static diagnostic; NOT new source Main build/native/coverage acceptance','inputsUnchanged':True,'rulesSuppressed':False,'F03Accepted':False,'staticGatePassed':not findings,'formalAccepted':False,'vmActions':0,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if data.get('includeCheckstyle'):
        proof=json.loads(stage.read_bytes())
        octal=data.get('semanticKind')=='OCTAL_EXPLICIT_BASE'
        if octal:
            require(proof['actualExit']==0 and proof['octalIntegerTokens']==187 and proof['changedFiles']==30 and proof['normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical']and all(m['actualExit']==0 for m in proof['modules'].values()),'actual full6 exact integer value/type proof')
        else:require(proof['actualExit']==0 and proof['renamedPrivateSymbols']==190 and proof['changedFiles']==90 and proof['serializedFindingsUnchanged']==63 and proof['normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical']and proof['allNewFieldsPresentOldFieldsAbsent']and all(m['verifyExit']==0 for m in proof['modules'].values()),'actual full6 private-only positive semantic proof')
        rule=rules/'checkstyle.xml';jar=b/'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar';require(sha(rule)==old['ruleSha256']['checkstyle.xml']and sha(jar)==old['pinnedToolSha256']['checkstyle-14.3.0-all.jar'],'same exact fixed Checkstyle rule/tool')
        cmd=list(fixed['checkstyle']['argv']);cmd[cmd.index('-c')+1]=str(rule);cmd[cmd.index('-o')+1]=str(out/'checkstyle.xml');cmd[-1]='@'+str(listing)
        c=subprocess.run(cmd,capture_output=True,timeout=90);(out/'checkstyle.private.log').write_bytes(c.stdout+c.stderr);cs=E.parse(out/'checkstyle.xml').getroot().findall('.//error');require(c.returncode==len(cs)%256,'genuine fixed Checkstyle exit')
        value['checkstyle']={'actualExit':c.returncode,'findings':len(cs),'reportSha256':sha(out/'checkstyle.xml')};value['mainApplied']=False;value['all849AppliedSourceExact']=False;value['all849IsolatedCandidateExact']=True;value['wholeTypedBindingEquivalenceRef']=data['candidateJob']+' all6 final normalized actual declarations/type/bounds/capture-identity/tree/literal/public ABI'
        if octal:
            base=b/'runs/PG3722-private-candidate-static-v1/manifest.safe.json';require(sha(base)==data['baseStaticManifestSha256'],'original current private190 fixed diagnostic');baseproof=json.loads(base.read_bytes());basecounts=baseproof['pmd']['ruleCounts'];delta={k:counts.get(k,0)-basecounts.get(k,0)for k in set(counts)|set(basecounts)if counts.get(k,0)!=basecounts.get(k,0)}
            value['octalDelta']={'actualRawReduction':baseproof['pmd']['rawFindings']-len(findings),'onlyOctalRuleChanged':set(delta)=={'AvoidUsingOctalValues'},'ruleCountDeltaFromBase':delta,'allSourceSha256':actual,'candidateManifestSha256':sha(stage)}
        else:value['privateRenameDelta']={'actualRawReduction':old['results']['pmd']['violations']-len(findings),'onlyExpectedNamingRulesChanged':set(rule_delta)<={'AvoidFieldNameMatchingMethodName','AvoidFieldNameMatchingTypeName'},'allSourceSha256':actual,'candidateManifestSha256':sha(stage)}
        require(all(sha(p)==actual[str(p.relative_to(candidate))]for p in files),'all849 byte unchanged through both analyzers')
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean applied source and fixed operator')
    applied=json.loads((W/'pg3694-hygiene-candidate-material-v1/apply.safe.json').read_bytes());require(applied['actualExit']==0 and applied['applied'],'actual214 mechanical apply')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();source=last_main_source(ROOT)
    staged=json.loads((W/'pg3692-hygiene-candidate-stage-v1/manifest.safe.json').read_bytes());old=W/'pg3422-candidate-static-v1/manifest.safe.json'
    data={'head':head,'source':source,'candidateManifestSha256':staged['result']['serverManifestSha256'],'originalStaticManifestSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ROOT.glob('src/*/src/main/java/**/*.java'))}}
    os.umask(0o077);out=W/'pg3696-hygiene-pmd-diagnosis-v1';out.mkdir();payload='\n'.join(inspect.getsource(x)for x in [require,server])+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';compile(payload,'<exact candidate all849 fixed PMD>','exec');script=out/'pmd.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3696-hygiene-pmd-v1 && mkdir -m700 '+BASE+'/transfer/PG3696-hygiene-pmd-v1',timeout=30);require(rc==0,'new-only static scope')
    rc,_=copy(script,BASE+'/transfer/PG3696-hygiene-pmd-v1/',timeout=60);require(rc==0,'fixed static-only payload')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3696-hygiene-pmd-v1/pmd.private.py'),timeout=240);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionCandidateSource':source,'operatorSource':head,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return rc


if __name__=='__main__':raise SystemExit(main())
