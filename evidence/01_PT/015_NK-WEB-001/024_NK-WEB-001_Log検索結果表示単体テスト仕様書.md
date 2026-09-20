# Log検索結果表示単体テスト仕様書

NK-WEB-001/SCR014、LogSearchResultsViewModel/from/Row、FUN008/AUT002～003/MON003～004/TST、UI225§2/235§11/264、SS311/313/323/352、PG-D-212。仕様先行・未実装/未実行。LogSearchResultsViewModelTestの8methodへ一意対応。

| Test ID | method | fixture・操作 | 独立期待値 |
|---|---|---|---|
| PT-WEB-262 | web262CompleteRow | ADMIN/PAGED48/全Log field | ID/UTC日時/種別/level/各HTTP・MQ値/詳細のliteral |
| PT-WEB-263 | web263OptionalFields | 10optional fieldの1024組合せ | 文字列欠落は空、status/elapsed欠落はOptional.empty、存在値不変 |
| PT-WEB-264 | web264PageBounds | 0/1/100/101、中間/最終/上限page、不一致 | page100固定、件数一致、超過・不整合拒否 |
| PT-WEB-265 | web265OrderingAndIdentity | 日時降順、同時刻ID降順、逆順/重複 | API順保持、逆順とduplicate拒否、sortしない |
| PT-WEB-266 | web266NullRoleAndOwnership | null/要素null/USER/元List変更 | null契約、ADMINのみ、不変snapshot |
| PT-WEB-267 | web267ClosedBeansAndRedaction | getter集合/field型/診断 | TopBar/Page/閉Rowだけ、wire/contextなし、固定redact |
| PT-WEB-268 | web268SyntheticHtmlEscaping | message/path/details/usernameにHTML文字 | textとして保持・escape、HTML/JSON評価なし |
| PT-WEB-269 | web269ConcurrentProjection | 64actor/record/並行 | actorとrow値独立、共有fixture不変 |

Current AppLogService.mapEntryはOffsetDateTime、logs.htmlはその文字列表現。Current依存JDBC42.7.7のPgResultSet.getOffsetDateTimeは通常timestamptzをUTCへ変換することをlocal jarのjavapで照合済み。RowはInstant.atOffset(UTC).toStringとし、分ちょうど/秒/毫秒を独立literalで試験する。UI235 wireのmillisecond精度から勝手に桁を足さない。DIF010の業務Message/Correlation追加はUI225/235に従う。Page expectedはUI PAGED48算術で独立指定し、Production factoryで生成しない。

既存wire validation済みのDTOを受けるprecondition、文字列はここでtrim/redaction再加工やJSON parseをせずAPIの安全な値を閉snapshotへ写す。null/境界/異常/例外/並行、再送は副作用なし投影で非該当。Java25/Maven3.9.12、selected8PT後全体clean verify、4coverage100%・NullAway/Spotless/SpotBugs未解決0、failed/flaky/skipped/not-run除外。025結果/manifestへ環境/対象commit/日時/command/exit/coverage/BUG/SSC/path/hashを保存。form/実template/HTTP/実NKgate・PGPT/IT/ST未完了。
