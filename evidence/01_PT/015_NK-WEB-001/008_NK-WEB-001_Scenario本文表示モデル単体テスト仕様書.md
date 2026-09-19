# Scenario本文表示モデル単体テスト仕様書

NK-WEB-001 / ScenarioDetailViewModel.from、getter、内部Entry/Audio/Navigation。FUN004/AUT001～003/TST001～005、UI223§4.2/234§10、SS313/333、PG195。表示専用の部品で、画面・file読取・API認証・PGPT完了ではない。

| Test ID | method | fixture/入力/操作 | 独立期待 |
|---|---|---|---|
| PT-WEB-194 | web194HeaderAndNavigation | 両game/role、前後有無4組 | title/game/display path/数値URL・Topbar、欠落はOptional.empty |
| PT-WEB-195 | web195GroupingAndAudio | 3entry、0/1/2voice、非連続ID | 本文3回分の閉Entry、audio全3、入力順/line/speaker/type・entry anchor固定 |
| PT-WEB-196 | web196EmptyAndBounds | inline0/200、file1/10000、201/10001/件数不一致 | 承認上限受入、不正は投影拒否。file metadataはModel非保持 |
| PT-WEB-197 | web197NullContracts | principal/data/list/要素null | 境界拒否、NPE catch正常化なし |
| PT-WEB-198 | web198NavigationPairs | 前後ID/title欠落組合せ | 不一致拒否、空/未知を補正しない |
| PT-WEB-199 | web199SequenceRejection | 再登場ID、entry/audio欠番、本文不一致、audio片側欠落 | 共通wire sequence契約の拒否を維持 |
| PT-WEB-200 | web200EntryMetadataConsistency | 同entryのline/type/speaker変化 | 不一致を先頭値で隠さず拒否、正しい複数audio保持 |
| PT-WEB-201 | web201ImmutableSnapshot | 入力clear、返却Entry/audio list clear | 投影値不変、返却変更不可 |
| PT-WEB-202 | web202ClosedBeanContract | JavaBeans property一覧 | 表示scalar/閉値だけ、protocol/context/descriptor/physical pathなし |
| PT-WEB-203 | web203SyntheticHtmlEscaping | 合成Thymeleafでbody/title/speaker/pathにHTML文字 | literal text維持、注入要素なし、固定URL |
| PT-WEB-204 | web204ConcurrentProjection | 64独立principal/本文 | snapshot/context混線なし・全結果独立literal一致 |
| PT-WEB-205 | web205RedactedDiagnostics | 4閉classのtoString | 本文/title/username/path/descriptor非露出、固定REDACTED |

入力は公開合成typed record、期待値はUI定義と独立literal。expectedをProduction投影/codecから算出しない。I/Fは既存decoder/readerによるbyte・hash・path検証後が前提で、本PTはその代替ではない。Java4coverage100%/NullAway/SpotBugs、全既存PT回帰を要求。branch0/0の値getter classがあれば分岐なしとして明記し除外しない。未実装・未実行、失敗/flaky/skipped/not-runは合格算入しない。command/環境/commit/結果/coverage/hashは009とmanifestへ確定後記録する。
