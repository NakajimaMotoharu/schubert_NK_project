"""Two explicit Program indexes and one source-local completion; no new Product execution."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '94eeea264b449e5826f292c746a9cd4655b3122a'
PINS = {
    'PG12992-value-binding-preflight-v1':'5849dba9b1e9ed5d5c7940fa4524c24314529a177aadb994549d3ff385e477d1',
    'PG12993-value-binding-style-before-v1':'d7ecef6908bdf5cf724e87824752a404893d2e1ab76e070c2c91bddff1a1a5ad',
    'PG12994-value-binding-preflight-v2':'2f2df02a4403be1446e8d0c4482e73fcd19f7be2340831980f9087f37463be9f',
    'PG12996-value-binding-plan-v1':'07fc9a45967a0da188eae4777f4b39c3627b88850754c818afb3092701b74386',
    'PG12998-value-binding-six-compile-v1':'f391201e726c7e4ad28b86b4e8d5ef332e2c06cfdca02d4df05529f332f8e730',
    'PG13000-value-binding-host-v1':'90ec2c83ee7746f7a602cbb8c2fd8edd75ade4b3a0336c843966e52aba290194',
    'PG13002-value-binding-static-v1':'d6240e732635baad7185ae535a5be2141e275d3c4b18030efbdf0bf6d1626e22',
    'PG13004-value-binding-post-v1':'3ea296e632ac9f8e2b9ae5824fb0637a8edf821d4c49bfa9140f476c5c22df85',
    'PG13006-value-binding-trace-v1':'f78a2bcc2f7285d3aacc87248ea21cb1ecc8ebafe34aaeec998fabaf218f972d',
    'PG13007-value-binding-trace-post-v1':'1ba4e0f66d5af60138d6cb4217d7b6dd65f3fabcde4ccc4cc2e6d7c179088b2a'}

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG13008-value-binding-completion-v1'; assert not out.exists()
    values = {name:data.read_checked(data.BASE/name/'manifest.json',sha) for name,sha in PINS.items()}
    for name,value in values.items():
        assert value['actualExit'] == (1 if 'PG12992-' in name else 0)
        if name.startswith(('PG12992-','PG12993-','PG12994-')):
            assert value['source'] is None and value['baseSource'] == '762568bb0338749c9549ec937cc2c79e84418836'
        else: assert value['source'] == SOURCE
    host = values['PG13000-value-binding-host-v1']; proof = values['PG13004-value-binding-post-v1']
    assert host['observedTestExecutions'] == proof['observedTestExecutions'] == 6
    assert proof['rawStatic'] == proof['staticGateExit'] == proof['spotbugsSixExit'] == 0 and not proof['selectedMainCoverage100']
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/name for name in ['2401_P008P009独立値束縛_単体テスト仕様書.md','2402_P008P009独立値束縛_実行結果.md','2403_共有83pct定期点検・業務oracle増分と残依存.md']]
    assert all(sha in docs[1].read_text() for sha in PINS.values())
    indexes = []
    for program,folder,test,prefix,count,subject in [
        ('NK-SCN-001','008_NK-SCN-001','ScenarioScriptFileBindingTest','PT-SCN-SCRIPTBIND',2,'ScenarioRequest'),
        ('NK-MED-001','009_NK-MED-001','MediaRequestDescriptorBindingTest','PT-MED-BIND',4,'MediaRequest')]:
        root = data.ROOT/'evidence/01_PT'/folder
        name = 'value-script-binding' if program == 'NK-SCN-001' else 'value-descriptor-binding'
        index = root/'evidence'/name
        assert root.is_dir() and not root.is_symlink() and not index.parent.is_symlink() and not index.exists()
        selected = [row for row in host['begin']['cases'] if row['className'].endswith('.'+test)]
        assert len(selected) == count
        indexes.append((program,index,selected,prefix,subject))
    verify(invocation); out.mkdir(); records = []
    for program,index,selected,prefix,subject in indexes:
        if not index.parent.exists(): index.parent.mkdir()
        assert index.parent.is_dir(); index.mkdir()
        path = index/'manifest.json'
        data.write(path,dict(actualExit=0,program=program,source=SOURCE,run=host['sessionId'],invocation=invocation,
            hostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13000-value-binding-host-v1/manifest.json',hostSha256=PINS['PG13000-value-binding-host-v1'],
            postManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13004-value-binding-post-v1/manifest.json',postSha256=PINS['PG13004-value-binding-post-v1'],
            observedRunProductTests=6,programSelectedTests=len(selected),newUniqueTestIds=len(selected),
            newTestIdMappings=[dict(testId=prefix+str(i).zfill(3),className=row['className'],method=row['method'],actual='PASS') for i,row in enumerate(selected,1)],
            selectedMain=proof['selectedMain'][subject],fullProgramAccepted=False,newAccepted=0,whole451Accepted=False,oldExecUnion=False))
        records.append(dict(program=program,path=str(path.relative_to(data.ROOT)),sha256=data.sha(path.read_bytes()),tests=len(selected)))
    assert sum(row['tests'] for row in records) == 6 and len({r['path'] for r in records}) == 2
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},programIndexes=records,
        observedProductTests=6,newUniqueTestIds=6,scopeStaticExit=0,selectedMain=proof['selectedMain'],
        selectedMainFourCounters100=False,fullArtifactCoverage100=False,whole451Accepted=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
