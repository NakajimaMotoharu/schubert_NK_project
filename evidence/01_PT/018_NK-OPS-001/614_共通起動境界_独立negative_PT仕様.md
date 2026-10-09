# 共通起動境界の独立negative PT仕様

NK-OPS-001・OPS-009/SYS-002/SYS-004/TST-004、UI212/251、SS343/451、主担当P018-03.02（daemonデータ境界）/P018-08.02（計測factory）。開始前見積りlow.15/base.5/high1.2週次共有pp/LOW、各既.02子budget .67/1.67/3.67内の限定subset、親子/共通/全体費加算0。P00404の実OS/InspectorNative依存は未完のまま、必要共通境界を独立正常・異常・null試験で確認する。

| Test ID | 事前条件・入力/操作 | 独立期待値・資源後条件 |
|---|---|---|
| PT-COMMON-922001 | default Surefire JVMにreserved PT agent無し（事前確認）。fromCurrentJvmのservice欠落/phase欠落を各一件、対応正常API ORDINARY/defaultを対照 | 欠落はIOException/既generic unavailable message、原因/INVを露出しない。正常defaultはOptional.empty、agent/出力/argv/env等の変異0。Production parseでexpectedを生成せずliteral例外/emptyを使う |
| PT-COMMON-922002 | 独立rootUid0 fixture・同boot/fixedNSS、Broker/Caddyの期待invocationをempty/allzero/uppercase/短い/hyphen付きへ一件ずつ変更 | 全件IOException・manager/kernel読取0。Root owner一致だけで不正INVを承認しない。既正常daemon/他owner negative suiteを併用 |

追加試験は観測portの境界であり、人工startup/反射/JVM option注入/任意agent/profile公開0。Native factoryは実JVM引数を読むだけ、欠落null negativeはAPI境界の既拒否契約を確認しNPEの正常catch禁止を維持。正式四100/同source全体・実経路は実測結果後に区別。実行command・source・終了code・OS/tool・coverage/static/hash/関連BUGは未実行時点では未確定、失敗/flaky/skipped/not-run加点0。
