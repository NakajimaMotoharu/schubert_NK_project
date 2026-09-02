# 不適格run分離記録

| 実行日時 | 範囲 | 結果 | 原因 | 扱い |
|---|---|---|---|---|
| 2026-09-03 00:22:17 JST | 未commitのPT証跡exporter | ERROR 1 | PostgreSQL catalogの内部`"char"`型をtextへ明示castしていなかった | Production DDLは15 assertion通過後、未確定test helperのexportで失敗。PASS非算入、BUG非該当 |
| 2026-09-03 00:22:42 JST | 未commitのPT証跡exporter | ERROR 1 | 1列へ連結後の`UNION` queryに`ORDER BY 1,2,3`を指定 | Production DDLは15 assertion通過後、未確定test helperのexportで失敗。PASS非算入、BUG非該当 |

両件ともTDD中の未実装証跡出力機能の初回失敗であり、実装済みproduction処理の承認済み仕様違反ではない。
修正後commit `06da7ac`および分岐拡張commit `72af383`/`b1bec26`の後、正式run `PT-DB-20260903-01`は
failure/error/skipped 0でPASSした。
