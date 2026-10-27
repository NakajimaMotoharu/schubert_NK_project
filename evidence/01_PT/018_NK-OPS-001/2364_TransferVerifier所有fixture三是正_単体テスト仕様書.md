# Transfer verifier 所有fixture三是正

2026-10-28 / PG-D752 / BUG1991-YKT1739。着手HEAD/savee47073590633c331c461f41b362196826f70c7f4/push42224真正0、Main-Testsource917f2e755d4912e522b9893e55aa272fd8e80934。群TRANSFER_VERIFIER_OWNED_FIXTURE_THREE、低2/標準5/高8pp・cap10を着手前固定。主費F03、canonical owner-costP00803は維持/共有参照追加0、元見積/v3/v4・受入・N/T/専有費null不変更。

## 原全3case・独立oracle

TransferContentVerifierTest全methodをPT-SCN-008-W06のqualified class#methodで一意指定する。RD FIL001..009/UI237/SS333§6.1（origin/main）と008正式仕様W06に対応。1/201/10000件の独立4800byte（先頭1/末尾2/他ASCII space）、4800×件数のlengthと自前JDK SHA-256計算、全32位置hash差、3byte部分read/maxbuffer4800、null/早期EOF/zero/追加byte/末尾zero/IOException/closedを検査、caller channelを勝手にcloseしない。Productionメソッドからexpectedを生成しない。保持inode属性/認可/record decode/原本pathをhash部品の成功で代替しない。

Main TransferContentVerifier/LargeResultContent/LargeResultDescriptor/StorageIoException（Reasonを含む）とTest/helperを親が全文確認。Mainは渡されたchannelだけを読む。LargeResultDescriptorはcompile-time定数参照だけで外側構成/ファイル操作は無い。試験は新規自分の@TempDir、固定名count-1/201/10000へCREATE_NEW後に自己open/read/TWRする。合計48,969,600byte（10202×4800）、既存file/本番path/原本DB/Backup/鍵/VM/Root/native/FFM/permit/intentへ接続しない。JDK FileChannelの通常OS I/Oと既保留の実配置/native試験を混同しない。

PT_DEFAULT：新規0700 own SLOTと専用java.io.tmpdirを作り、Jupiter @TempDirのALWAYS cleanupを固定。新public fixtureの作成/通常削除だけで既存領域を清掃しない。全methodを閉catalog/extension自動発見falseで実行するがJupiter組込みTempDir注入は必要な通常fixtureとして維持。試験CWDは別の新empty directory、終了時にCWD/専用temp rootとも空を検査。未知file/権限/Root等の安全条件へ依存せず、既拒否Testの再送/分割/別経路ではない。

## 変更と証拠

if mode1をprivate int ZERO_PROGRESS_MODEへ、inner TestInput→ChunkedInputの八identifier、closed synthetic channelの三assertを保持したtry/finally最終closeだけ。元全tokenへ逆変換し、追加finallyの定形以外を拒否する。新TestID/業務仕様/Main変更0。ScenarioRecordStreamTestは別writer/codec closureの未資格対象として今回未実行、共通原因の未完確認をYKT1739に残す（全横展開完了としない）。

新source固定→六正常format/null/lint-Werror/PT0→原3一JVM一exec・ja-JP/JST・240秒→当Test PMD/CS→独立XML/全source前後/全Main1843 byte不変・全Test1962のinner名old/new一対一/他物理byte・CRC/session/完全API467/Protocol176/Storage80 counters/許可外Product probe0。クラスrenameを削除/追加のまま見逃さず、元SourceFile/親クラスとの関係を照合する。counter未達/分母0/既定filterの限界を結果へ明示、手動除外/旧exec union無し。WBS983当一SHA/元owner-cost/予算受入不変・全監査既HOLD1、static原三IDだけ是正、全F03/451/正式1964-53/個別17-190/工数null/QA051finalは維持。実command/環境/exit/hash/TestID/BUG・実temp後条件は2365と専用manifestへ結合する。
