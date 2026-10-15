# PG3204 Expiry三Test・全3694と同native27の統合結果

NK-BAT-001/689/OPS009～017/DAT009/UI251252/SS331341343/451。新Test三method/三Test file（共通helper含む）、Production a9cb0ac9は不変更。根拠はPG3200全十/3202全七actual0と、固定Test byteからの一回全統合であり限定成功の単純加算ではない。

## 実行と独立資格

対象snapshot `f00d9012390224d86835555f26bad6caf5ff266f`、source archive `952b92821049b0f831b3c6022b5af0b8d91039de11abe823509989df3ecf0d09`。aruの隔離source-full-PG3204/PG3204-six-v1、JDK25.0.4/Maven既固定版/PG18/GoogleJavaFormat1.36.1/JaCoCo0.8.15/ASM9.10.1。branch dev-foundation、source変更0、Main再配備/Root/VM操作0。

既PYTHONPATHからpg3204_expiry_group_full_six.py（exec57168）を一回実行。六format事前全0→全体actual0、03:39:02.519221～04:05:30.214559Z、1587.695338秒。server manifest990f598e64834f477ecd99ba4c082d2905eb1307afb36fb6f01e98326bb61cf2。途中countや旧3691は今回全体成功へ加算していない。

pg3206_expiry_group_full_qualified.py（exec14419）別独立actual0。全3694PT/542suite/1643Main/F-E-S-flaky-notRun0/static六module指摘0を全XML/source/archive/各class/hashと照合。

| module | tests | suite | 物理Main |
|---|---:|---:|---:|
| protocol | 82 | 17 | 174 |
| storage | 163 | 23 | 74 |
| bootstrap | 298 | 40 | 105 |
| API | 969 | 159 | 407 |
| Web | 888 | 130 | 315 |
| Batch | 1294 | 173 | 568 |

資格器が古い比較基点から報告する八物理差分/NativeIo一debug差分は今回三Test変更によるMain差分ではない。後段3208で当a9 nativeの全1643/79 member原byteへ別照合するまで、changedMainMemberQualificationPendingを合格にしない。

pg3208_expiry_group_native_rejoin.py（exec82617）actual0、同a9三activation30点/Inspector三組はclosing一回ずつの27独立stream・異session27を再資格。全1643Main＋79resource/META/debug一致、class CRC不一致0、旧source輸入0、VM操作0。旧native capsuleのhost3691 provenanceを新3694へ書き換えず、原manifest/hash/exec/library/session/CRCを保持して新hostへbyte join。server manifest `97928bf9d4d1978a4c8c89651d536dccf8a3880f29c51b98e741370a9ca25690`、私有outer SHA `5ed3407a166370d24ddb822607ec42db7dfe2cb5d8ed42fdb48e474d70d50738`。全体資格outer SHA `beb24c05267b898593419eb5e90ac9b85361c7e6130d34cf607db7aa35586b5b`。

## 実測差分と未完

同Main前3691＋native27の659L133M5C483Bに対し、新3694＋同27で **652L131M5C481B**。新三Testの統合で7行/2method/2branch減、class減0。CleanupDatabaseSessionは138行/24method/1class/64branchの全四miss0となった。ExpiryAuditRepositoryは201行/14method/1classのmiss0、branchはcovered171/missed7で未完。新raw XMLを別RO読取して対象classのcounterを確認し、coverageだけのassertion/除外/Production変更はない。

障害発見0、TDD工具の初期未実装namespace拒否と実VM/Production障害を混同しない。失敗/skip/notrunの加算0、秘密scan/trace/残CHR/四100/正式451/全体受入は別未完。正式1964PT/53scope、工数率null、QA051final保留を維持し、IT/ST完了認定0。

保全物/stash七/原Scenario3/Currentbaseline/原本DB/Backup/鍵/native22/全成功失敗は維持、現在VMは3198で普通全十Unit/kernel/actor-client-advisory-flock0を確認した保存点のまま保持。次は残class/owner/異常境界の意味ある独立PT、必要な隔離fixtureの承認内整備、残CHR/451/trace/引継ぎへ継続する。旧成功全回帰/Root/ownedstop/runtime退役を繰り返さない。
