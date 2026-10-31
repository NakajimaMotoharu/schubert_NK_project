# MorningBackup合成metadata・catalog原八 単体テスト仕様

2026-10-31 / PG-D999 / 主WBS-P017-03.01（canonical source/cost P01703、親へ重複配賦0）/ 開始1/4/8共有pp cap10、fresh16:56used55/rem45/reset1793774153/短期null・N/T専有費不明。保存a8d2b9183/remote同値、3114の477定期点検を実施済み。

先行MorningBackupMetadata index2/1077・全三Test/全MorningBackupArtifacts628行・EnvironmentInodePolicy.require/Metadataの呼出閉包を確認。PT_DEFAULT：MorningBackupMetadataTest whole4/PT-BAK-2122-001..004＋MorningBackupCatalogTest whole1/BCATALOG001＋MorningBackupInputModeTest whole3/PT-OPS-BMODE197001..003を原文のまま初回実行。動的DB/worker/原本/権限操作を含む他MorningBackupTestは選択せず、保留Test抽出・新fixtureは作らない。

Mainのstatic initializerは公開name list/mapだけ、instance constructor/complete/check/backup・read/write/shaを呼ばず、Linux/Root/鍵/認証/Backup/DB/JMS/VM/FS/保持・配備/permit操作0。credential名は公開catalogの文字列であってcredential値や実fileに触れない。inputModeは設定0640・api/web.envとcatalog credential0600、Inspector static0640・未知/cross catalog/null拒否を独立literalで確認し実permission変更なし。metadataは独立八進mode/uid/gid/link/sizeの正常・境界・異常/null、ACL present empty/非空不変を確認する。

全MorningBackupArtifacts一SourceとWork/Writer二NoCode interfaceの三physicalを分母に含める。Mainの大半の実Backup経路は未実行としてmissを保持し、metadata成功を実artifact/role/DB/原本Backup成功や全四100にしない。EnvironmentInodePolicy/Metadataは既proof維持・同execの補助class実行を新whole資格へ追加しない。

予定16176原8/3一JVM→16178全Source/XML/CRC/session/二NoCode/四held六native受動確認→16180独立POSIX/catalog/SS341343/metadata反例→registry/WBS。F/E/S/aborted0のみ成功、normal14216・全src/元assertions不変更/旧成功合算0。toolchain/command/source/hash/元環境/時刻/結果は各manifest、正式1964/53・工数null・QA051final/全HOLD不変更。
