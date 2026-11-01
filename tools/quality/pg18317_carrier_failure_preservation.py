"""Preserve original failed XML and failed tool terminal separately, no Product replay."""
import json
import shutil
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18317-carrier-failure-preservation-v1'
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rawdir=data.BASE/'PG18320-carrier-catalog-five-pt-v1'
    pin='01fd16320e3b840c6f1feed9407c06558f13adae8e09a29a0ce8b78871072fa4'
    raw=data.read_checked(rawdir/'manifest.json',pin)
    assert raw['actualExit']==1 and len(raw['cases'])==5 and sum(c['result']=='PASS' for c in raw['cases'])==4
    host=data.ROOT.parent/'pgpt-runs/PG379/pg18320-carrier-catalog-five-pt-v1'
    for filename,digest in raw['xmlHashes'].items():
        source=host/'xml'/filename;target=rawdir/filename
        assert data.sha(source.read_bytes())==digest
        if target.exists():assert data.sha(target.read_bytes())==digest
        else:shutil.copyfile(source,target)
        assert data.sha(target.read_bytes())==digest
    prior=data.ROOT/'tools/quality/pg18318_composite_bytecode_witness.py'
    assert data.sha(prior.read_bytes())=='4cc7f723ae8d54bdceff7e6fb15c90b7f465a94f1c1ed54a6df6cf8b324ea34e'
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg18318-composite-bytecode-witness-v1'
    stages=[]
    for label in ['javac','static-instrument-bytes']:
        p=slot/(label+'-exit.safe.json');m=json.loads(p.read_bytes())
        assert m['actualExit']==0 and not m['timedOut']
        assert all(data.sha((slot/(label+'.'+k)).read_bytes())==m[k+'Sha256'] for k in ['stdout','stderr'])
        stages.append(dict(name=label,path=str(p),sha256=data.sha(p.read_bytes()),stage=m))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,preservationOnly=True,originalFailedRawSha256=pin,originalFailedRawExit=1,originalFailedCases=1,originalSuccessfulButUnqualifiedCases=4,oldXmlHashes=raw['xmlHashes'],originalFailedWitnessEntrySha256=data.sha(prior.read_bytes()),originalFailedWitnessExit=1,originalFailedWitnessToolResultChunk='716d61',originalFailedWitnessExitBasis='OBSERVED_TOOL_TERMINAL_TRANSCRIPTION_NOT_A_NEW_RUN',completedWitnessStages=stages,failedEvidencePromotedToPass=False,productTestsExecuted=0,oldTestsOrToolsReexecuted=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
