"""Bind actual successful scopes to source and record one fixed host-tool version; no Product replay."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17515-current-scope-source-binding-v1'
RECORDS=[
('PG17440-primitive-owner-sixteen-pt-v1','5b57c7ddf85dc5d968c8d9559855dde8eac90adfca542903ca109576447d4fb9'),
('PG17442-primitive-owner-sixteen-post-v1','1be28e136e936315ddf5228cc1b142d6016cd9d67a2ee0fad90b4249754739e8'),
('PG17460-root-elf-metadata-six-pt-v1','a91debe4aeb7a59f914e84d30b720acba7f535a358596093d2a144e60c403dc8'),
('PG17462-root-elf-metadata-six-post-v1','f23d9f7deb1d4d302bde387305c4895ac516c45db206fdd115a6dcdafa0b8182'),
('PG17480-expiry-owner-two-pt-v1','51797f2b4a343b94450640ebe74cfc0b7c0a0485ff2020c7e8c317476b878140'),
('PG17482-expiry-owner-two-post-v1','cf4ea8e6a6095fb25c20b562a030fce1dbb639a6e4e7fec8312bb37a8c216a71'),
('PG17485-expiry-owner-two-independent-v2','79ae23fe5edca4c36a6569185acc298fefd910144b8254c7a460b0d7310cfc5e'),
('PG17500-inspector-deployment-eight-pt-v1','7fec86110b87d453a89b3ec57348754664d40248567d2ec6dc5eb7ef40336c57'),
('PG17504-inspector-deployment-eight-post-v2','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f'),
('PG17510-current2746-inspector-deployment-registry-post-v1','a36a52c7f9929cc941898d04794ba361ffbb5bb1a437b2ca9948846300107ba2'),
('PG17514-current2746-inspector-deployment-wbs-post-v1','374480cb06832c87678f8caf2048a131d66a6a63fed2d8dc260ae3540fbe73c2')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/name/'manifest.json',pin) for name,pin in RECORDS],SOURCE)
    binary=data.ROOT.parent/'pgpt-runs/PG379/pg17500-inspector-deployment-eight-pt-v1/public-fixture-root'
    assert binary.is_dir()
    tool='/usr/bin/systemd-analyze'
    assert data.sha(__import__('pathlib').Path(tool).read_bytes())=='188138cf3aea2111c7744069b58c0597559808163d1b7f74ded0348d85e4bef3'
    version=subprocess.run([tool,'--version'],cwd=data.ROOT,env={'LANG':'C.UTF-8','PATH':'/usr/bin:/bin'},capture_output=True,text=True,timeout=10,check=False)
    assert type(version.returncode) is int and version.returncode==0 and not version.stderr and version.stdout.startswith('systemd ') and len(version.stdout)<4096
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,sourceFromActualCompletedProof=True,toolVersionCommand=[tool,'--version'],toolVersionExit=version.returncode,toolVersionStdout=version.stdout,toolBinarySha256='188138cf3aea2111c7744069b58c0597559808163d1b7f74ded0348d85e4bef3',productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(version.stdout.splitlines()[0])
if __name__=='__main__':main()
