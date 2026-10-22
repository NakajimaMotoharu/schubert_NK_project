# BackupRequest普通読取 独立仕様

実行工具固定：`python3 -B tools/quality/pg6744_request_read_selected.py run`→元真正0後だけ`read`（原6746）。選択47/11=六guard12＋既Native20/新ABI2＋既request10/新reader3。Main/全旧oracle不変更を機械guard、元archive/原Jar/全8511667/全XML・counterを照合する。関連既request Testの正常public TempDir publish/retireは従来の自己所有fixtureのみ、新三Testのmutation0と分けて記す。既Native loader契約は1476と同じで実bus/Unitを呼ばない。実原本/Backup/DB/鍵/VM/Root/intent/permit/cohortはアクセスしない。

NK-OPS-001/WBS-P017-03.03（親P017-03参照費0）、SS341§6.1/343・SSC092/113/114、BackupWorkerRequestFiles.prepareResume/prepareResumeReplacement/read、PG-D502。基点Test snapshot c45cd204b、全Main01e同byte。原6726 coverageの未達は97/126非MISSING再throw、102二読不一致、138再読不一致/最終directory不一致。既正常/欠落/foreign/clock/proof testは重複新規加算せず関連回帰する。

群1688開始低.2/標準.8/高2pp固定（未較正）。目的は普通public record readerのfail-closedと後条件、実Backup/Root/failed cohort/DB/intent/permitを回収・退役する試験ではない。自己所有TempDirと既BackupPublicationFixtureのIO/metadata入力口だけを使い、UID0は入力値で実権限変更しない。seedは下記公開literalをFilesで配置、Production encode/prepareからexpectedを生成しない。新試験は全て拒否帰還を期待し、createPrivateFile/openWriter/publish/unlink/sync/forceへの到達はfixtureで事前失敗にする。

```text
NKBACKUP1
run=11111111-2222-4333-8444-555555555555
started=2026-09-27T14:59:59.123456Z
```

新part=22222222-3333-4444-8555-666666666666、replacement expectedは同run/2026-09-27T15:00:00Z。公開UUID/timeのみで秘密情報0。各caseはfresh fixture、mode0600・固定byte、比較前後のino/ctime/mtime/sizeと内容は同一、part不存在、全owned channel/FD解放・publish/unlink/write/force/sync0を確認する。

|Test ID / Java method|入力・操作|独立期待値/根拠|
|---|---|---|
|PT-OPS-BREQ-READ-001 / breqRead001UnavailableIsNotMissingAndNeverPublishes|両resume entry各fresh。既recordの初回reader取得に既Io fault UNAVAILABLEを入力|StorageIoException.Reason.UNAVAILABLE。MISSINGだけ新規publishできる契約なので非MISSINGを伝搬、proof0/全mutation0・元byte/inode不変|
|PT-OPS-BREQ-READ-002 / breqRead002SecondValidRecordMismatchNeverRetires|両entry各fresh。二番目のIOだけ有効な公開別runを返す。元file/metadataは変えず、golden文字列のrun開始byte14を1→2へfixtureで一回差替え|StorageIoException。expected/previousと再読が一致しないので拒否。replacementだけproofは旧公開requestで一回、退役/新規発行0、元file不変|
|PT-OPS-BREQ-READ-003 / breqRead003FinalDirectoryChangeNeverRetires|両entry各fresh。両readは同一record、外側before→read1 initial/end→read2 initial/end→最終という六回のparent metadataの最後だけinode入力を+1|StorageIoException。最終directory snapshot不一致で拒否、replacement proof一回・元byte/inode/全mutation0。hookはIO入力に限定し本当のdirectory変更/競合/raceを起こさない|

副vectorは二entryずつの計六だがJUnitは新三件、各expectedはSSの二読/同一directory前後条件と公開literalから作る。Production methodをexpected生成に使わない。seed変化の注入回数/proof引数/呼出数もassertし、単なる例外だけで合格にしない。null/欠落/正常/競合・既metadata/encoding検証は既BackupWorkerRequestFilesTestを同source関連実行する。

PG照合：既Mainは初回readのMISSINGだけprepare、他reasonをそのまま再throw、同expected/previous二読・before directory一致の後でのみretire/prepareを呼ぶ。この最小範囲のコード変更は不要、実上位callerの所有/DB proofは本fixtureから認定しない。新矛盾発見時は915先行、必要PG/横展開/SS分類を適用する。

PT_DEFAULT、new-only selected工具/同source archive/六format/compile-null/Werror/SpotBugsを維持し、元真正0後に原readerで全XML/Jar/8511667とMain差0を確認。実command/source/coverage/結果/hashは後続結果へ記録。実VM/Root/native/原本/鍵/HOLD・PTALT代替0/正式1964-53/17-190/工数null/QA051final/原-v4不変、通常群終了で停止しない。
