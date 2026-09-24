# NK-OPS-001 Artemis Queue容量 PT仕様

PG242。RD MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §5.2/5.3/10/13・342 §4、QA-042/UIC-002/SSC-075、YKT-185。対象はOps専用Core管理で6業務Queueの`messageCount`と`persistentSize`を読取り、閾値との状態を返すread-only `ArtemisQueuePressureClient`。Artemis公開管理APIでは両値がscheduled/paged/in-deliveryを含む。Byte閾値はSS321の合計保存上限の70%/90%を用い、件数は§5.2の明示値を優先する。critical一致はcritical。DLQは1件でalert、他のQueueと同じ件数warning/criticalへ勝手に置換しない。Byteは2GiB上限の70/90%を別監視する。この部品単独でAPI起動可否を宣言しない。

| Test ID | 事前条件・fixture・入力/操作 | 独立期待値と根拠 |
|---|---|---|
| PT-OPS-MQ-019 | 隔離実Artemis2.56.0/security有効、Ops credentialで全6 Queueの実metricを読む。application roleでは管理照会を拒否 | 6 Queue各0件/0byteはNORMAL、借用Ops session開・一時返信Address残存0。app roleは固定redacted失敗。期待値はSS321の6組を固定 |
| PT-OPS-MQ-020 | 6 Queueについて件数/byteをそれぞれ境界-1/境界/境界+1、負値/型/欠落へ変異。DLQは0→1件、byte70/90% | SS321 §5.2の件数250/450、5000/9000、1000/5000と合計byte70/90%、DLQ1件alert。低位計算はproduction methodでexpectedを作らず固定数値でassert |
| PT-OPS-MQ-021 | null session/reader、provider失敗、管理返信null/不正、borrowed所有、重複照会 | null契約で拒否、provider/metric異常は秘密causeなし固定redacted例外。Ops管理の2秒/一時reply cleanupを維持し、failed/skippedは合格にしない |

最初に選択Batch PTと追加class全4coverage/静的、collector負canaryを確認し、正式全reactor/全scope/hashで認定する。時刻/OS/JDK/tool/branch/commit/command/exit/input/expected/actual/coverage/関連台帳/hashは047とmanifestへ固定し、credential/raw session/tokenを保存しない。全matchは起動前にOps sessionで直列読取する。実際の起動阻止・metric/alert配送・journal/Expiry purge/JAAS user配布は後続gate。
