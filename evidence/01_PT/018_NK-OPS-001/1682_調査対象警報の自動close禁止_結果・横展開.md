# 1682 調査対象警報の自動close禁止 結果・横展開

1681/PG-D553/BUG1667-YKT1418/group1899。Main修正9c087705c、旧oracle追補後の資格source `3a863d360489cc2b09b4e1287b6469d4740eedf2`。SS351§12を根拠にDLQ/INTEGRITY_CONFIGは通常observeで自動closeしない。他10conditionの5分/10分＋原因確認は維持。実手動調査/明示退役の権限・永続経路は未実装受入であり、本結果で全C07を完了扱いしない。

| provisional原run | 真正結果 | manifest SHA256 |
|---|---|---|
| PG7548-protected-alert-host-v1 | source9c/exit1/204試験F2（Registry/Missing旧oracle）・未合格 | df3badf1da66a3b65fdc8b539028c3c7dae458d95651633a28e7ba86e3a64a06 |
| PG7552-protected-alert-six-compile-v1 | source9c/六正常compile0・PT0/UNRUN、当sourceへ転用0 | d296b74e8643d3d76dbc9848297c384ba1fff62874d3531d7687cc4f120ec2d5 |
| PG7548-protected-alert-host-v2 | source3a/真正0/204普通PT27suite/FES・flaky0 | d73153d5f4e014f0c591ff7a5f0cb220de6880a3f65cd2aae0183f6417b5c19f |
| PG7550-protected-alert-post-v1 | 全55Java/実49＋metadata1/単一sessionCRC0/L812 M187 C49 B367全miss0/NullAway-SB-CS0/raw28 exit4保持 | a66a2a1f437ac38b95c1619e1b4d9daae480e0800f8d5df18a0e31334e616e52 |
| PG7553-protected-alert-six-compile-v2 | source3a/六正常Main/Test compile-package0、PT0/UNRUN | 007a91fc99e2d44fb8c4afe6ddc2eea2ccb91c8eaf5ea26908b12636439a4266 |
| PG7554-protected-alert-six-post-v1 | 全1750Main/元1669debug込みbyte不変・当Batch50/歴史API21-Web10 byte-only/三POM・SDK pin・当五rule0 | 2d5f8cdf6fbd9d9d7eb02a1a4add74e7f42ec9c0f66a1761ac3f130015ffd4eb |
| PG7556-protected-alert-trace-v1 | 全94source/81追加physical・編集5/不変89/新0・当Batch49だけcurrent PT | 1c6883b725742d327cf00c0ff6cc5d4dccc1119dfd324a73ab1656878ef91c55 |
| PG7558-protected-alert-review-v1 | raw28全理由/26同位置＋core二行guard挿入による二行移動をexact context照合/未分類0・生成23型82method/六domain負改変 | 6b7bdebb0764238cce1d51bc176a3d8940ac55b4614b36efdf9f8260cf2e1a82 |

全環境/日時/OS/JDK25.0.4/Maven3.9.12/branch/source/command/actual exit/input/XML/output/CRC/coverage/static/hashは原manifestへ一意結合。初回204F2を成功へ合算せず、失敗理由はMain guardの不足でなくSS351禁止を未反映のRegistry/Missing期待値。上位期待を緩和せず、固定protected二condition×6service=12保持・他60正常回復へoracleを追補し、同source再実行した。

## YKT1418全対象の確認

- AlertLifecycle.normal：activeなしはempty、protected二keyはcause両値・両level・1日/MAX elapsedでも同eventを保持。PROTECTEDALERT001/002は全72key/288組合せと64caller×二ownerを実行。count/first/last immutable、invalid/null/逆行とprivate lockは既当回帰。
- AlertRegistry：ALERTREG002で全72warning→0/300normalの後も12の正確なcondition/service/order/count1を保持、他60だけclose。snapshotの元72件immutableを確認。
- MonitoringPolicyEngine：MONPIPE003で全12criticalの正常600＋CONFIRMEDでもprotected二keyを正しい順で保持、他10だけclose。
- Missing observation：MONMISSING001の全72key/gap300→normal301/600/601は他60の厳密5分回復を維持し、protected12のevent/count/first/lastを保持。欠測から解除を捏造しない。
- 他10condition/各monitor：既warning5分/critical10分＋原因確認・gap/並行/null等を当204回帰で維持。secret/config driftは現Condition.INTEGRITY_CONFIGの統合keyであり架空の追加conditionを作らない。実調査/永続退役権限は別未受入・操作0。

元製造新規0/実装とoracle手戻り一・新case2＋必要既202、初回失敗/再試行原因/二Test追補を分離。古い202成功確認の再演ではなく、Main変更とoracle修正による必要fresh資格。検証時のdraft apply_patch context拒否は無変更・試験開始前、pyflakesのunused importは未実行工具の事前検査で除去。既source/raw/失敗を上書き0、解析抑制/一括行無視/除外追加0。

BUG1667/YKT1418は自動close禁止と影響全oraclesの限定修正をCLOSED、明示退役の運用機能や全監視受入は未完。群開始3/5/9pp上限10/fresh25、原-v4-v5/元窓0/reset1793306748不変更。専有費/N/T/工数null、正式1964/53・原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLD不変更。自分の7548-v1/7552/v2/7550/7553/7554/7556/7558は全終端回収済み、実VM/DB/Root/keys/通知/退役操作0。
