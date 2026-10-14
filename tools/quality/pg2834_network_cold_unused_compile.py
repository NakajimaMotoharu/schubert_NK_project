"""Host-only new-only bundle and current ABI freeze. No VM mutation."""
import datetime
import hashlib
import json
import os
import subprocess
import tarfile
import pg1442_current_cold_compile as compiler
from pg1446_current_cold_stage import W,P
from pg601_stage_contract import check_members
import pg2832_network_cold_unused_sources as s

FROZEN='pg2834-network-cold-unused-frozen-v1.safe.json'


def main():
    s.qualify();os.umask(0o077)
    require=lambda v:None if v else (_ for _ in ()).throw(ValueError('fixed unused compiler input refused'))
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=compiler.ROOT))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=compiler.ROOT,text=True).strip()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    out=W/s.TOOLS;out.mkdir(mode=0o700)
    release=W/'pg2802-release-v1';raw=(release/'RELEASE-MANIFEST.json').read_bytes();data=json.loads(raw)
    require(hashlib.sha256(raw).hexdigest()==s.DIGEST and data['source']['commit']==s.CANDIDATE
        and data['release']=='0.1.0-PG2802' and len(data['artifacts'])==187 and len(data['migrations'])==29)
    for row in data['artifacts']:
        p=release/row['path'];require(not p.is_symlink()and p.is_file()and p.stat().st_size==row['size']and compiler.sha(p)==row['sha256'])
    signature=P/'pg2802-manifest-v1.sig';require(signature.stat().st_size==64 and compiler.sha(signature)==s.SIGNATURE)
    bundle=P/s.ARCHIVE
    with tarfile.open(bundle,'x:')as tar:
        for p in sorted(release.rglob('*')):
            require(not p.is_symlink());tar.add(p,arcname=p.relative_to(release).as_posix(),recursive=False)
    with tarfile.open(bundle,'r:')as tar:check_members(tar.getmembers(),{r['path']for r in data['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'})
    record={'archiveSha256':compiler.sha(bundle),'signatureSha256':s.SIGNATURE}
    compiler.write(out/'bundle.safe.json',json.dumps(record,sort_keys=True).encode())
    prior=json.loads((W/'pg2818-network-current-cold-frozen-v1.safe.json').read_bytes())
    require(prior['actualExit']==0 and prior['productionSource']==s.current.SOURCE)
    for name,digest in prior['fileHashes'].items():
        p=W/s.current.TOOLS/name;require(compiler.sha(p)==digest)
        if name.endswith('.class')and not name.startswith(s.current.CLASS):compiler.write(out/name,p.read_bytes())
    compiler.write(out/(s.CLASS+'.java'),s.java().encode())
    compiler.write(out/(s.CLASS+'Test.java'),s.java_test().encode())
    compiler.write(out/s.REF,s.observer(compiler.sha(out/'bundle.safe.json')).encode())
    current=W/'pg2654-release-v1'
    cp=':'.join(map(str,[out,current/'api/api.jar',current/'operations/batch.jar',current/'api/lib/*',current/'operations/lib/*']))
    # Explicit actual toolchain path, no inferred workspace repository fallback.
    repo=P.parent.parent/'toolchain/m2/repository'
    cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',
        'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
    commands=[('independent-python',['python3','-B',str(compiler.ROOT/'tools/quality/pg2832_network_cold_unused_sources_test.py'),'-v']),
        ('javac',[str(compiler.J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(out),str(out/(s.CLASS+'.java')),str(out/(s.CLASS+'Test.java'))]),
        ('literal-java',[str(compiler.J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,s.CLASS+'Test'])]
    phases=[]
    for phase,command in commands:
        log=out/(phase+'.private.log')
        with log.open('xb')as f:r=subprocess.run(command,cwd=compiler.ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        phases.append({'phase':phase,'actualExit':r.returncode,'logSha256':compiler.sha(log)})
        if r.returncode:break
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=compiler.ROOT)
        and head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=compiler.ROOT,text=True).strip())
    hashes={p.name:compiler.sha(p)for p in out.iterdir()if p.is_file()}
    for p in out.iterdir():p.chmod(0o400)
    compiler.write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
    result={'run':'PG2834-network-cold-unused-compile-v1','actualExit':phases[-1]['actualExit'],'operatorSource':head,
        'productionSource':s.current.SOURCE,'candidateSource':s.CANDIDATE,'candidateManifestSha256':s.DIGEST,
        'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':phases,
        'fileHashes':hashes,'bundle':record,'vmActions':0,'formalAccepted':False}
    compiler.write(W/FROZEN,json.dumps(result,sort_keys=True).encode())
    print(json.dumps({k:v for k,v in result.items()if k not in ['phases','fileHashes','bundle']}));return result['actualExit']


if __name__=='__main__':raise SystemExit(main())
