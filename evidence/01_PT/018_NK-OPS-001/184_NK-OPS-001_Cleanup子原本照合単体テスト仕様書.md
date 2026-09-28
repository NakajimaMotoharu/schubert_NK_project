# 184 NK-OPS-001 Cleanup子原本照合単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。Class/method: `MaintenanceRunFiles.Session.observeCleanup`、既存`scan`/`graph`/`perform`。RD OPS-009/BAK-001、UI251、SS341/343 §6.15/SSC104-PG330。Test ID: PT-OPS-MRF001～004、既存PT-BAT-058～113を回帰対象とする。

前提: `MaintenanceRunFilesTest.Fixture`の保持dir/fileで、SS343の独立literal `NKRUN1` anchor、`NKACT1` begin/active、`NKDONE1` doneを直接配置する。期待値はProduction writer/`resume`で生成しない。Linux root権限/真正M/A/全close後の外側Unit gateはこの限定fixtureの範囲外。

| Test ID | 入力・操作 | 独立期待値と根拠 |
|---|---|---|
| MRF001 | 同run UUID・activation UUID・UTCµs cutoffのanchor/begin/active、doneなし。`observeCleanup`後のfile map/IO回数 | SS343の三literalが同identityで、書込/create/force/publish/unlink/syncは各0、返るactivationが独立literal一致 |
| MRF002 | run/activation/cutoffを各1値だけ変更した固定request | いずれも固定`StorageIoException.UNAVAILABLE`、原本不変・publish0。requestのmanifest SHAは相関であり原本照合権限ではない |
| MRF003 | anchorのみ、beginのみ、activeだけ孤立、active＋同beginのdone済 | 各固定非成功、publish0。graphの`pending=同run`は当該active begin未完了を含意し、done済を拒否 |
| MRF004 | null request、2回scan間のactive交換、所有close故障 | nullは境界NPEとして拒否・正常化しない。交換/close不確定は固定非成功、publish0 |

正常・境界・異常・例外・null・再送/並行はMRF001～004と既存MaintenanceRunFilesTestのrun recovery/同scope並行試験を合わせる。`observeCleanup`の成功はM/A、両backup現物、DB lock、子真正Unit、DELETEの許可ではない。実行command、OS/JDK/tool、対象commit、coverage、F/E/S・静的、BUG/SSC、sanitized証跡path/hashは185に記す。Coverage除外なし。原本file内容/raw UUIDは本番証跡に格納しない。
