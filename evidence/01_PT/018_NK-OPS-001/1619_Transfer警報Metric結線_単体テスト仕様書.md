# 1619 Transfer警報・metric結線 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS341§8・SS351§7/8/10/PG-D538。TransferHealthMonitor constructor/observe/snapshot/observedUsage/detail/Evaluation、独立TRANSFERCONN001～008。入力は既validated Usage/Optional/ObservationContextだけ。実file/dir/walk/collector/cleanup/Root/DB/VM/provider/keys操作は行わない。

固定oracleはSS351のbytes>=3,500,000,000又はfiles>=5,000でWARNING、bytes>=4,500,000,000又はfiles>=9,000でCRITICAL、warning5分正常/critical10分正常＋原因撤去でclose。STDは詳細metric0でもhealth判定を継続、DEBUG4gauge/固定suffixだけ。UNKNOWN/gapは正常回復切断・event/countを保持し、未知をzeroにしない。異常null/elapsed逆行をsource/metric/state変更前に拒否する。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| TRANSFERCONN001 | DEBUG固定二suffix Usageとcontext | health正常・4gauge固定値・immutable入力snapshot/借用所有 |
| TRANSFERCONN002 | byte3.5GB/件数5000それぞれ直前/丁度、二suffix各半分の合計 | 別ownerとも直前正常/丁度WARNING、partだけ等への誤集計をcount増分で検出 |
| TRANSFERCONN003 | byte4.5GB/件数9000それぞれ直前/丁度・二suffix合計、warning域へ戻す | WARNING→同event CRITICAL、sticky/count正確・合計条件を独立確認 |
| TRANSFERCONN004 | 初期未知/critical/正常/未知/正常599・600秒 | gauge NaN/clear・open/count保持、未知後正常10分が必要 |
| TRANSFERCONN005 | critical→正常中の明示gap | 回復期間リセット、旧count保持・十分な正常後close |
| TRANSFERCONN006 | STANDARD warning/criticalと正常・原因確認 | health継続/metric0・値保持0、warning5分/critical10分＋原因確認 |
| TRANSFERCONN007 | null ctor/service/mode/Optional/context/Evaluation・elapsed逆行 | 境界拒否/metric・既event/count不変、無効service時登録0 |
| TRANSFERCONN008 | 64並行同Usage/elapsed | 同event count65/旧snapshot不変・4系列不増 |

新8＋必要既161を当source固定後ordinary Maven verify、全XML/終了/FES0/実CRC・単一session・全Main四counter100、lint/Werror/NullAway/SB/CS/PMD個別適用性。PG7286/7288以降manifestへOS/JDK/tool/branch/source/command・日時/終了/XML/coverage/static/path/hashを保存予定。既SDK四Jar同版を再利用/取得なし、元成功確認の4222/common44再演なし。新障害は修正前915/916へ起票。

実collector真正性/periodic採取・期限・entry停止制御/exporter/Root/native/CHR/全体451は未受入HOLD。optional供給は権限や実source成功を意味しない、別gaugeのcross-scrape transactionも保証しない。正式1964/53・歴史17/別source新7・原190新受入0・工数null/QA051final/PTALT0を維持する。
