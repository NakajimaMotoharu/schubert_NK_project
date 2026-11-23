# Batch監視の例外後解放の単体テスト仕様追補

NK-OPS-001、WBS-F03/2-2-b／P018-09、RD171／UI252／SS351 §7・§10。BUG-3726／YKT-2925。対象はContinuousConditionWindow.observe、Timed* 四監視observe、AlertLifecycleの同状態への正常・警告入力とsnapshot。既存の時刻・観測・結果境界と同じ単体契約。

| Test ID | 独立入力と操作 | 独立期待 |
|---|---|---|
| PT-OPS-MON-SNAP005 | 4監視・連続窓・アラートに経過1秒からの測定を入れる。同じcallerから経過0秒を入れて拒否を確認。別の有限workerで経過2秒の測定・snapshotを行う。 | 逆行はIllegalArgumentException。連続窓の違反継続は1秒、アラートと閾値越えDB poolの累計2。ファイル／heap／同期遅延の警告初期は空。すべて別workerで有限に完了する。 |

原PG43028の値・並行54とAlertLifecycleTestの既存契約を同候補で選択する。規則判定はPG42998の対象のみ。実DB・ファイル・実時計へ接続なし。変更前の適用PMD9を保存し、コード・試験同候補の結果、四指標、元とのABI照合を追補する。
