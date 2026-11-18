# BUG-3234／3235 SchemaHistory所有の実行結果

対象はJava25のSchemaHistoryAdmissionとRow。WBS-F03、WBS-P004-05、SYS-005、UI241/243、SS311/332、SSC129/461。試験source 380a0369e42ad8fa0ed093f3368d335f53c93721、製品Core 9ad70c3fa00bb45010767fab382fd334352c2763。同session PG38668、原PT-OPS-SCHEMA001～010とRow 011の全11件が初回成功。失敗、エラー、skip、選択内の未実行はいずれも0。

既存SQL・借用Connection・08001・行から文への解放順・既存例外選択を保持。原ケースの期待値に加え011は固定値と独立31進計算を照合した。対象2物理classの公開ABIは変化0。未フィルタで行92、method18、class2、branch70、instruction421がすべて実行。支援型4件の未到達はmanifestに保持し、F03全体へ加算しない。旧execとの結合・設定除外なし。

静的検査は厳格NullAway、Checkstyle、formatter、SpotBugs Max/Lowが0。PMDの元27件は各source位置・理由・実行契約を照合し、適用0。修正途中のOBL1件とRCN2件の元証拠を別sourceとして保持。途中sourceでは動的PT未実行。独立unfiltered読取の初回は明示class引数の誤りで終了1、引数を直して保存execを照合した。

独立証拠 evidence/01_PT/018_NK-OPS-001/evidence/PG38670-f03-schema-owner-raw-independent-v3/manifest.json、SHA256 7f55734dd7bc0adcaf0cb5506c2f543da117d9a75aeb1d4e58b0ab2ec56ec643。別run・旧source・実VM・実DB・正式試験へ加算なし。受入増0。
