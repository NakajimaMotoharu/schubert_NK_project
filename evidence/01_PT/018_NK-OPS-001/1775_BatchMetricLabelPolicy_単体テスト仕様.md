# Batch closed label policy PG/PT仕様

NK-OPS-001/RD171/UI252/SS311341351/411/451、PG-D603/group2002、主WBS-P018-09/C07参照0加算。fresh30残70/reset1793382075/1-3-6pp/cap10をPG8448/event2002へ固定。後続索引一致0・現Batch MetricContractは名前だけ検証、実writer/値検証ではない旨を明記済み。API/Webと違いBatch POMはmicrometer-coreのみでtext SDK Production依存がない。当群は既依存内のBatch-owned六family値検証・immutable Mapへのcopyに限定し、POM横断変更/実exporter接続や当作業だけの受入を捏造しない。

## 製造
BatchMetricLabelPolicyはcounter3（batch_runs/integrity_failures/process_restarts）、gauge3（batch_last_success/file_transfer_files/bytes）のname/type/key/valueを閉じる。batch step10/status4・Integrity area3/step10・Service6/reason4・suffix .part/.readyを既SS/供給Recorderと同じfixed catalogへ。未知metricを先に拒否し、Tag name/valueを各一回、duplicate/missing/extra/nullを拒否、返却Mapとnamespaceは深いimmutable。provider例外を握り潰さず、実Batch/DB/Backup/鍵/file/process/VM/endpoint/既Mainの操作変更なし。

## 新BATCHLABEL001～014・14/1
1. exact六family/type/keys（Counter3/Gauge3/Histogram0）。
2. literal batch step10×status4、last-success10、transfer4。
3. Integrity HASH/PATH/CONFIG×独立step10=30。
4. Service6×Reason4=24。
5. unknown/API/Web/name prefixを固定diagnosticで拒否、tags未読。
6. 各family全fieldの未知値と高cardinality keyを拒否。
7. 各familyの欠落/余剰を拒否。
8. duplicate Tag実在を先にassertし拒否。
9. kind/name/list/Tag/key/value nullを拒否。
10. mutable Tag/listから返却Mapをdetachしimmutable。
11. namespaceと内側keysを深いimmutable。
12. Tag provider Runtime/Errorの同一identity保持。
13. 有限64並行・join10sec/sleep0、別instanceの状態を混ぜない。
14. 一回key/value read、返却値はSS literal、元providerの後続変化へ依存しない。

期待は上記独立literal、production enum/methodからexpectedを生成しない。正常六compile/NullAway/format→新14/1（一exec）→新Main1実line-method-class-branch100/PMD-CS-SB-missing0/CRC0/session1→全physical/source-owner/role→1776。実command/環境/OS-JDK/branch/source/時刻/exit/input/期待/実際/XML/exec/counter/static/log/hash/BUG-YKTを新only公開manifestへ。未実行/skip/failureをPASSにせず、実装済み違反は修正前915/916へ。独立PTは機密/実操作/拒否再試行なし。

現在PT/coverage UNRUN。固定値policyをgeneric text writer安全保証とせず、同じ返却copyを後続modelへ直接接続する必要あり。whole451/CHR/実VM-Root-DB-native-Backup-鍵-permit-配備/拒否未特定HOLD、formal1964-53/原190新受入0/工数null/QA051final/PTALT0・元-v4-v5/欠測維持。

