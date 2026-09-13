# NK-BAT/OPS root・namespace資源解放横展開 PT追補

PG172/SSC063継続、BUG195/YKT154、実装前仕様。NK-BAT-001/NK-OPS-001、OPS009・UI251・SS311/341/343。正式13/source82055460へ未実行観点を遡及加算しない。

SSC063継続/PG172・BUG195/YKT154: MaintenanceFileLockのrun/app取得・再照合、InspectorEnvironmentFilesの5 root取得・再照合、MaintenanceRunFilesの6 root取得・再照合とnames列挙を共通ResourceScopeへ横展開する。取得順・取得直後のadmission順・逆順一度close・Session無効化の時点・static参照byte消去・失敗時run環境保持・borrowed能力を変更しない。DirectoryIteratorExceptionは列挙body内で既知IOへ固定化してからcloseし、未知cleanupを隠さない。未知bodyと同じThrowableをcloseが投げても元identity＋固定secondary1、既知IO bodyと未知cleanupは同じ未知cleanupを伝播する。Runtime/NPE/Errorを正常化せず、入力null契約と公開仕様を維持する。process/JDBC候補は別段で未完了を維持する。

## Test ID・独立期待値

- LOCK006 MaintenanceFileLock.tryExclusive/verifyCurrent: callback失敗後に外側app/runの各closeへ未知を注入。2位置×既知IO/同一未知body×IllegalStateException/NPE/AssertionError3型=12case。callback中のclose数からentry→app→runの3終了を独立計数、native FD全解放、外部flock再取得0、lockfile 0byte維持。
- NS002 InspectorEnvironmentFiles.execute/verify: callback失敗後に外側5rootの各close。5×2×3=30case。取得済全FD/readers/writers解放・callback1・5close、公開run環境は固定RUNTIME byteのまま保持、unlink0、静的CONFIG byte不変更。
- BAT079 MaintenanceRunFiles.execute/Session.verifyNamespace: callback失敗後に外側6rootの各close。6×2×3=36case。6close、全FD/readers/writers/listings解放、Sessionは閉鎖状態、recordsの新規生成なし。
- BAT079 MaintenanceRunFiles.names: 最初のnamesIteratorの既知IO（DirectoryIteratorException）または同一未知bodyとnamesClose未知を組み合わせ、2×3=6case。取得済stream一度close、全資源解放、何もpublishしない。

追加合計84compound caseは既存3 Test ID内の観点であり、新JUnit数/部品数は0。期待値はProductionから算出せず、Throwable identity/固定Storage secondaryのreason・cause/suppressed、close注入1回/実native解放/固定byte・ファイル集合を独立assertする。未知primaryの場合は同一元例外＋固定StorageIoException secondary1、既知IOの場合は同一cleanup未知・secondary0。借用資源は解放しない。

外側root取得13個と再照合root13個・列挙1個の全27scopeを修正対象とする。再照合の各unknown組合せを別々に網羅したと主張せず、共通ResourceScopeの全契約PT＋既存全open/close/metadata IO故障matrix・前後identity交換・全分岐PTを併用する。null/missing/parallel/割込と成功時cleanup/失敗時保全を既存PTで再実行する。

## 実行・証跡方針

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12（421）。変更前red→変更後3class・PG171の4class・ResourceScope・MaintenanceRetirementRecordsTestの選択PT→全reactor/4coverage100%/NullAway/Spotless/SpotBugs。format後に同時Mavenなしで実行。未実行/failed/flaky/skippedは成功へ算入しない。

source/branch/command/日時/exit/coverage/BUG/SSC/結果/hashは本追補と017/018の正式manifestへ固定する。既存Current baseline・RD/UI/test oracle/coverage除外は変更しない。PG171の未選択retirement分岐も関連PTと全体試験で再確認する。process/JDBC/親/backup生成/IT/STは未完了。
