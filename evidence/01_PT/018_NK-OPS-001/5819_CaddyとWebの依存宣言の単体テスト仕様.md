# CaddyとWebの依存宣言の単体試験

NK-OPS-001、WBS-C02-a、RD OPS-009、UI251、SS342 §4.1。BUG-3733／YKT-2928。PT-OPS-UNIT-SUP006、SupplementaryUnitTemplateTest。Caddy起動drop-inだけを固定設定のクラスパスから読んで独立期待を照合する。

| 観点 | 入力 | 期待 |
|---|---|---|
| 正常 | 起動用 Unit節と従来Service節 | `After` と `Requires` が各一回で `schubert-nk-web.service`。既daemon ABI、時間、sandboxも個別固定値と一致 |
| 欠落・弱い依存 | AfterまたはRequiresを削除、RequiresをWantsへ置換 | それぞれ対象名義で不合格 |
| 過剰・自動enable | Afterを別対象で重複、Install節を追加 | 規定との差を検出 |
| 横展開 | 既停止用drop-in、Backup、Admin、親targetとWebの追跡雛形 | 既入力の契約を保持。Web→Caddyを加えた宣言29辺は循環せず、逆向き辺を足した合成graphは拒否 |

赤試験はJDK25.0.4／JUnit1.13.4で対象1件、コンパイル0、失敗1。起動用設定にUnit節がなかった。試験・正本・原結果を固定した後、正本の二宣言を追加して同クラス6件を実行する。合成設定内容だけ扱い、実Unit・OS、署名、配備は別の受入証拠。 [元証跡](evidence/PG43734-caddy-web-order-before/manifest.json)
