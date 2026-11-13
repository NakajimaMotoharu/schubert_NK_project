# Scenario entry 現行ID順移行対応・独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT005/FUN004、UI223§3.2/254§4、SS331 script_entries/SS343§10。未実装artifactの新PG/PT。元IDを維持する必要はないが、現行script_entries.id昇順をdisplay_orderへ固定する。target ID順を採用しない。ファイル別entry_index、game/file順、音声link/pair/media順は別条件、当部品で閉じない。

予定Productionはbootstrap migration/ScenarioEntryMigrationMap、IdPair(currentId,targetId)、MappedEntry(currentId,targetId,displayOrder)。currentIdは既採取のsigned longを狭めず、targetIdは既V002 identity/CHECKとwireに一致する1..999999999999、source/target重複は拒否。source昇順へ1始まりdense displayOrderを割当、Listのint件数はSS331 N12上限内、公開MappedEntryのorderは1..999999999999を検証する。immutable List/Mapを明示copy、original入力/返却List/byteは別所有。lookupは既sourceのみ・未知を0へ補完しない。実DB存在や完全件数、FK、file/entry/game一致、DBロードを証明しない。

canonicalはNKMIGSCENARIOORDER1 LFの後、sourceId TAB targetId TAB displayOrder LF、source昇順ASCII正準decimal（sourceはsigned）だけ。入力再順序化/再採番後も同sourceから同tuple順、actualMasterアクセス/DB/移行/RootVMnative鍵Unit操作0。

| ID PT-MIG-ORDER | 独立期待値 |
|---|---|
|001| (10→100,2→900)から手書き2/900/1と10/100/2の全byte golden。target順と区別 |
|002| source LongMIN/負1/0/LongMAXのsigned比較、target N12上端、allaccessorsと固定redaction |
|003| source重複拒否、元list不変 |
|004| target重複拒否、source順とは別のbijection |
|005| IdPair/MappedEntryのtarget0/負値/N12超（LongMAX含む）拒否、source値を勝手に変えない |
|006| MappedEntry order0/負/N12超拒否、1/N12許容 |
|007| list/null要素拒否、NPEcatch正常化0 |
|008| 元mutableList/返却List/返却byteへの変更が保存順・goldenに影響しない |
|009| 既source毎lookupの独立target/orderと未知source拒否、固定診断/cause/suppressed |
|010| 空mapはheaderのみ・lookup拒否、移行完了の証明ではない |
|011| sourceIDのgap/renumberedtargetに影響されないdense順位、再順序入力の同一byte |
|012| 所有8worker/64taskで固定goldenとlookup、Future各5秒/finallyshutdownNow-await10assert・未終端fail |

詳細SSC343を先行起票しdesign-only main公開、owner登録後PG。全3physical/JDKJSpecifyJUnitだけ。RootNullAway/lintWerror/PMD/CS/SB/formatと元全12固定source一回/別postのCRC初期化/全四counterを確認。期待は上表literalと算術から独立作成、production encoder/sortから生成0。失敗/未網羅は保持、手除外/抑制/旧exec合算なし。実行環境/source/branch/tool/command/exit/input/output/hashはmanifestへ。

追加不足価格 .8/2.4/4.8: 詳細 .1/.3/.6（上限1）、source/Test .4/1.2/2.4（上限3）、normal .3/.9/1.8（上限3）。original/2の全ETL/実master/FK/IDmapping/表示順/再実行criteria費用、S/V原枠は保持。actual費/token不明null、元190/全451/ITST未受入。
