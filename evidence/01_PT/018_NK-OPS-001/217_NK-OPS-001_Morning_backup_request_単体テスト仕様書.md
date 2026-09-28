# 217 NK-OPS-001 Morning backup request公開順・単体テスト仕様書

Program ID NK-OPS-001、PG347。対象`MorningBackupPreparation.execute`。RD OPS-009/BAK-001、UI251、SS331 §8.3、SS341 §6.1～6.2、SS343 §6.15、SSC-092/094/104。親`MorningControlScope`のINVALID後、同run・同cutoffの専用DB能力で`BACKUP_DB`と`BACKUP_CONFIG`を一括begin/commit確認し、その後に限り非秘密`BackupWorkerRequest`をnew-onlyで公開する内部境界。実backup worker・Unit終端・manifest・DB成功・Cleanup/permitは別未達。

| Test ID | fixture・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-MBPREP001 | 固定run/cutoff/activation、固定UTC µs時刻、手書き2step attempt、fake DB/Publisher | `begin(DB,CONFIG)→publish→work`。両step同run、別ID、順序/commit前公開0。SS341 §6.1～6.2 |
| PT-OPS-MBPREP002 | 明示resume、元cutoff+1秒、既存attempt形、recover=true | DBへ元run/同cutoffとrecover=trueを渡し、requestは同run・開始時刻のみ。新run IDを作らない。SS341 §3/6 |
| PT-OPS-MBPREP003 | DB beginがIOException/不正handle/null | publish/workとも0、非成功。commit不明を成功へ変換しない。SS341 §6.1 |
| PT-OPS-MBPREP004 | request公開失敗 | work0、同runを保全。DB begin済みを成功済みbackupへ読み替えない。SS341 §6.2 |
| PT-OPS-MBPREP005 | completion有、now<cutoff、無効request時刻・part/run重複 | DB/publish/work0。無効入力によるcommit先行を防ぐ。SS343 §6.15 |
| PT-OPS-MBPREP006 | state/DB/clock/publisher/part/work null、worker結果null | 境界でNPE契約拒否、I/O開始0。NPEをcatchして成功扱いしない。 |

独立期待値は固定UUID/Instantと手書きevent列、SSの固定step enum/順序から作る。production methodからexpectedを計算しない。異常、null、再送は上記、並行・DB実後条件は既存MDB/MNEW/MRESUME PTと併走。requestは権限証明ではなく、publish後の実Unit fresh起動/終端・backup現物は別PT。coverage除外なし。実行command/環境/source commit/coverage/結果/証跡hash/障害番号は218とmanifestに記録する。
