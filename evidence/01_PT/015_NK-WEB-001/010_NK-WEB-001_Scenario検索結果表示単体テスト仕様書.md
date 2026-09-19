# Scenario検索結果表示単体テスト仕様書

NK-WEB-001/ScenarioSearchResultsViewModel.from/getter、Row/Audio。FUN003/AUT001～003/TST001～005、UI223§3/234§7、SS313/323、PG198。既にwire検証済みのPAGED48/SRCRSP01を表示専用snapshotへ変換する。検索form/candidate取得/HTTP/template/実NKgateの完成ではない。

| Test ID | method | 入力・操作・fixture | 独立期待 |
|---|---|---|---|
| PT-WEB-206 | web206LiteralRowsAndAudio | 両game/role、dialogue/narration、chapter/speaker/audio有無、非連続ID | 全表示scalar、セリフ/ナレーション、順序、固定Scenario anchor/audio/DL URL一致 |
| PT-WEB-207 | web207PageBounds | 0件/100件/中間100/最終1/最大page | Page表示値・Row件数一致、空でもpage1、silent truncateなし |
| PT-WEB-208 | web208PageRecordMismatch | 0件へ1row、100件へ99/101row、最終1へ0/2row、page不整合 | 不一致拒否、件数だけの補正なし |
| PT-WEB-209 | web209AudioAndLineInvariants | audio flag/id/pathの全8組、line0/1/99999999 | 正しい全欠落/全設定のみ受入、line0拒否 |
| PT-WEB-210 | web210NullAndOwnership | null actor/data/list/要素、入力clear、返却clear | null境界拒否・immutable snapshot、protocol参照保持なし |
| PT-WEB-211 | web211ClosedBeansAndRedaction | main/Row/Audioのbean/getter・toString | 表示値だけ、setter/context/DTOなし、全診断REDACTED |
| PT-WEB-212 | web212SyntheticEscaping | title/body/speakerにHTML文字、合成Thymeleaf | literal text保持、注入nodeなし、URL固定 |
| PT-WEB-213 | web213ConcurrentProjection | 64actor/本文/ID別の並行factory | 他request混入なし、全独立literal一致 |

期待値はUI/Currentのliteralと独立PAGED48数値で、Production methodからexpectedを生成しない。typed fixtureの前提と、この境界で追加確認する整合性を区別する。Java line/method/class/branch全100%・NullAway/static・既存回帰必須、枝なし値classは0/0として除外しない。未実装・未実行。011/manifestへcommand/OS/JDK/commit/時刻/結果/coverage/BUG/source・evidence hashを成功後固定する。
