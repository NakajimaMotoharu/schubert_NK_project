# 1002 SSC299 三entry同body終了要求PT仕様

Program NK-OPS-001、OPS009/SYS002004/UI212251253/SS343 SSC299・SS341、BUG1380/YKT1146。設計正本main **b81df447419c4750d43955acd01f73106aa9f0d9/PR145**、doc-only b31fd1146。承認済SSC083/234同方式を拡張する内部詳細設計、RD/UI/既FQCN/argv/0・10・30・70/元1800/認可・owner・measurement順序は不変更。

対象=MorningProcessMain/RootServiceLauncher/CleanupProcessMainの公開native noargとinstance main、package内終了要求/operation/measurementの検査port。元PG4684は実CLI43PT FES0/Maven0だがSystem.exit非帰還によりMorning main probe全missでqualification1。元結果を成功化せず、新sourceの同body実行・真正JDK25 launcherを別fresh scopeで検証する。

| MainTerminationPortTest / Test ID | 入力・独立期待値 |
|---|---|
| morningRequestsLiteralSuccessWarningOnlyAfterTypedBusinessReturn / MAIN-TERM001 | 新/同run resumeの各typed SUCCESS/WARNINGを固定公開activationで返す。business正常帰還後だけ終了要求0/10を一回、元budget/選択runを保持。架空completionをnative受入へ加点しない |
| morningMalformedKnownAndUnknownFailuresNeverInventSuccessfulExit / 002 | 不正argv70・known IO30、unknown runtime/fatal/null argsはidentity保持して終了要求非発行 |
| rootRetainsSameMeasurementThroughAdmissionTerminalThenNonReadyExit / 003 | API/WEB・測定有無・known admission失敗有無。open→同Optional identityを借用したadmission→必要TERMINAL→exit30、通常returnはreadiness0ではない |
| rootBadArgsAndUnavailableMeasurementCannotReachNativeAdmission / 004 | 不正argv70でfactory/operation0、null args/measurement result・factory IO/runtime/fatalはadmission/exit非発行 |
| rootCaptureAndUnknownAdmissionFailureNeverBecomeExitRequest / 005 | TERMINAL export IOはidentity保持/exit非発行、admissionのunknownはcapture/exitへ正規化しない |
| cleanupSelectsOnlyExactExpiryAndRequestsLiteralNormalizedStatusOnce / 006 | empty/--expiryの別operation、戻り0/10/30は同値・71は30へ正規化。選択operation→終了要求一回、既uncaught handlerをmainで設定 |
| cleanupInvalidKnownUnknownAndNullArgumentsPreserveFailureContract / 007 | 不正argv70/operation0、既IO30、unknown runtime/fatal/null argsはexit非発行。Test thread handlerは各試験後に元へ復元 |
| constructorNullsAndTerminationFailuresNeverEnableAlternatePublicEntry / 008 | 全port依存nullを構築時拒否、標準public noargのみ・main非static、終了要求port unknownはidentityを保持して再要求しない |

RootEntryCheckpointFixtureは同packageの**data-providerのみ**。手書きprofile/session/headerとメモリexportでMain順序を検査し、実agent attach/出力file/OS権限/CRC streamを生成しない。期待出口/順序は上表の固定値から作成、Productionからexpectedを生成しない。Unit/DB/原本/秘密情報へ接続しない。既ExternalEntryRejectionTestは実JDK25が同FQCNのnative noarg/instance mainを選ぶことを別child JVMで確認する。OS mainへのMorning/noargs/有効resume/ADMIN/Backupを発行しない。

runner **pg4690_entry_termination_selected.py** は固定source/関連16suite（既11＋上記port/既Morning/Completed/Root/Cleanup）を全六projectで明示、compiler/null/formatと全method/XML FES0/未実行0、三main同bodyのLINE/METHOD/BRANCH各miss0を要求する。proof/environmentの既0も維持。default native execution、必要fresh全回帰・全Main物理差・187署名・新source nativeは後続で別認定。旧964e native9の新コードへの輸入0、除外/private反射/JVM終了抑止0。

実command=既PYTHONPATHで当runner一回、PG379/pg4690-entry-termination-selected-v1に全入力/owner/command/exit/XML/log/coverage/hashを保存。対象snapshot/実結果は実行後記載、現在未実行。
