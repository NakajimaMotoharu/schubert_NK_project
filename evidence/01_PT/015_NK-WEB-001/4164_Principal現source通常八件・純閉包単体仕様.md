# NK-WEB-001 Principal/TopBar 通常閉包8件仕様

対象5Main: SessionPrincipal、TopBarViewModel、ClosedWebAuthentication、SessionStoreException、InvalidSessionRowException。RD FUN001002/AUT001～004/MON004、UI222226242、SS313314331352354/SSC328。詳細は018_NK-OPS-001/4492とPG37466normalized-prepareの入力hash・各Test IDへ一意対応する。

元PrincipalTopBarValueTest2＋ClosedAuthenticationValueTest4は期待値/sourceを保持し、新PrincipalCurrentClosureContractTest2（独立hash・null/graph順不変）と同一sourceで実行。全8のcase ID一覧はPG37470.caseIds。固定vectorは233/1926890496/-549611547、Enum hashはJDK identity、production principal hashをexpected生成に使わない。正常・Unicode/NFC・全成分・null/空/長さ/未知・境界・例外/cycle/fatal順・redacted出力を元6と新2で確認する。実session/DB/秘密/Root/nativeの試験ではない。

実行command/OS/branch/source・XML/exec/classinit/coverage/staticはPG37468.beginとPG37470ファイルhashに記録。原POMJava25/ErrorProne/NullAway/JSpecifyの限定Main7（2package-infoを含む）compile、全7physicalSB、全10Java PMD/CS/format。対象は全Codeを含む5class20method、共有Protocol2classの部分counterは別に保持し全classPASSにしない。0/0のpackage metadataは自然NoCodeで除外設定はない。
