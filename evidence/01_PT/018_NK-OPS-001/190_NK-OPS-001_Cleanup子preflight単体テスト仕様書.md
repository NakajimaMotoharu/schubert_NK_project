# 190 NK-OPS-001 Cleanup子preflight単体テスト仕様書

Program ID NK-OPS-001/NK-BAT-001。対象`CleanupPreflight.verify`/固定factory。RD OPS-009/BAK-001、UI251、SS341/343、SSC104-PG333。Test ID PT-OPS-CPR001以降。実装前仕様。

fixtureは公開固定`NKCLEAN1` request・原本activation値・手書き順序eventと、PG332の独立file/PG試験結果を接続点に使う。期待順はSS343の列挙から作成し、Production methodの呼出結果をexpected生成に用いない。秘密値・raw session/DB dumpは保存しない。

| Test ID | 操作/入力 | 独立期待値 |
|---|---|---|
| CPR001 | 正規CLEANUP snapshot/request/原本/専用DBと実backup成功 | gate→request→original→DB/backup→request→original→gate、同request/activationで限定観測成功。呼出側root/sessionは借用、DELETE 0 |
| CPR002 | 前後のrequestまたは原本を同size/同run別activationへ交換 | 後段を固定拒否。成功/Unit exit0/削除開始なし |
| CPR003 | 入口/終端root再確認、private read、原本、DB/backup、closeの各故障 | 固定非成功。後段への到達回数・source/owner後条件を独立検査 |
| CPR004 | null、別actor、割込・時刻無効、同fixtureで再送 | nullは境界契約違反、別actor/割込/clock異常は拒否。再送は削除0で同一限定観測 |

実行command・環境/commit、coverage4指標、F/E/S/static、BUG/SSC、sanitized evidence path/hash、未実行範囲は191へ記録。全体coverage100%、親M/A/真Unit/DELETE/transferは別条件、除外なし。
