# F02 現候補の四モジュール統合buildとBackup差分

WBS-F02-a、SYS-002/005、SS311/332/354、F03/2-2、SSC461、BUG3233／YKT2680。現Core `29f3b433952ad19d4ad34c4e1a31ed310bebde6a`。PG39122はLinux/JDK25.0.4/Maven3.9.12、原Root・4moduleのoffline compileが真正終了0。482 Main・8 POMを固定し、全1,102物理のうち1,101点が旧PG38952と同一。唯一のBackupCommitService.classはPG38977の通常16件・Root静的適用0の閉包とbyte一致。旧証拠の合格試験は再実行せず、同候補の四moduleのコンパイル証跡を新規保存。

PG39124 ArchUnit 1.4.2は1,102物理、49,822参照、36,712アクセス。Batch→Bootstrapが726→729、Batch→Storageが1,653→1,650。Bootstrap→Storageは320。真正終了1はStorageIoException→java.sql.SQLExceptionの既知境界1件のみ。新規禁止辺・製品クラス初期化0。旧Storage入口の撤去は残callerのPG/PT後。現在は上位29/104を移管し75残、Storageの直接3と旧入口は別。全六moduleの型付き結果と実環境・451未受入。

[PG39126](evidence/PG39126-f02-current-four-backup-independent-v1/manifest.json) SHA-256 `6ec0f964aed1265fb40a953d54cbb3ff0b94d72b524e129d35eedf2f50dd83b5`。command、実終了、全入出力hash、ArchUnit生一覧、保全stdout/stderrと旧runとの対応はmanifest参照。
