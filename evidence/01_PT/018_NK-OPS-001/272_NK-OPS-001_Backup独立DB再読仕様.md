# PG381 Backup成功commit後の独立DB再読（実施中）

## 外部接続と同run再開（SSC112、未受入）

MMAIN008: noargsと厳密 `--resume <canonical非zero UUID>` を別portへ渡し、同じ親budgetを借用。未知/NPE同一性を維持。未知option/欠落/null/短縮UUID/uppercase/zero/cutoff追加は呼出し前70。期待UUIDはliteral31100027-2222-4a33-8444-555555555555から独立生成。

MRESUME011: 同run/cutoffのdurable resume内で同保持原本proofを2回実行、DB/file ownerが保持中であることを確認。別threadとcallback終了後はIOException、run/cutoffはfixture literal。freshへ自動変更しない。

BARCHIVE001/native MMAIN: signed effective profile/public recipientと実工具hash・全config/credential保持前後再照合後、実dump/config.tar/credentials.tar.ageの独立size/hash→manifest atomic publication→同Connection両SUCCESS確定→別transaction完全再読。全close/承認BOM再照合前にはDB成功を書かない。実VM command/個別Test ID・外部JaCoCo・literal SQL/hash比較を後続manifestへ記録する。現時点NOT-RUN、Main全体0/10はS2/S3未結線につき主張しない。失敗/UNKNOWN/timeoutの保全・実再開もS1完了条件であり、成功のみで閉鎖しない。

Program NK-OPS-001/NK-BAT-001、`BackupBundleCompletion.complete`。RD BAK-001/OPS-009、UI251、SS341§6.11/SS332、BUG326/YKT258。上位仕様は変更しない。

PT-OPS-BCREAD001: `verifiedCommitAndReplay`。独立golden artifact・同一owner Connection・両RUNNING stepから実commitし、別transactionで両handle/時刻/status/count/bytesを再読してrollback(read only)→autocommit復元する。SQLの独立期待は既存fixtureのliteral2 SUCCESS行/END。commit1・readback rollback1・autoCommit変更4を確認し、borrowed connectionは閉じない。

PT-OPS-BCREAD002: `postCommitReadbackFailureNeverClaimsRollbackOfCommittedPair`。write commit後のreadback開始/SQL/rollback/autocommit復元へ個別SQLExceptionを注入。public methodは成功を返さず、独立admin SQLでは実commit済み2 SUCCESS行の保持を確認。fault到達1、commit1、resource解放とartifact非変更を確認する。未確定commitをrollback済みと推測しない。

既存BAT274～281のnull/境界/IO/DB/並行/deadline/割込も再検証する。fixture expectedはproduction methodから生成しない。native Main到達/全coverage/正式scopeは別途未実行である。

実command・source・結果・coverage・hashは実行後に273へ記録する。Failed/skipped/not-runを成功に算入しない。

PT-OPS-BCONTENT001～003: `BackupArtifactVerifier.observePending`。SSC110、SS343の生成側接続。真正worker終了後の固定requestで派生した`.part`にある3固定fileを同保持inodeで最後まで読取り、size/SHA256を観測する（まだ認証・SUCCESSではない）。独立literal公開fixtureの26/35/32 byteと各固定SHA、strict owner/mode/ACL/RW/link/同device・前後snapshot・固定3集合を検証。extra/missing/既存manifest・wrongrequest・metadata drift/read失敗を拒否し、fileを書換えず全FDを解放。観測値は後続manifest出版/全artifact照合/同owner DB再読に必ず渡す。Productionによるexpected生成は禁止。

PT-OPS-BPROFILE001～004: BackupProfileTestのliteral compact JSONをgoldenとし、8version/7hash/固定順LF/全byteを確認。missing/unknown/duplicate/escape/whitespace/CR/NUL/nonASCII/4096上限/hash境界/schema000/nullは拒否して入力を消去し、map不変性を確認する。ReleasePayloadVerificationTest FULLBOM001は実照合済みinventoryのschema/artifact hash mapを独立SQL byte hashと比較し不変性を検証する。旧5arg Contentsは追加mapが空でありprofile承認には使用できない。RootReleaseAdmission.inspectMorningは既存root・実platform/schema gateを再利用するnative到達未実行。
