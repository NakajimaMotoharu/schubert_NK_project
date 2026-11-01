# Root ELF原8・実行結果と独立照合

3372/PG-D1083、2026-11-01/dev-foundation、qualification HEAD1faa9a78585efd181feb9822829d66ee5852c29d、Production source6b53efeec87f3ec36a840dd8e7759656cb4aee5c（未配備）。原whole8/1suite全PASS、F/E/S/aborted0。原Test/Main/仕様は不変、旧1045の成功転用0。新規専用runのcommand/開始終了/OS/JDK/exit/XML/exec/input pinは下記manifestへ固定。

|段階・公開manifest（evidence/provisional/配下）|SHA256|真正終端|
|---|---|---|
|PG17309-root-elf-digest-review-v1/manifest.json|b6b45247e72774f119e73bc5d3d0f6b1afbdaef94f3ae7c21f8ce9794ed7b81a|事前source/Test全読取|
|PG17310-root-elf-digest-eight-pt-v1/manifest.json|8e1b843cc463d2c8a28e25717d760cf207a1453f5c8ef1d68a6ddaa9174e5858|session33231/終端bafbdc genuine0|
|PG17312-root-elf-digest-eight-post-v1/manifest.json|4590d3fae00a2b778203b1e2893d394e3f1d3da4bc42c498334bb93696867307|session3532/ebcbba genuine0|
|PG17314-root-elf-digest-eight-independent-v1/manifest.json|41cf065f95e0de4271293294d97828ab6232ef6f10db131824a53c7b57f1151a|97a141 genuine0|

全Source五physical＝Code二（outer/RootDescriptor）＋NoCode三SAM。RootDescriptorは未実行のまま保持、Main total L28covered/175miss M3/50 C1/1 B22/70、strictFour100GateExit1。未達175L50M1C70Bを除外/旧source/別execへ合算しない。四held/六native trueprobe0、RootFailed五/Cycle23/既inactive全record不在。借用memory Inputだけをdigestが読む。JCA SHA256利用true、鍵/資格/実file/DB/VM/Root/Unit/サービス/権限操作false。same session/CRC不一致0、TestとInput二Code CRCも独立照合。

独立27非同値metadata反例、原8の明示assertion対応とPython hashlib固定vector二つ（64/8388608byte）一致。001～008 ID/method/input/期待値は1045表の順をそのまま対応、本文3372参照。NoSuch→固定IOException/no cause、未知失敗identity/null fail-fast、8193report拒否、借用close0/wipeを確認した。実OS admission/readAttributes/withSetpriv/admit/RootDescriptor.closeは未実測。Source全分岐/正式F03/451/CHR/nativeの受入ではない。

BUG2201/YKT1948：旧17320の公開要約6/2/2/0が残り17322がWBS書換前に拒否（825b0c/body1/OUTなし）。元raw8は再演0。新17321v2の全34metadata/二chain/二profileに四公開要約反例を加え、actual XML/fresh physical/metadata集合から8/1/5/3を導出して一致確認。全四family（元17298/17300正例、今17318正body、旧17320誤出力、新17321v2是正）を比較した。旧工具/entry/誤結果/費用を保持、有限再試験PASS_SAVE_PENDING、commit/push実確認前にCLOSEDとしない。別BUG2195/YKT1942 OPEN不変。
