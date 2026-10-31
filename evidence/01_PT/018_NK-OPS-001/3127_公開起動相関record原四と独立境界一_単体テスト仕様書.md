# 公開起動相関record 原四＋独立境界一 単体テスト仕様書

2026-10-31、PG-D1004、主WBS-P018-03（親・品質の追加配賦0）。開始HEAD89acbb31741a033a917df6c138704351f7a95ead、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216未配備。fresh17:45共有used55/rem45/reset1793774153・短期null・券0、専有費/実N/T null。着手前見積 low1/base4/high8共有pp、群cap10、原見積/v3/v4不変更。

## 着手判定と独立性

PT_DEFAULT。2356/2357はStartupLaunchRecordTestの独立whole四を公開相関codecとSHA256、MaintenanceOwnerFrame.Parentの値だけに限定して明示許可済み。旧source4749755の20試験を再演せず、現registry16182に未参照の原四を当sourceで初めて資格確認する。MaintenanceOwnerFrameTest/InspectorLaunchConfigurationTestのHOLD維持・抽出0。Main/Test/Parent公開Sourceと先行実績を照合済み。Root/permit/intent/親生存認証/FFM/clock/Unit/VM/DB/実Backup/鍵/ネットワークを呼ばない。MessageDigest(SHA256)は公開abc固定vectorに限り実行するためcrypto=true・secret key=falseと明記する。

## Test ID・期待値

関連NK-OPS-001/OPS009/UI251/SS343§6.17・SSC137、SS341§6/SSC092・SS342、既LAUNCH001～006/PT297。原StartupLaunchRecordTest四method全体は変更しない（Main2d5590794349337b7351f97582511f4c2244b8ae3fe42a7976202eb766cf05d5、Testcfb3ced853e96604d7746b195727258106aa75ec5af6d0f010dc7539f99f648d）。手書きNKLAUNCH1の八field順序、両service、UUID/hex/数値のcanonical、null、不正byte/長さ、未知例外identity、SHA256(abc)固定値を検証する。expectedをProduction encode/hashから作らない。

追加PT-LAUNCH-FRAMING-001（PublicLaunchFramingBoundaryTest一method）はSSの印字ASCII0x20～0x7eとLF、厳密末尾LFを独立literalから検証する。(a)正常frame先頭をDEL 0x7fへ置換、(b)正常frameの末尾LF後にxを追加し、各IOExceptionが期待値。前者は非ASCII上限、後者は十行のまま最終lineが非空という既原四の不足分岐である。新quality fixture一件は普通Test分母5786から分離し、原四＋quality一=五/二suiteとして同一execで一回だけ実行する。held Testからの抽出ではない。

## 実施・後条件

PG16216: tools/quality/pg11123_checked_python_entry.py経由の固定五JUnit launcher、自己所有new-only host slot、JDK25.0.4/javac -proc:none/-Xlint:all/-Werror、既normal六Jarと固定外部依存のみ、180秒上限。全normal inputの前後byte不変、Source変更0、F/E/S/aborted/not-runを合格にしない。PG16218で単一exec/session/CRCと全StartupLaunchRecord Source物理二（DigestFactory真NoCode一）を測定し、全分母を保存する。四counter不足は隠さず未達とする。

受動監査はProduct classをloadせず、実exec内のtrue probeを固定五のcall closureへ限定する。親outerはclinit/invalid以外の記録済みinstructionを拒否する。別in-memory metadataの許可外class/親全probe偽装を各拒否し、実execは不変更。これはprobe記録の限界がある補強であり、method-entry全追跡の主張ではない。既四held/六native受動監査も維持する。新しいguard/親実認証を実行しない。

PG16220独立照合で承認設計/手書きvector・元全四/Test ID/新一/XML・全Source/NoCode分母と呼出閉包を別経路で照合し、その後だけregistry/WBS技術overlayを更新する。全451/G07/G13・正式1964/53・歴史17/190・QA051final/工数null/HOLDを維持する。実command/時刻/OS/JDK/branch/source/終了/hash/coverageはmanifestと3128へ保存、通常小群/commit/報告で全体停止しない。
