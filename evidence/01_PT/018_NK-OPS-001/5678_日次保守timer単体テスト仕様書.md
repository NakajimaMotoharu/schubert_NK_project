# NK-OPS-001 日次保守timerの単体テスト仕様

PG42306、BUG-3577／YKT-2812。親仕様5677のPT-OPS-MAINT-PREBOOT001から、timerの静的な時刻宣言と接続先を検証する。

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-MAINT-PREBOOT001-T01 | 製品timerの各sectionとkeyを読む。別の合成入力には重複時刻、異なる接続先、追い付き再実行、異なる時差を各一つ設定 | `OnCalendar`は1件、接続先は`schubert-nk-maintenance.service`、`WantedBy=timers.target`。合成入力4通りは全件拒否する。UI251 §2、SS341 §2、SS343のschedule。 |
| PT-OPS-MAINT-PREBOOT001-T02 | 2026-11-22 04:59:59、05:00:00、05:00:01 JST、2026-12-31 05:00:01 JSTの基点でcalendar式を解釈 | 基点より後の最初の日次05:00 JSTとその翌日を、独立した固定UTC期待に照合する。年越しは2026-12-31 20:00:00 UTCから連続する。 |

正本の時刻はJSTとする。停止中に経過した予定を起動時に再実行しないため、`Persistent=false`を明示する。PTは作業用の一時processで構文と次回時刻の計算を行う。serviceの実効接続、OS排他、並行要求の後条件、再起動安全判定、実機受入は親仕様5677の対象に残る。試験対象にJava実行分岐はなく、各設定項目と時刻境界を表で確認する。
