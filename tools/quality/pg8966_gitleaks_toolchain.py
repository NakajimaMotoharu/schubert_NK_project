"""Public pinned Gitleaks binary/license install only; no scan, credential, daemon or target access."""
import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import tarfile
import urllib.request
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

TC=host.ROOT.parent/'toolchain'
SLOT=host.W/'pg8966-gitleaks-toolchain-v1'
INSTALL=TC/'gitleaks-8.30.1-linux-x64'
OUT=host.BASE/'PG8966-gitleaks-toolchain-v1'
ROOT_URL='https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/'
ASSETS={
 'gitleaks_8.30.1_linux_x64.tar.gz':('551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb',8230402),
 'gitleaks_8.30.1_checksums.txt':('061476c21adaf5441516f96f185c1a4706a83cd6329b9b38762271b3d4a52fae',999)}

def main():
    invocation=capture(Path(__file__))
    assert platform.system()=='Linux' and platform.machine() in ('x86_64','amd64')
    assert not SLOT.exists() and not INSTALL.exists() and not OUT.exists()
    SLOT.mkdir(mode=0o700)
    downloads={};payload={};stage='PUBLIC_PINNED_DOWNLOAD'
    try:
        for name,(expected,size) in ASSETS.items():
            request=urllib.request.Request(ROOT_URL+name,headers={'User-Agent':'Schubert-NK-PGPT-toolchain'})
            with urllib.request.urlopen(request,timeout=30) as response:
                data=response.read(size+1)
            assert len(data)==size and hashlib.sha256(data).hexdigest()==expected
            file=SLOT/name
            with file.open('xb') as output: output.write(data)
            file.chmod(0o600);payload[name]=data
            downloads[name]=dict(source=ROOT_URL+name,sha256=expected,bytes=size,path=str(file))
        checks=payload['gitleaks_8.30.1_checksums.txt'].decode('ascii').splitlines()
        chosen=[line.split() for line in checks if len(line.split())==2 and line.split()[1]=='gitleaks_8.30.1_linux_x64.tar.gz']
        assert chosen==[[ASSETS['gitleaks_8.30.1_linux_x64.tar.gz'][0],'gitleaks_8.30.1_linux_x64.tar.gz']]
        stage='NEW_ONLY_VERIFIED_BINARY_EXTRACTION'
        contents={}
        with tarfile.open(fileobj=io.BytesIO(payload['gitleaks_8.30.1_linux_x64.tar.gz']),mode='r:gz') as archive:
            members=archive.getmembers()
            for name in ('gitleaks','LICENSE'):
                selected=[member for member in members if member.name==name]
                assert len(selected)==1 and selected[0].isfile() and 0<selected[0].size<64*1024*1024
                stream=archive.extractfile(selected[0]);assert stream is not None
                with stream: contents[name]=stream.read()
                assert len(contents[name])==selected[0].size
        assert b'MIT License' in contents['LICENSE']
        INSTALL.mkdir(mode=0o700)
        files={}
        for name,data in contents.items():
            target=INSTALL/name
            with target.open('xb') as file: file.write(data)
            target.chmod(0o700 if name=='gitleaks' else 0o600)
            files[name]=dict(path=str(target),sha256=host.sha(target),bytes=len(data),mode=oct(target.stat().st_mode&0o777))
        stage='FIXED_BINARY_VERSION_ONLY'
        command=[str(INSTALL/'gitleaks'),'version']
        result=subprocess.run(command,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},capture_output=True,timeout=15,check=False)
        assert result.returncode==0 and result.stdout.strip()==b'8.30.1' and not result.stderr
        verify(invocation);OUT.mkdir()
        value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,version='8.30.1',os=platform.platform(),architecture=platform.machine(),downloads=downloads,installed=files,versionCommand=command,versionExit=result.returncode,onlyVersionExecuted=True,scanExecuted=False,publicArtifactDownloads=2,checksumBasis='FIXED_GITHUB_RELEASE_API_DIGEST_AND_OFFICIAL_CHECKSUM_FILE_OVER_TLS_NOT_VENDOR_SIGNATURE',repoBinaryAdded=False,systemOrPathModified=False,actualVmActions=0,actualDatabaseActions=0,actualPrivateCredentialReads=0,actualTargetServiceConnections=0,newProductTests=0,coverage=None,formalUpdated=False)
        host.write(OUT/'manifest.json',value)
        print(json.dumps(dict(actualExit=0,version='8.30.1',publicArtifactDownloads=2,binarySha256=files['gitleaks']['sha256'],manifestSha256=host.sha(OUT/'manifest.json'))))
        return 0
    except Exception as failure:
        # Never format provider errors/redirect URLs/headers, including temporary CDN query values.
        failed=host.BASE/'PG8966-gitleaks-toolchain-failed-v1';failed.mkdir()
        host.write(failed/'manifest.json',dict(actualExit=1,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,stage=stage,failureType=type(failure).__name__,completedDownloads=downloads,originalPublicBase=ROOT_URL,rawErrorSuppressed=True,partialSlotPreserved=True,scanExecuted=False,newProductTests=0,formalUpdated=False))
        print(json.dumps(dict(actualExit=1,stage=stage,failureType=type(failure).__name__,rawErrorSuppressed=True)))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
