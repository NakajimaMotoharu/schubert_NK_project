"""Exact mechanical bulk apply of proven new-only source copies; no runtime deployment."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tarfile
import tempfile
import lan_server

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=W/'pg3694-hygiene-candidate-material-v1'
REMOTE='/home/mini/schubert-nk-pgpt/runs/PG3692-hygiene-candidate-v1'
PRIVATE=False
OCTAL=False


def require(value,reason):
    if not value:raise ValueError(reason)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main_map():return {str(p.relative_to(ROOT)):sha(p)for p in sorted(ROOT.glob('src/*/src/main/java/**/*.java'))}


def verify_generated(names,changes,original):
    paths={'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/'+name for name in names}
    require(len(paths)==70 and paths<=set(original)and not paths&set(changes),'all seventy reproducibly generated artifacts unchanged, no generator alteration required')


def stage():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed source before stage')
    proof=json.loads((W/('pg3726-octal-candidate-v1/manifest.safe.json'if OCTAL else 'pg3720-private-field-candidate-v2/manifest.safe.json'if PRIVATE else 'pg3692-hygiene-candidate-stage-v1/manifest.safe.json')).read_bytes());r=proof['result']
    if OCTAL:
        fixed=json.loads((W/'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes());s=fixed['result']
        require(proof['actualExit']==r['actualExit']==fixed['actualExit']==0 and r['changedFiles']==30 and r['octalIntegerTokens']==187 and r['normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical'],'actual187 exact integer/type semantic proof')
        require(len(r['modules'])==6 and all(m['actualExit']==0 for m in r['modules'].values()),'all6 complete original/candidate literal/binding/ABI proofs')
        require(s['candidateManifestSha256']==r['serverManifestSha256']and s['octalDelta']['actualRawReduction']==187 and s['octalDelta']['onlyOctalRuleChanged']and s['pmd']['processingErrors']==0 and s['pmd']['rawFindings']==1840,'actual187 octal decrease and all other rule counts unchanged')
        r={**r,'checkstyle':s['checkstyle'],'candidateChanges':{p:{'original':v['before'],'candidate':v['candidate']}for p,v in r['changes'].items()},'productionSource':r['baseCandidateSource']}
    if PRIVATE:
        fixed=json.loads((W/'pg3722-private-candidate-static-v1/manifest.safe.json').read_bytes());s=fixed['result']
        require(proof['actualExit']==r['actualExit']==fixed['actualExit']==0 and r['changedFiles']==90 and r['renamedPrivateSymbols']==190 and r['serializedFindingsUnchanged']==63 and r['normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical']and r['allNewFieldsPresentOldFieldsAbsent'],'actual190 private semantic proof')
        require(len(r['modules'])==6 and all(m['verifyExit']==0 for m in r['modules'].values()),'all6 complete final compiler proofs')
        require(s['candidateManifestSha256']==r['serverManifestSha256']and s['privateRenameDelta']['actualRawReduction']==190 and s['privateRenameDelta']['onlyExpectedNamingRulesChanged']and s['pmd']['processingErrors']==0 and s['pmd']['rawFindings']==2027,'exact actual190 decrease without other rule changes')
        r={**r,'checkstyle':s['checkstyle'],'candidateChanges':{p:{'original':v['before'],'candidate':v['candidate']}for p,v in r['changes'].items()},'productionSource':r['baseCandidateSource']}
    require(proof['actualExit']==r['actualExit']==r['checkstyle']['actualExit']==r['checkstyle']['findings']==0 and r['sourceFiles']==849 and r['changedFiles']==(30 if OCTAL else 90 if PRIVATE else 214) and not r['mainApplied'],'actual whole candidate semantic/Checkstyle proof')
    if not(PRIVATE or OCTAL):require(all(x['actualExit']==0 and x['allBindingsAndDeclarationsIdentical']for x in r['modules'].values())and len(r['modules'])==6,'all six semantic source proofs')
    os.umask(0o077);OUT.mkdir();original=main_map();require(len(original)==849,'every Main input')
    changes=r['candidateChanges']
    for name,v in changes.items():require(original.get(name)==v['original']and str(Path(name))==name and '..'not in Path(name).parts and name.startswith('src/schubert-nk-')and '/src/main/java/'in name and name.endswith('.java'),'exact unchanged approved Main path')
    code=r'''
from pathlib import Path
import hashlib,json,tarfile
p=Path(REMOTE);raw=(p/'manifest.safe.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
v=json.loads(raw);assert v['actualExit']==0 and not v['mainApplied']
if not PRIVATE:assert v['checkstyle']['findings']==0
archive=p/ARCHIVE
with tarfile.open(archive,'x:gz')as t:
 for name,item in sorted(v['changes'if PRIVATE else 'candidateChanges'].items()):
  path=p/'candidate'/name;assert not path.is_symlink()and hashlib.sha256(path.read_bytes()).hexdigest()==item['candidate'];t.add(path,arcname=name,recursive=False)
print(json.dumps({'actualExit':0,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'files':len(v['changes'if PRIVATE else 'candidateChanges'])}))
'''
    archive_name='candidate-'+str(len(changes))+'-source.tar.gz'
    payload='EXPECTED='+repr(r['serverManifestSha256'])+'\nREMOTE='+repr(REMOTE)+'\nPRIVATE='+repr(PRIVATE or OCTAL)+'\nARCHIVE='+repr(archive_name)+'\n'+code
    # Only a derived source archive is written in the existing isolated candidate directory.
    command='python3 -c '+shlex.quote(payload)
    rc,output=lan_server.run(command,timeout=45);(OUT/'archive.safe.log').write_text(output);require(rc==0,'new exact derived candidate archive')
    archive_info=json.loads(next(x for x in output.splitlines()if x.startswith('{')))
    key=lan_server.pinned_key()
    with tempfile.TemporaryDirectory(prefix='pgpt-hygiene-pinned-')as directory:
        known=Path(directory)/'known_hosts';known.write_text(key+'\n');known.chmod(0o600)
        shell=shlex.join(['ssh',*lan_server.ssh_options(known)])
        rc,output=lan_server.authenticated(['rsync','-a','--partial','--stats','--secluded-args','-e',shell,f'mini@{lan_server.HOST}:{REMOTE}/{archive_name}',str(OUT/'candidate.tar.gz')],known,120)
    (OUT/'transfer.private.log').write_text(output);archive=OUT/'candidate.tar.gz';require(rc==0 and sha(archive)==archive_info['archiveSha256'],'complete immutable source archive receive')
    candidate=OUT/'candidate';candidate.mkdir();patch=[]
    with tarfile.open(archive)as t:
        members=t.getmembers();require(len(members)==len(changes)and {x.name for x in members}==set(changes)and all(x.isfile()and not x.issym()and not x.islnk()for x in members),'exact regular source files only')
        t.extractall(candidate,filter='data')
    for name,v in sorted(changes.items()):
        require(sha(candidate/name)==v['candidate'],'every proven candidate source byte')
        patch.extend(difflib.unified_diff((ROOT/name).read_text().splitlines(keepends=True),(candidate/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    (OUT/'candidate.patch').write_text(''.join(patch));require(original==main_map(),'all Main unchanged throughout stage')
    subprocess.run(['git','apply','--check',str(OUT/'candidate.patch')],cwd=ROOT,check=True)
    generated=json.loads((ROOT/'evidence/01_PT/006_NK-MSG-002/evidence/quality/generation-results.json').read_bytes())
    verify_generated(set(generated['generatedSha256']),changes,original)
    value={'actualExit':0,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'baseProductionSource':r['productionSource'],'originalAll849Sha256':original,'changes':changes,'patchSha256':sha(OUT/'candidate.patch'),'archive':archive_info,'candidateManifestSha256':r['serverManifestSha256'],'checkstyleFindings':0,'allSixBindingsAndDeclarationsIdentical':True,'seventyGeneratedFilesUnchanged':True,'applied':False,'vmOperations':0}
    with(OUT/'stage.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({'actualExit':0,'stagedMainFiles':len(changes),'checkstyleFindings':0,'allGenerated70Unchanged':True,'mainApplied':False}));return 0


def apply():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed source before one mechanical apply')
    v=json.loads((OUT/'stage.safe.json').read_bytes());require(v['actualExit']==0 and v['operatorHead']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'exact staged operator')
    require(v['originalAll849Sha256']==main_map()and sha(OUT/'candidate.patch')==v['patchSha256'],'all current source and patch still exact')
    for p,x in v['changes'].items():require(sha(OUT/'candidate'/p)==x['candidate'],'all214 new proven bytes')
    subprocess.run(['git','apply','--check',str(OUT/'candidate.patch')],cwd=ROOT,check=True)
    count=len(v['changes']);require(count==(30 if OCTAL else 90 if PRIVATE else 214),'exact configured delta count')
    with(OUT/'apply-intent.safe.json').open('x')as f:json.dump({'patchSha256':v['patchSha256'],'files':count,'originalHead':v['operatorHead'],'vmOperations':0},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    subprocess.run(['git','apply',str(OUT/'candidate.patch')],cwd=ROOT,check=True)
    expected={**v['originalAll849Sha256'],**{p:x['candidate']for p,x in v['changes'].items()}}
    require(main_map()==expected,'all849 source bytes, only exact214 candidates applied')
    changed=set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines());require(changed==set(v['changes']),'no unapproved path changed')
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    with(OUT/'apply.safe.json').open('x')as f:json.dump({'actualExit':0,'applied':True,'changedMainFiles':count,'all849Exact':True,'candidateManifestSha256':v['candidateManifestSha256'],'runtimeDeployment':False,'wholeAndNativePending':True},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'appliedMainFiles':count,'runtimeDeployed':False,'wholeAndNativePending':True}));return 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply']);group=p.add_mutually_exclusive_group();group.add_argument('--private190',action='store_true');group.add_argument('--octal187',action='store_true');args=p.parse_args()
    if args.private190:
        PRIVATE=True;OUT=W/'pg3724-private-candidate-material-v1';REMOTE='/home/mini/schubert-nk-pgpt/runs/PG3720-private-field-candidate-v2'
    if args.octal187:
        OCTAL=True;OUT=W/'pg3732-octal-candidate-material-v1';REMOTE='/home/mini/schubert-nk-pgpt/runs/PG3726-octal-candidate-v1'
    raise SystemExit({'stage':stage,'apply':apply}[args.action]())
