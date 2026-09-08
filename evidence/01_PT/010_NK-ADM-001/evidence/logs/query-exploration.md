# User照会PG/PT探索記録

PG-D-081/PT-ADM-001～007、2026-09-08、dev-admin。Production sourceと独立UI236 byte/SQL後条件を並行実装した。

| Run | 結果・扱い |
|---|---|
| PT-ADM-query-explore-01、14:48:36 JST | 3件とも新規fixture resetで未到達。app roleにTRUNCATEを許可していない正しい権限制御に抵触。隔離test DBのresetだけadminへ変更し、Production queryはapp roleを維持。合格に算入しない |
| PT-ADM-query-explore-02、14:49:22 JST | 3件中detail fixtureがauth_sessions必須client_addressを欠いて目的session検査へ未到達。DDL全文を照合しclient_address/created_message_idを合成値で補足。Production/DDL変更なし。合格に算入しない |
| PT-ADM-query-explore-03、14:50:34 JST | 正常一覧/詳細/lock境界3件PASS。残るnegative/並行は未実施 |
| PT-ADM-query-explore-04、14:53:37 JST | 全7件PASS。新規queryの明示branchは網羅。detail早期returnによりjavacが二重生成するresource-close/null分岐が残るため、同じOptional値を一つのreturnへ集約した。close/SQL/不存在契約は不変で除外設定は追加しない |
| PT-ADM-query-explore-05、14:56:46 JST | 全7件PASS、新規UserQueryRepository/UserQueryExceptionのline/method/class/branch100%。不存在＋close故障・prefix bind/getObject故障も追加確認。正式全gateの代替にはしない |

生provider errorには合成session列が含まれるため/tmpだけに保持し、Gitには上記sanitized要約のみ保存する。実credential・利用者data・DB dumpは使用しない。正式対象source commit、日時、環境、command、終了code、独立expected/actual・全coverage・Test ID/hashは正式実行後manifest.jsonへ収集する。
