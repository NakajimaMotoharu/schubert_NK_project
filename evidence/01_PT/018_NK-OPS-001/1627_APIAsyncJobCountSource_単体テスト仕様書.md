# 1627 API Async job count source 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS331§6.3・332§2・342§6.2・351§6/PG-D540。AsyncJobCountRepository.read/state、独立ASYNCDB001～008。同API metric Snapshotへ接続するreadonly集計部品であり、実JDBC driver/DB/Root/VM/cohort接続・業務process/worker・原本/鍵/permit等へ一切アクセスしない。Testは自己所有のConnection/PreparedStatement/ResultSet dynamic proxyと固定rowのみ。

独立oracle SQLは`SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state`。全体一SELECTの成功したgroup結果だけを読み、存在しないgroupはSQL上0件と確定して五stateを埋める（未知/失敗の0補完ではない）。null/未知state/null COUNT/負数/重複group/総和overflowは固定redacted SQLExceptionで非成功。borrowed ConnectionはautoCommit=false/readOnly=true/READ_COMMITTEDで、設定変更/commit/rollback/close/新接続なし。API query1500ms/role1500ms内の内部保守的JDBC timeout1秒を設定、実driverの厳密期限は未測定HOLD。RS→PSの順に全close成功後だけSnapshotを返し、SQL/close故障は非成功でJava TWRのprimary/suppressedを維持する。自動retryなし。

| Test ID | fixture/操作 | 独立期待値 |
|---|---|---|
| ASYNCDB001 | 五rowをshuffle/一read | 固定SQL一回/timeout1、五count1..5・total15、RS→PS各1close/Connection close等0 |
| ASYNCDB002 | empty rows・一部groupだけ | 成功したqueryの未出現stateだけ0、全五count/totalが固定期待値 |
| ASYNCDB003 | null/autoCommit/readOnly/isolation境界 | 無効txはprepare/query0、接続設定・commit/rollback/closeなし |
| ASYNCDB004 | SQL NULL/未知・alias/負数/重複row | 固定checked例外、raw stateをechoしない、RS/PS閉鎖・部分Snapshot返却0 |
| ASYNCDB005 | 最大long/総和overflow | 最大原値保持、overflowはchecked failure・wrap0、全資源close |
| ASYNCDB006 | null PS/RS・prepare/timeout/execute故障 | boundary failure/同一vendor例外、該当取得資源だけclose、Connection所有保持 |
| ASYNCDB007 | next/getString/getLong/wasNull/RSclose/PSclose故障・循環cause | 部分値を返さず同一primary/正しいsuppressedと逆順close、自動再試行/原因graph走査0 |
| ASYNCDB008 | 64並行/それぞれ独立conn・row値 | singleton Repositoryの状態混同0/各期待値・一query/全RS-PS close、Connection操作0 |

新8＋必要既API8を当source固定後API monitoring harnessのordinary Maven verify、XML全case/終了/FES0・実4class/単一session/CRC/四counter100、lint/Werror/NullAway/SB/PMD/CSを確認。PG7314/7316以降manifestへOS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashを保存予定。予定全67source/1727physicalは実測前未確認、旧Batch169/Web23はbyteだけで当API16へ合算しない。実DDL/DB後条件/role接続の成功とはしない。障害は修正前915/916起票。

actual DB identity/role/timeout実設定/query plan/driver cancellation/outer finite collector・transaction所有の真正性/Root/exporter/native/CHR/全体451は未受入HOLD。借用tx getter検査はruntime権限証明ではなく、SQL型付きdata集計から業務成功を生成しない。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0不変更。
