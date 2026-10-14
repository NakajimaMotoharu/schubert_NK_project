# PG2566 当runのBackup内容・保持後条件

NK-OPS-001、SS341/343/353/354、WBS-N05群0661のsubset（追加予算0）、P017/K01参照費0。当a79/PG2512/bootb2d6/runb29fb3e5/cutoff2026-10-14T00:36:06.976135Z/activationd021、実2544/2546/2548/2552/2555/2556/2560完了receiptを必須とする。旧世代の原値は保全のみ、期待値へ混入しない。

PT-BACKUP-2566-001：全24・32設定・署名187・原本Backup/native・全資源のread-only後条件に、独立literal run/cutoff/設定fixtureと保持manifest/archive内容oracleを結合。完全DBhandle、tar byte/hash/ファイル名/metadata/config、普通pg_restore --list終了0を照合する。restore/Backup/Root/ADMIN/停止/reload/writeを発行しない。production codeから期待値を生成しない。

PT-BACKUP-2566-002：oracle欠落、seal欠落はguestへ接続前に拒否。ASTで全payloadにlifecycle command listが無いこと、全namespace、当run/cutoff/config/Source・stop receiptを検査。古いrun/configを許さない。新工具二独立fixture PASS、Production PT加点0。

command：固定PYTHONPATHで python3 -B tools/quality/pg2566_strict_current_backup_content_test.py → clean source固定後 pg2566_strict_current_backup_content.py。actual実VMは未実行、未合格。実時刻/環境/source/終了/hashは結果取得後別記する。coverageは既PG2564当source残L803/M156/C9/B573、global100/451/正式/leaf終了依存は未完。
