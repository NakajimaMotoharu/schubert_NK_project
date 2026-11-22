# 警報・時刻・合成FileStoreのfixture是正

BUG-3590／YKT-2825、WBS-F03/2-2-b、RD171／UI252／SS351。六fixtureの有界待ちchecked型を特定し、注入例外の型を明示、固定順序の比較後に位置を進める。製品は f8532c27c2666570fe450f285c5a5436aacd8e7e のまま。期待は元仕様の固定警報順、日時・整数・合成FileStoreの値、元例外の同一性、復帰後の状態と有界終了。

| 対象 | 現通常試験選択 | 独立期待 |
|---|---|---|
| 警報registry／閾値／時間窓 | ALERTREG002/004、THRESHOLD014、MONWINDOW007 | 72件の固定順と残る12件、64件でも対象owner毎に一意、固定閾値、同一点からのDuration.ZERO |
| 観測clock／poller | OBS-CLOCK005/007/008、POLL002/004/007 | 固定Instantとnano、注入した例外の同一性、未観測gap、64値を各一度 |
| 合成FileStore | FSINPUT007/010 | 固定total1000、usable200の計64回と80%、失敗時に状態を変えず終了count65 |

PG42598は12件成功、F/E/skip 0。開始時のbuild scopeは装置・サービスに触れない合成fixture六source、承認済み現物理19。PG42596 v1は支援fixture欠落でcompile終了1、PTは未実行。v2で既承認fake storeの依存を明示し静的検査を完了。現SpotBugs生5は既fixtureの同一Unchecked例外注入、PMD生35はtest所有の有限pool。Checkstyle・型欠落ともに0。実FileStoreや実サービスは未試験。独立した測定用coverageや全451に加算しない。

- 元静的証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42596-f03-monitoring-related-fixture-raw-evidence-v2/manifest.json SHA256 0e6cd7d14356996389996990607f1ca1f0e3ca4d05b19499ad50cc2bab65b1fd
- 現試験・再静的 evidence/01_PT/018_NK-OPS-001/evidence/PG42598-f03-monitoring-fixtures-selected-twelve-retest-v1/manifest.json SHA256 caedc10867051ff375ee7cc7fb9533247524b1b2b2b6db7fd133e7bcc929d024
