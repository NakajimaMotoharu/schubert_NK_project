# 162 候補release・初期構築単体テスト仕様書

Program NK-OPS-001。StartupReleaseManifest.verifyCandidate / fixed releases traversal、配備側trusted signer/approval、専用PGPT initial migration。RD SYS002/004/OPS009/DAT009、UI212/251/253、SS331/34311.1、SSC095096097、471 D02/04/05。PG315。

## 候補検査（PT-OPS-FULLBOM006/008、既存program suite内）

fixture: 独立literal NKRELEASE1、JDK ZIP作成、JDK SHA256、固定Flyway CRC literal、tmp通常file。入力approvalは公開claimであって認可でない。Current selectorが不存在または別旧releaseでも、指定tokenの固定releases候補を全検査しcurrentを変更しない。期待は明示VERSION/全payload/SQL byte/共有class集合・mode/owner/ACL/RO/同inodeで独立決定。現在releaseの起動検査は従来通りselector必要、候補検査の成功をroot proofへ読み替えない。

- 正常候補、current不存在/不正、旧selector文字列不変、NULL approval、異版/digest、未知/不足/余剰/無署名claim境界。
- 全取得close位置に独立faultを注入し実到達/全owned空を確認。前後祖先reopen・owner/mode/ACL/RO・interruption/unknownを既存suiteと共用して回帰。
- Signatureは固定pin/Ed25519/元bytesだけ。pin候補由来、署名をhashやbooleanへ置換、current先変更による検証を禁止。

## 初期専用VM構築（PT-OPS-NATIVE-028以降、まだ未実行）

marker・全actor停止/真正全cgroup終端・M/A・未permit/INVALID・業務行0/seedのみ・snapshotを事前確認。001..022 source byte/historyを保全し、専用schubert_migration/Flyway13.4でV023だけ追加。repair/clean/baseline/履歴手修正/superuser fallback禁止。固定query six-column期待はrelease SQL＋一次Flyway toolで生成、実DBをexpectedへ採用しない。projection/grantはDDLと独立SQL後条件で確認。

候補外tool/pinのtrust根拠・鍵custody/版・RO host mount・approval publication/force-close-atomic-sync/current切替と途中失敗を実観測し、既存Native027 run/activation/cutoff/3原本hash保持・同identity resumeを確認。真正RootReleaseAdmission固定public factoryとread-only schema検査はnative部分受入のみ。backup begins/DB success/permit発行/全親/R2R3をまだ合格へ算入しない。

## 実行/結果

command/env/branch/source/終了code/selected suites/4 coverage/static・BUG/SSC・evidence hashは後続結果manifestへ記録。未実行・skipped/failedを合格にしない。test-only assembler/probeはProduction source/coverageを代替せず、秘密鍵/password/DBdump/raw sessionはprivate Git外。全新Production branchのcoverage100%は実行後に確認し不足を除外しない。
