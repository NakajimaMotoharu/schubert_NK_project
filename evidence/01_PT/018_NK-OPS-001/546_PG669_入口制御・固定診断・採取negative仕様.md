# PG669 入口control-flow host群（独立PT並行）

Program NK-ADM-001/NK-DAT-001/NK-OPS-001、BootstrapAdminMain.main/launch/captureNative、InspectorLauncher.main/complete/captureNative。RD AUT001002/DAT009/OPS009/MON004、UI212225226242251、SS343354/451、PG-D401。WBS主担当P010-05/P004-04、共通再回帰K01・実nativeN15は本費へ併算しない。Current VM36fe/PG631/host630/資格17は別sourceの固定履歴、新source結果と混合0。

PT-ADM-BOOT669001：入力status各0/20/50/70、capture有無の独立vectorで、操作args/env保持、run→固定finished LF→capture→有の場合だけcomplete LF、最終status不変を検証。002：業務IOException/Errorのfixture詳細を外部へ漏らさずfailed→finished→capture/非成功50。003：capture IOException/Errorでfinished→failed・fakecomplete0/status50。004005：args/env/runner/capture/diagnosticsのnullそれぞれ、I/Ocallback未発行/出力0/IllegalArgument（NPE正常化0）。期待string/statusは独立literal、Production methodからexpected生成0。

PT-DB-INBOX-669001：未知argvで先にconfiguration拒否70/Factory未実行→明示receipt `NKINSPECTOR1 70\n` write/checkError→capture有無/有時だけ固定診断。002：capture IOExceptionは同failure伝播/receiptあり/complete表示0。003：output.write IOExceptionで固定redact `inspector receipt unavailable`・cause/suppressed0・採取0。004：六nullable入口依存を各欠落、receipt/Factory/capture/診断0。秘密詳細・DB/FS/socket/Unit権限はfixtureから生成しない。

正常/境界/異常/例外/null観点を上記各goldenへ対応。並行/再送はstateless入口合成で共有mutable state無し、各local output/runnerの独立性を検査、業務DB/inbox/replayは既対応suiteを選択する。現mainのdefault Unit/credential/security admissionは維持し、synthetic callbackを実VM成功へ読み替えない。

選択trigger：API入口control-flowリファクタ2classと新独立8testの一群。BootstrapAdminMainTest（実独立PGtransaction/actor）、InspectorLauncherTest/InspectorApplicationTest/InspectorProcessTest（実別privatePG/owned roots）とentry2suiteを選択しcompile/NullAway/Spotless/SpotBugsを実行。全体/source-bound/nativeは未実行。Command `pg669_entry_selected_v1.sh <fixed source>`、W/pg669-entry-component-v1/{started,source,source-files.sha256,build.private.log,exit,completed,surefire-reports,api.exec,jacoco.xml,spotbugsXml.xml,jar}。実source/exit/XML FESflaky/coverage/staticを照合しmanifestに実値保存、四100未達は不合格/未受入扱い。秘密/credential/rawDBログを公開しない、BUG発見なら是正前915/YKT。実selected未実行/正式24-1964-53/ACCEPTED0維持。
