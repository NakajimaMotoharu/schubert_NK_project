# F03 六module現在source静的ゲート仕様

WBS-F03/2-2、SS352/354・451。製品Main Core7123の六module（Protocol165/Storage25/Bootstrap87/API283/Web262/Batch200、計1022 Main.java）を対象にsource/設計版/原toolchainを凍結。比較ツールprogram/characterizationは別ownerとし六moduleへ混ぜない。Root2 Test/保護二工具/旧原本/master/秘密を列挙・読取・試験せず、四保留型もMain.java sourceのformat/Checkstyleだけでclassfile生成/読取/定義/初期化をしない。

F03-SOURCE-001: git CoreのMain集合と現在ファイルbyteが完全一致、六module/source1022/全SHAを保存。新旧差は一意にし古い合格を無条件転記しない。
F03-SOURCE-002: 原承認GJF1.36.1 --skip-reflowing-long-strings --dry-run --set-exit-if-changedを全sourceへ適用、変更0とactual exit0。ここではreformat/Production source変更をしない。
F03-SOURCE-003: Root Checkstyle全規則/14.3.0で全1022sourceを検査、error/warning0・処理エラー0・全file集合一致。tool source自身とJAR/ruleset全SHA、actual command/terminal/log hashを保存。
F03-SOURCE-004: 独立postで入力不変/源Core/Git byte、tool/rule hash、元terminalとXML/source集合を照合。format-CSをNullAway/PMD/SpotBugs/PT/coverageと混同しない。

Main全体compile/NullAway・PMD型解析・SB/依存byteが必要な残段はQA056のclassfile範囲確認後にだけ行い、既閉host guardは変更しない。Root11/実DB/native等のHOLDを変更0。実操作/拒否対象の探索再試行や暗黙PTを起動0。通常PTを新たにPASSへ加算0。F03は「NullAway/format/Werror/静的解析gateの稼働」という元契約に対する四個別判定であり、全製品各ownerのraw/機能試験・後続G01を無条件なF03の先行へ追加して循環依存を作らない。同時にF03の六module該当静的実証をProtocol限定で代用しない。全製品100/工程451は個別ownerと最終gateで別に維持し、測定不足を100へ補完0。正式受入は元条件/source/必要なtool gateのcanary・独立期待/終了依存を全件実証してからだけ行う。

元既存行2.4ppの低/高とcap5を凍結。source-only一部終了では行完了や元項目受入とせず、保留・残条件を返す。追加の見積減額/工数率推測0。
