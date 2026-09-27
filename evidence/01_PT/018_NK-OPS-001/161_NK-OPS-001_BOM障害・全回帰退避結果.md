# 161 BOM障害・全回帰退避結果

Program NK-OPS-001 / StartupReleaseManifest・ReleasePayloadVerification・CleanupRepositoryTest。RD SYS002/004、OPS009、DAT009 / UI212/251/253 / SS331/34311.1 / SSC095096。2026-09-28。

source8f41401dfの全6 clean回帰は05:37:42 exit1、2217PT/F1/E0/S0。失敗はBatch境界oracleが実Bootstrap所有のSchemaHistoryAdmissionをAPI依存と誤判定したBUG298。全340 XML（329 JUnit/6 coverage/5 static）、compiled class hashesをprovisional/PG314-regression-2217-REDへ次実行前退避。Batch staticは未実行、coverageだけ同class/sourceのままreport追加。過大JSON draftは破棄し完全なmodule/file/class hash chunkだけを保存。合格へ算入しない。

BUG299/YKT232はSS3436.8の承認済Inspector wrapperをfullBOMが拒否する不足。FULLBOM006へ独立literal2固定bin・750 positive/640 negative・未知bin negativeを追加。Storage8＋Bootstrap8のREDは05:46:58 exit1、Bootstrap E1がInspector拒否を再現。前のcommandは依存suite未選択でStorage guardにより拒否（BUG300/YKT233）、Bootstrap未実行と区別。既定No-tests guardは維持。

修正は2固定bin whitelistと750判定を共通化し、Batch境界は独立literal＋実Bootstrap file条件にSchemaHistoryAdmissionだけを追加。Missing/unknown wildcard/API実装依存を許可しない。05:48:19 exit0、ResourceScope8＋FullBOM8＋Cleanup17＝33PT/F-E-S0、NullAway/SpotBugs各0。provisional/BUG298299-GREENへselected XML/3coverage/3static/source/log hashを退避。clean無しの累積execであり正式isolated coverage runではない。FullBOM未網羅37branchを除外しない。状態は直接限定再試験済、security全回帰/native/activation待ち。

VMは全業務表0/games2既定seed確認後、正常shutdown/QEMU退出を確認しoffline QCOW2 snapshot `pre-PG315-20260928-0539`（05:41:40）を作成。disk/private snapshotはGit外。QEMU999117で再起動、marker/PG起動/Artemis停止とNative027原本3hash不変を確認。これは復元点であり業務backup成功/Production更新/IT-ST合格ではない。JAR package/dependency assemblyは05:49:31 exit0だが-DskipTestsでありPT結果とはしない。続いてSSC097候補外署名・候補検査/実release/初回V023→真正root原本/schema→親実工程/main/CHRへ進む。
