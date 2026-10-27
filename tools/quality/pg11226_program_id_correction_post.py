"""Add canonical Program-ID correspondence without changing any historical sealed evidence."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT=data.BASE/'PG11226-program-id-correction-post-v1'
SOURCE='ae55baa85af2174fa01d73b62ad8899d3f44f306'
PARENTS=[('PG11170-api-metric-fixture-completion-v1','f6a7798fe6dfa3334c2bb38615449e33d3cde780fc36cf42a8ddb57b9f3697e5','aafcc38d2d48627e10f816dd45bfaeb20bf5e415',34),
    ('PG11196-api-catalog-scalar-pool-completion-v1','7a49203701dec9e04d05a32744a08299bd984af27a2e8b1c2c5c1e7c7e6f7f61','5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81',46)]


def require(value,reference):
    if value!=reference:
        raise ValueError('only explicit canonical Program correspondence; original source/results/hash unchanged')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    registry=data.ROOT/'documents/400_PGPT/430_構成・追跡/431_Module・Program一覧.md'
    registry_raw=registry.read_bytes()
    assert data.sha(registry_raw)=='1ee5e867c8ac7ceebe036eb16a0e959c81cc91477aaeadf6f1cc5b214c724049'
    assert '| 018 / `NK-OPS-001` |' in registry_raw.decode() and 'NK-MON-001' not in registry_raw.decode()
    record=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2167_Program ID誤併記の追記訂正.md'
    assert data.sha(record.read_bytes())=='61f8c6f9311521c5e0fe721bb5d3933fc80438f65caef8a1c10b92cc86dcfe7f'
    rows=[]
    for folder,pin,source,tests in PARENTS:
        path=data.BASE/folder/'manifest.json'
        old=data.read_checked(path,pin)
        assert old['actualExit']==0 and old['source']==source and old['actual']['tests']==tests
        assert old['programIds']==['NK-OPS-001','NK-MON-001']
        assert all(old['actual'][k]==0 for k in ('failures','errors','skipped','aborted'))
        spec=data.ROOT/old['specificationPath']
        assert data.sha(spec.read_bytes())==old['specificationSha256'] and 'NK-MON-001' in spec.read_text()
        producer=data.ROOT/old['invocation']['entrypointPath']
        assert data.sha(producer.read_bytes())==old['invocation']['entrypointSha256'] and 'NK-MON-001' in producer.read_text()
        rows.append(dict(originalManifestPath=str(path.relative_to(data.ROOT)),originalManifestSha256=pin,originalSource=source,
            originalActual=old['actual'],originalProgramIds=old['programIds'],effectiveProgramIds=['NK-OPS-001'],
            originalSpecificationPath=old['specificationPath'],originalSpecificationSha256=old['specificationSha256'],
            originalProducerPath=old['invocation']['entrypointPath'],originalProducerSha256=old['invocation']['entrypointSha256'],
            productTestsExecuted=0,coverage=None,oldSourceResultsReassigned=False))
    current_path=data.BASE/'PG11222-web-supplied-metric-fixture-completion-v1/manifest.json'
    current=data.read_checked(current_path,'d41379b2da95614f97ae78636c91c9ed4047def6460ff176b35b48b9c58fd144')
    assert current['source']==SOURCE and current['actualExit']==0 and current['programIds']==['NK-OPS-001']
    spec=data.ROOT/current['specificationPath']
    assert data.sha(spec.read_bytes())==current['specificationSha256'] and 'NK-MON-001' not in spec.read_text()
    assert current['actual']['tests']==32 and current['newAccepted']==0
    reference=copy.deepcopy(rows)
    require(rows,reference)
    negatives=0
    for key,value in [('effectiveProgramIds',['NK-MON-001']),('originalSource','old'),('originalManifestSha256','0'*64),
        ('productTestsExecuted',34),('oldSourceResultsReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][key]=value
        try:
            require(bad,reference)
        except ValueError:
            negatives+=1
        else:
            raise AssertionError('unregistered ID/source reassignment or invented PT accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,relatedBugs=['BUG-1903'],relatedYkt=['YKT-1654'],
        canonicalRegistryPath=str(registry.relative_to(data.ROOT)),canonicalRegistrySha256=data.sha(registry_raw),
        correctionRecordPath=str(record.relative_to(data.ROOT)),correctionRecordSha256=data.sha(record.read_bytes()),
        preservedHistoricalCorrespondence=rows,currentCompletionSha256=data.sha(current_path.read_bytes()),currentProgramIds=['NK-OPS-001'],
        currentSpecificationSha256=current['specificationSha256'],metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,
        originalEvidenceRewritten=False,actualSecretDataAccess=False,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
