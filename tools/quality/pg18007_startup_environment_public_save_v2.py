"""Save corrected human count units, bound to actual original ten tests/four suites."""
import g07_host_class_provenance_inputs as data
import pg12706_scenario_writer_public as save
save.OUT=save.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18007-startup-environment-public-save-v2'
save.BEFORE='bd801e101ad6b52248d36229b400f8d76f2b18ab'
save.PREFIXES=('documents/','evidence/01_PT/','tools/quality/pg1799','tools/quality/pg1800','tools/quality/architecture/ApiEnvironmentGateContractTest.java','tools/quality/architecture/WebEnvironmentGateContractTest.java','tools/quality/architecture/StartupEnvironmentTenCurrentJunitLauncher.java')
def main():
    p=data.read_checked(data.BASE/'PG17992-startup-environment-ten-post-v1/manifest.json','7ab47d6e2acfdf8fd9da99c99d11884b0174b94cf001ea986c6f6fea3d20f4da')
    assert p['tests']==10 and p['suites']==4 and len(p['cases'])==10 and len(p['xmlHashes'])==4
    for path in ['evidence/01_PT/018_NK-OPS-001/3449_APIWeb起動入力環境境界PT結果.md','documents/400_PGPT/401_PGPT成果物一覧.md','documents/400_PGPT/450_品質/456_領域別進捗・利用枠・中断再開管理.md','documents/400_PGPT/450_品質/460_基盤残件・再開優先順.md']:
        text=(data.ROOT/path).read_text();current=text if '/3449_' in path else text.split('\n## 最新checkpoint',2)[0] if '/401_' in path else text.split('\n## 最新checkpoint',2)[1]
        assert '十件/四suite' in current and '十四suite' not in current
    save.main()
if __name__=='__main__':main()
