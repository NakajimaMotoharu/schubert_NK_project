# Music category・section表示単体テスト仕様書

現在状態: 正式24/source5f2abbf2で8PT認定済。結果021・manifest参照。以下の「仕様先行」は作成時点の記録であり現在の未実装を意味しない。Music HTTP/配信は未完了。

NK-WEB-001/SCR011/012、MusicCategoryViewModel/MusicSectionViewModel・nested Card、FUN007/AUT/TST、UI223§7/235§7～8/264、SS311/313/323/352、PG208。仕様先行・未実装/未実行。MusicHierarchyViewModelTestの以下8methodを対応付ける。

| Test ID | method | fixture・入力・操作 | 独立期待値 |
|---|---|---|---|
| PT-WEB-246 | web246CategorySnapshot | USER/ADMIN、曲/BGM/その他・trackCount | record順維持、合計129、name/count/href/TopBar |
| PT-WEB-247 | web247SectionSnapshot | 選択category、ゲーム/アニメ/キャラクターソング | Current category/section・個別/合計件数、固定URL |
| PT-WEB-248 | web248SizeAndCountBounds | 0/1/20/21、0/1/100/101、6桁count最大、total不一致 | 0/上限受入、超過/不一致拒否、最大合計19999980/99999900 |
| PT-WEB-249 | web249DuplicateAndSegment | 重複名、空/dot/double-dot、Unicode/special path segment | 重複/危険segment拒否、明示UTF8percent URL、名称は非加工 |
| PT-WEB-250 | web250NullAndOwnership | actor/data/list/選択category null・要素null、元List変更 | 明示null契約、不変snapshot/返却List、DTO不保持 |
| PT-WEB-251 | web251ClosedBeansAndRedaction | bean property/reflection/診断 | TopBar/name/count/href等だけ、wire/session/contextなし・固定redact |
| PT-WEB-252 | web252SyntheticHtmlEscaping | title/category/sectionにHTML文字列 | 合成Thymeleaf text/hrefの明示値、script生成なし |
| PT-WEB-253 | web253ConcurrentProjection | 64actor/要求値、共有不変fixture | username/name/URL独立、元fixture不変 |

期待はCurrent music/music-sections templateのsubtitle/card、UI235件数上限と独立literalから作る。Production factoryをexpected生成に使わない。API順はmigrationで確定済みとして受け、ここでsortしない。byte/NFCはwire側の既存全codec PT、path/form validationは後続HTTP試験と分離する。null/空/未知表示名/境界/重複/並行を明示し、再送は副作用なし投影で非該当。

Java25/Maven3.9.12、selected新8PT＋既存表示/PT、その後clean verify。line/method/class/branch100%・NullAway/Spotless/SpotBugs合格、failed/flaky/skipped/not-runは不合格。command/環境/対象commit/日時/exit/coverage/BUG/SSC/証跡path/hashは021とmanifestへ保存。実template/HTTP/配信/実NKgate・PGPT/IT/ST未完了。
