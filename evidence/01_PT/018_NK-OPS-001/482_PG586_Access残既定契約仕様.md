# PG586 Access残既定契約・同data readback

NK-BAT-001 / P017-01.02 / OPS009,DAT009/UI251/SS341343/SSC129133200、同群初期0.67/1.67/3.67ppを保持。Production不変更、同test class追加3ケースMACCESS586001..003。001=正規型のExpiry gate fixture receipt/cleanup七step snapshotを渡してもnon-native AccessはIOException literalで拒否、owner/lookup0。null receipt/ownerの明示境界拒否。002=実host TempDirの借用FDとCompletion objectはnative parent/JDBC権限ではない。completeBackup拒否・directory空・borrowedFD正常close、実VMや本番Backupへの接続無し。003=data-only DB/Expiry readbackの同値は同owner/receipt/beginsを転送、異値は拒否、nullは操作前fail-fast。guard/callbackはnative許可に読み替えない、redacted toStringの固定literal。期待値は独立public vector、Productionで生成0。

新MACCESS3＋既4とMorningDatabaseSessionTestのみを同reactor依存で実行する。非選択module/testはnot-runで加点0、以前のXMLを今回へ加算しない。command bash tools/quality/vm/050_s1/pg586_access_selected_v1.sh <固定HEAD>、JDK25.0.4/Maven3.9.12/PG18 fixture・format/NullAway-Werror/静的六module、post-run両XMLの時刻/source/hashとclassbyteを照合。旧host六execはPG585封印hash一致確認後、新私有outputへrecoverable renameし、選択execへのappend/mixingを防止する。PG585元私有copyも保持。

新私有PG379/pg586-access-selected-v1、実未実施・合格加算0、source/run/時刻/exit/coverageの実後追記。全回帰は当testonlymatrixの次品質group/source固定時に必要triggerで行い、通常小PTごとに重複実施0。独立hostの既定契約を実native否定matrix代替にはしない、formal/global受入不変更。
