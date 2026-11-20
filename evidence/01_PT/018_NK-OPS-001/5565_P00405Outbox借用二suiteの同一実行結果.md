# Outbox借用観測の当候補同一run

NK-OPS-001、P004-05/2、F03/2-2、SS332／351、SSC470、PT-OPS-OUTBOXDB-012と原19件。現Core `559f5b5945e82374e0843dcfae11a8d07faef1ea`。対象はOutboxObservationRepositoryとOutboxMetricCollector。五Mainから九物理を生成し、前の型付きcurrent資料八物理と旧型付きCollector一物理のSHA-256と一致を確認した。

PG41076は独立fixtureの原19とOUTBOXDB-012を一回で実行し、20成功／2 suite、失敗・エラー・skip・未実行0。追加済みの012は正常な読み切り後、ResultSetとStatementの逆順解放が双方失敗する二組。最初のThrowable同一、二つ目を一度だけsuppressedへ保持、借用Connectionの変更・closeなし。旧試験のSQL、UTC、例外、同時owner、公開値とmetricの固定期待は以前の仕様と試験を使用。

PG41078は元XML、単一exec、正の三CRCを別に照合。中心三classの生L89/M14/C3/B30/I379は未到達0、付随六物理の生counterはmanifestに保持。実PostgreSQLや外部サービス、QA-056の対象型は使わない。P004-05実DBのUTC、取引・権限・資源後条件、二所有型、F02／F03／451は未成立。元19＋単独1の結果を合成していない。

実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5576_p00405_outbox_twenty.py`、独立 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5577_p00405_outbox_twenty_post.py`。最初のpreflightは元単独1件の試験ファイルを製品Coreで照合しようとして未起動。元fixture SHAと新Coreの両方で確認するよう修正した。動的PTの再試行0。

[同一実行](evidence/PG41076-p00405-outbox-current-twenty-v1/manifest.json) [独立照合](evidence/PG41078-p00405-outbox-current-twenty-independent-v1/manifest.json)
