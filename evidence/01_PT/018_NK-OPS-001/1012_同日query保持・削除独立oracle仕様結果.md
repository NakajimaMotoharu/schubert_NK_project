# 同日query保持・削除独立oracle仕様結果

NK-OPS-001/PT-OPS-SSC299-SAMEDAY001、SS341/SS324§12.2/12.8/SS352 SSC157/UI232・236、BUG1383/YKT1149。Source825e/PG4702/BOMf1、branch dev-foundation、Linux/Python3.14.4/独立cryptography AESGCM/zlib、旧before f8d全24を私有読取。Root/SQL/時計/Unit変更なし。

4732元60301 actual1は旧2078 AUTH_SESSION限定oracleの適用外拒否で保全。4733元41393 actual0で当候補=LGN10・UDT1・QSD2・NTS1、通知候補1だが当日CLEAN_NOTIFICATION既SUCCESSのため保持、非backup7step skip・backup毎回、Outbox候補はcutoffで変化することを独立確認。取消ではなく質問回答明細QSDである。

新4742はliteral UI236 QSD8352/NTS48+624×最大50、既独立UDT320、NKENC1/AES256GCM/AAD/zlib/byteoffset/全field/保存code/参照NONEとNKQRY1 scopeを独立検査する。QSD frameはSS352の7byte magic＋USER/ADMIN一byte、別layout・短縮・未知scopeを拒否。失われたAUTH_SESSIONは保護、正しい過去queryは現在の質問/通知本文へ比較し直さない。通知candidateを当日skipにもかかわらず削除する期待値を作らない。

期待値の根拠は上記SS/UIのliteral/immutable BEFOREだけ、Production呼出し0。独立literal成功/error/byte変異・scope USER/ADMIN/legacy/異layout/短縮・暗号・24table差分/通知不変/Inbox削除不正/progress不正を5工具試験FES0で確認（旧SameDay2も含む、Production PT追加0）。全host/emitted静的0。初期TDDのgeneric条件置換過剰/bytearray集合member/fixture位置を是正。元4744/64829 actual1はframe漏れ、元4748/56964 actual1はbytearray scope型不備として保存し、元log/payloadを書き換えない。

**PG4750元81319 actual0**、22:10:59.163205Z、payload SHA256 `86857837f9c7631887118d84e5e5589cd786a41c8a875433f8495e7c23cfeab3`、private manifest=`PG379/pg4750-scoped-query-preflight-v2/manifest.safe.json`。修正後host静的import整備後もemitted完全SHA同一を確認。現cutoffと2h後とも当日2026-10-17・7skip・**Inbox削除4/保護10/通知候補1保持**、Outbox削除448→672、独立適用true。件数だけを公開、鍵/平文/row/ID輸出0・buffer zero。実Root cutoffで再計算し、単一固定448を全cutoffに流用しない。

observer4734 stage元60836はdirty guardで開始前AssertionError、local stage .started/.exit/私有bundleの不存在を確認、guest stageなし。clean固定後の初回stageに進める。4740資格payload/hosthash不変更、Root未発行。正式1964/53・工数null/QA051final/F03/四100は未完。
