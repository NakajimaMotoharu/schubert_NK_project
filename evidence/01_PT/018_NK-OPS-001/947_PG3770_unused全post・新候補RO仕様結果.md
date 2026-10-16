# 947 新候補unused/RO・独立全post

対象Main7fffab57a567914956b66452e5e54388642efdec、PG3748/BOM652915c694fe6120af81587195150d7df8bcc411b7eb4f5d74cf3f71fd87517b。現行4856/PG3420、SS343/354/355/451、BUG1322～1324/YKT1088～1090。工具試験をProduction PT件数へ加算しない。

| Test ID | 独立期待値・手順 | 元結果・証跡（WorkPG379） |
|---|---|---|
| PT-HYGIENE-UNUSED-3770 | 全187署名済み候補をunusedのみ配置。現行link/24表/原本Backup/native34/全32/全資源は保存済み独立beforeのまま | pg3770-stage-v1.safe.json、pg3770-place-v1.safe.jsonはactual0。place00:17:50～00:18:37Z、全新scope正常返却 |
| PT-HYGIENE-POST-3778 | 元sealed11 SHA35f5e077/canonical10 SHA c85b34d3、全24二読・実DB事後条件・全current/candidate187署名・32設定厳密一致。fresh十Refを正常返却してから成功出力 | pg3778-hygiene-unused-held-post-v1/manifest.safe.json actual0、00:23:15～21Z、payloadSHA f7bc99b9ae211edb6f8f88f38351bcf3796086891f8b062477365bc1fa9c4516 |
| PT-HYGIENE-RO-ABI-3782 | 全18実source/共有class hash保持、latest3600完成tupleをdataとして分離、全Java lint/Werrorと五mainの固定golden/未知/null/余剰/label/ownership前境界 | pg3782-frozen-v1.safe.json actual0、operator0cb6c1b73、全五main0。現行jarで工具ABI検査のみ、VM変更0 |
| PT-HYGIENE-RO-3784 | 一回予約stage→prepare-ro。fresh M/A/DB/十Ref下で候補だけPID1 namespace RO、現current/epoch/start/SQL変更0、全scope正常返却 | pg3784-stage-v1.safe.json actual0、prepare-ro-v1.safe.json actual0、00:30:39～00:31:25Z、operator e9f52ec8d |
| PT-HYGIENE-RO-POST-3786 | 未使用postの全独立条件を保持、Ref返却後PID1 namespace/findmnt exact ro/rw不存在と真正complete.privateの全byteを別に検証 | pg3786-hygiene-ro-independent-post-v1/manifest.safe.json actual0、00:32:02～08Z、payloadSHA5a4e269fc154ee40693fb1ac8e2ea01e7256dc0f7b8d4d5014b37c889e7300ed |

再現commandはPYTHONPATH=tools/quality:tools/quality/vm/050_s1:toolchain/pyflakes-3.4.0/runtime下の各同番号Python。既実行3770/3784のstage/place/prepare-roは再発行禁止、元予約・元終了codeを参照。JDK25.0.4、Linux、guest boot79a3260a-e16d-42bf-942a-b914ed144c28、現起動を操作時再認証する。新source全体3714/545/1643は3734/3738/944に分離。旧3760place1・3772post1・3774NoSuchUnit失敗を保持し、新結果へ書換えない。

純source1/dispatch1/post1成功。新source native/ordinary/Browser/CHR/四100/F03/451/正式受入は未完、正式1964/53・17/190・工数null・QA051final保留。Raw原本/DB/秘密・native実体はguest root/privateのみ。
