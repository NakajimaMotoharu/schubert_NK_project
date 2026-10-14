# PG2510/2511 新Main候補の必要全体回帰

NK-OPS-001、WBS-K01.01主費／P017-10/P017-01.03参照費0、PG-D416/417、SS321/331/341/343。candidate a79b45b5858a186fa82bec1ff36882271ab996a4、既PG2504-v2独立八PTの入力と全snapshotが同一であることを発行前に確認する。

Test ID PT-STRICT-FULL-2510：六moduleの全既存試験と新mdb2504001を実行。独立期待=protocol81/17/174、storage163/23/74、bootstrap298/40/105、api969/159/407、web886/129/315、batch1253/172/568（tests/suites/Main）。総3650/540/1643、F/E/S/flaky/not-run0、静的六module0、format/compile成功。期待数は旧3649の全保持＋明示した新独立一method、Productionから期待値生成0。例外/null/境界/再送/競合は各既Program PTの独立fixtureを保持。

Test ID PT-STRICT-PROVENANCE-2511：真正exit0、source入力全hash・archive・全XMLの実時刻/唯一TestID/失敗要素不在、target classとJar member全一致、実counter/session照合。旧0fd比較は物理差分の検出だけに使用しcoverage/nativeを輸入0。従来semantic三＋NativeIo debug-only一に候補Broker/MDB/MDB$Sessionの三差分を想定するが、実物が一致するまで資格0。NativeIoは独立LNT-only +1を保持。古いXML/別Sourceは合格に加算しない。

実結果2026-10-14：PG2510/client16793真正0→PG2511/client19658独立actual0、snapshot1573a8bf9／Productiona79、23:55:03.314548Z～00:21:03.504390Z／1560.189842秒。全3650/540/1643・F/E/S/flaky/not-run0・静的六module0、全入力/archive/全XML唯一identity/時刻/hash/target-Jar一致、七physical＝六semantic＋NativeIo debug-only一（70LNT/+1/他byte同一）・追加class0を実照合。公開strict-current-reference/full-manifest.json、servermanifest7877b1c3、archive d1285293、独立manifest763c7e7d、qualifier7947e5b7を参照。新a79 host残L3704/M622/C37/B907、実native/全global100/CHR/451は未受入、旧cdbc nativeを加算0。正式1964/53・全leafdelta0維持。

command=`python3 -B tools/quality/pg2510_strict_reference_full_six.py`、終了後`python3 -B tools/quality/pg2511_strict_reference_full_qualified.py`、固定PYTHONPATHは456参照。LAN専用fresh source-full-PG2510/runs/PG2510-six-v1、JDK25.0.4/Maven3.9.12/PG18/Node24.19.0、私有repository/target/fixture、worker1。VM/業務mutation0。初期工具fixture二・pyflakes0、実回帰未実行。結果/manifest/hash/counterは取得後記録。全体成功はglobal四100/実native/CHR/451/正式認定と別条件、新sourceへ旧成果移植0。
