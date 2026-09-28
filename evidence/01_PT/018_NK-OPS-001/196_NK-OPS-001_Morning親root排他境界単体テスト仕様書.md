# 196 NK-OPS-001 Morning親root排他境界単体テスト仕様書

Program ID NK-OPS-001。対象`MorningRootScope.execute`（固定native入口・package限定port）。RD OPS-009、UI251、SS341 §3～5/343、SSC-100～102、PG336。親Mの実取得自体は既存`MaintenanceFileLock` PT-OPS-LOCK-001～008、固定8 policyのparser/全件順はPT-OPS-MCLIENT009～011で検証し、本仕様は両者を一つのroot主体scopeに束ねる順序とcallback所有を検証する。新たなUnit停止、A取得、backup/permit発行を実装済みとしない。

| Test ID | fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MROOT001 | 手書きliteral event列、fake root gate・M owner・固定8 policy・継続callback | root→M取得→root→全8 policy→root→callback→root→M close→root。callbackとpolicyの実行中Mが保持され、戻り値7。順序はSS341§3～5から導く |
| PT-OPS-MROOT002 | M競合で`Optional.empty`、policy/callbackは呼ぶと即失敗 | 固定IOException、policy/callbackは0回。二重起動で保守対象を停止しないというSS341§3の期待 |
| PT-OPS-MROOT003 | policyが既知IOException、M ownerでcloseを観測 | callback0回、同例外identity、M close確認。未配備・不適合Unitを成功へ補完しない |
| PT-OPS-MROOT004 | continuationがIOExceptionを投げる | 同例外identityを保持し、M closeは例外の後。これは後続失敗時の通常scopeであり、未解決stop-client `UNKNOWN`をcallbackから返すことを許可しない |
| PT-OPS-MROOT005 | 4つのpackage境界null、callback null、M close後のroot再検査故障 | nullは契約違反。null結果/後検査異常を成功へ変換せず、後検査の同IOException identityを保持する。M close後だけ結果を返す |
| PT-OPS-MROOT006 | root検査1～5回目それぞれへ独立IOExceptionを注入 | 失敗した段以降のpolicy/callbackを呼ばず、M取得後の失敗は必ずM close、同例外identityを維持。1回目失敗はM取得0回。SS341§3の前後identity要求 |

期待eventはProduction methodを呼んで生成せず、上表のSS固定順をliteralとして記述する。境界/null/例外に加え、既存lock PTの競合・再入・同run再試行と接続して確認する。native UID0/真正Morning Unit・全8 loaded/stop policy・固定kernel終端、UNKNOWN隔離、親M/A連続保持、実backup/cleanup・Artemis/API/Web起動は後続の実VM証跡まで未完了。`NullPointerException`をcatchして正常扱いせず、JaCoCo除外なし。実行日時/command/環境/commit、6件F/E/S、SpotBugs、4指標coverage、関連BUG/SSCとsanitized evidence/hashは197に記録する。
