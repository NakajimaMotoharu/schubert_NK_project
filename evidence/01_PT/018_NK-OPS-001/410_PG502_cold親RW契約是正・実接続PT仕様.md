# PG502 cold親RW契約是正・実接続PT仕様（限定正常完了）

2026-10-08現追加評価BUG813：所有scope正常帰還/full原値/新INVALIDの実測は保持するが、prepared native catalogはSSC193/196の6roleを欠落し完全性不合格。実装と同じ不足9catalogによる照合を独立網羅期待値として使用しない。現在のnative前提受入は未完へ戻す（正式/WBS認定元々0）。旧Root/tools/private証跡を変更せず、別new-only正常owned区間で是正・再試験する。

実結果2026-10-08 01:22JST：host独立76+16/compile Werror0、native70184 actual0、093..096全新scope正常。詳細safe manifest=`evidence/provisional/PG502-cold-normal-v1/manifest.json`、Root refs-after SHA07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49。以下表の計画欄「未実行」は初期状態の記録で、この実結果を現在値とする。全fault/競合/同source親全体・native coverage・正式は未受入。

NK-OPS-001/NK-BAT-001、WBS-N11/N14/G13.07、RD SYS-011/OPS-009～017、UI211/212/243/251～253、SS331332343353/SSC206207、BUG810/YKT579。
Production a2/PG495は不変更。PG501 actual143/closeUNKNOWN、限定hand-off実0/全原値二読/peer-lock0を保持。別新工具/新Root保存先で親RW/readCommitted/autoCommitfalse、全24私有照合は独立ROを使う。

| Test ID | 操作・fixture | 独立期待値/根拠 | 状態 |
|---|---|---|---|
| PT-OPS-PG502-001..076 | full18冷停止/ASCII INVALID/null/欠落/旧boot/foreign/上限 | SS343から独立literal golden、Production expected生成0。PG501 guardの別source再実行 | 未実行 |
| PT-OPS-PG502-077..092 | JDBC proxyのRO/autocommit/3未知隔離levelと正規RW | 不適合5modeはprepareStatement0/診断causeなし。正規modeは固定SQL一件/UTC bind/明示projection true,true,false,true/owned row-statementだけclose、親設定/close呼出し0 | 未実行 |
| PT-OPS-PG502-093 | 新M/A/専用batch DB/advisory/10Ref＋全原値/profile二読 | currentbootcc9/全10cold、全24table442batch/5永続tree102metadata/hash一致、Root同peer実FLOCK/inodeと他peer0 | 未実行 |
| PT-OPS-PG502-094 | readonly固定PG495/署名typedBOM | BOMf699/187artifact/SQL28/history29/approval raw一致、任意expected変更0 | 未実行 |
| PT-OPS-PG502-095 | 同run/cutoff/activationの新空namespace・新bootINVALID | startupはepoch.currentだけ。独立ASCIIgoldenfields照合、oldRuntimeRetired0/newISSUED0/DB業務更新0 | 未実行 |
| PT-OPS-PG502-096 | DB rollback/close→十Ref逆順/正常bus→A/M正常/receipt | 全新scope正常、全peer/advisory0・全原値維持。旧UNKNOWN/143は補完しない | 未実行 |

commands: bash tools/quality/vm/050_s1/pg502_cold_compile_v1.sh; python3 -B tools/quality/vm/050_s1/pg502_cold_native_v1.py（新only工具/保存先、前提認証後一回）。host16+76は工具assertでProduction PT/coverageへ加算0。native結果/hash/私有rawはsanitized manifestで対応。実所有/fault/競合全matrixや全正式品質は別残件、未実行を合格へ加算しない。
