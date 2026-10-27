# Batch二DatabaseSession残44・現在source理由仕様

群 BATCH_TWO_DATABASE_SESSION_CURRENT44_REASON_REVIEW_V1、event2590開始、WBS-F03、見積.75/2/5pp・cap10。原見積/専有費不明nullを維持する。source `7f035ccfe89c46e8f4fae52099b1c0e4e890e66b`、Main `21d7c30425e7aa9ce435e808035a94fa4d75c93b`。正式1964PT/53scope、17/190、工数率nullを更新しない。

## 対象・期待値

MorningDatabaseSession/CleanupDatabaseSessionの原48警告中、既参照DoNotUseThreads四件は再加算せず、残44件だけ。PG10690の不変ID/全source SHA/座標/priority/診断message SHAをPG6048・6354の公開理由へ結ぶ。旧PT・case/coverage/native・Root所有を新sourceへ転用しない。PG6048の非空理由21＋PG6354の非空理由21を再認証し、空欄のPMD-03398/03399は今回の新source点検二件として分離する。ラベルだけを理由にしない。

独立根拠はorigin/main SS332（SSC063/199、SQL/unknown順位）と既存Java sourceの直接所有/型/guard。executeのcredential消費、callback lifetime無効化、connection一回closeとknown SQL/IO/Repository・unknown順位、queryのnested Statement/ResultSet一回closeを確認。Morning七volatileは原thread/lifetime/run/receipt guardとの併用であり、cross-thread JDBC権限や真正終端の証明ではない。

新二件はrecheckConsistentのcreateStatement取得直後try、SQL/RTE/Error primary記録・同一性再送出、nonnull Statement direct close一回とJdbcResourceFailures順位、固定READ ONLY文、外側SQL-only固定変換をsource token/spanへ対応。返却結果をproduction methodから作らず、期待token列と承認契約を別に記述する。null/unknown/cleanup複合時の実測は今回未実施。

## 実行・合否範囲

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg11580_batch_session_source_review.py` → PG11582 metadata反例 → PG11584現在index → PG11585独立再計算。helperは11579。全て公開JSON/Javaテキストの読取と新規証跡保存だけ。Session構築、callback実行、実DB/VM/Root/credential実体/鍵/private rawアクセス、新fixture/harness/製品試験・署名・配備・旧成功再演は行わない。ドラフト事前点検で診断末尾空白のstripとhelper hash再束縛を調整、OUT/製品実行なし。

source/helper hash・元row identity・理由非空・新二実method token・raw保持・旧runtime転用0を独立照合する。source/理由/数量/coverage/再加算を壊したmetadata負例を拒否し、その負例を製品PT件数へ算入しない。実行日時/環境/command/終了は各invocation/checked entry、path/hashは結果2230へ記録する。

全44はSOURCE_REBOUND_CURRENT_WHOLE_PENDING。新製造/製品PT/coverage/raw削除/正式受入は0。全F03/451/実接続・並行・停止・CHRは未受入。QA051final、QA053通知消失/再質問不要、全安全HOLD・保留二工具・Graph9/deferred8/stash七/原本/Current baselineを維持する。
