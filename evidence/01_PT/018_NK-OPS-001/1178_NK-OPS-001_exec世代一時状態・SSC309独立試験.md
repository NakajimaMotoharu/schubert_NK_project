# PG5706/5708 exec世代一時状態・SSC309独立試験

2026-10-20、NK-OPS-001、RootStartupContext/MorningServiceReadiness、SS342/343/354・SSC164/309・BUG1470/YKT1233、WBS-P018-04.03。元Root43efe768は真正30の失敗として不変、正常後続/再起動を発行しない。

PG5704元98612は旧296の署名BOM85fb/六JarSHAと旧native14dcd6c8を旧source自身で解析し、現失敗native1c28beebと同byte classだけを診断比較。全六Jar/役割検証0、manifest8c1cf119f850a9fe2431a74734d2bf3c50b2b31bafa5df83217ee9e8dc63aeb6。同byte RootStartupContext392行state predicateと426行requireで現失敗だけ拒否側を通過。元raw stateは未採取なのでZと断定せず、旧成功の新source転用/coverage union0。

PG5706元57514は同bootで非leader execの独立Linux fixtureを一回実施し終了0。一試行でstat Z・pidfd非終端→同PID/startTicksでexec後R・自然終了0を確認。signal、業務Unit/Root/DB操作0。公開manifestは evidence/provisional/PG5706-exec-generation-kernel/manifest.json。初回未完成fixtureのunused importはtransport/static preflightで拒否されnamespace/SSH未作成、現process/出力不存在とemitted static一件を確認して除去後の初回guest発行。未完成TDD補助の準備拒否でありRootの新失敗としない。

独立期待値は手書きproc statのfield3/22・Unit/identity/HTTP golden。PT-OPS-EXECGEN309001はAPI/Webの一時Zを同世代pending、終了false、R復帰後も同世代、二回NoSuchだけtrue。002はRoot/self/PID1でZ拒否、X/x/未知、異ticks/cgroup/Unit漂移を拒否。003はguard通過だけでは空cmdlineをreadyへ昇格せずsocket/HTTP前false、復帰後は普通identity/同socket/HTTP200 UP/infoが必要で503拒否。既存のnull/IO/境界/世代・期限試験も全件選択。

実行commandは所定PYTHONPATH付き `python3 -B tools/quality/pg5708_exec_generation_selected.py red|green --version v1`。各入力はclean commitをarchiveし、実XMLの全選択TestID/失敗・error・skip/rerunと六moduleformat/static、全1664実class差分を照合する。redは001/003の二件だけの期待するassert失敗、greenは全選択成功とRootStartupContext内の差分だけを要求。限定coverageと全体/正式/正常nativeを分離し、全四100の宣言はしない。

状態：独立kernel反例は終了0。選択red/green・新全体/同source native・failed-cohort回収/全資源postは未実施、後記する。原/v3/v4未較正597.25ppは不変更、群1321の開始見積.5/2/6共有ppを固定し、Root失敗は新規発見/手戻りで前計画完了へ加算0。formal1964/53、工数率null、QA051finalHELDを維持。

## 2026-10-20 00:25 限定是正結果（上の未実施は起票時履歴）

Source **6db56feeea6df0e355c018e6b80ad4e40c2d90f5**。red-v1元11701はAPI選択NoTestsでactual1/18依存のみ・目的not-run、BUG1473/YKT1236修正6a57516acでno-tests厳格性を維持。新red-v2元99605は実62/8/F2/E-S0・309001/003のassert二件だけ・元全1664同byte、purposefulRedEstablished=true。新green-v1元89205は **actual0/62PT/8suite/F-E-S0/六format-static0**、sourceFixed/exactInventory/declaredPhysicalDelta真。green manifest f14cfae4b742be45d2c89a84efef0eea1653756c058db8c2c54678be7b6c088f。選択期間にMain/Test/設定及び元HEADを変更せず、独立read工具の準備は別private領域に保持し完了後に戻した（試験対象への混入0）。

独立5714 actual0/68c6322c579858cba956e2e6a3dc3eb98875b526e1bdd760277038417f043bea、全62元XML hash/TestID、実1664、RootStartupContextコード一/NativeIo debug-only一/他1662同byteを確認。公開e74f0f35eb977656fcc4bd8103b4cb4426639a10f7d697a87526a27254334212。対象Root line199/199・method25/25だがbranch133covered/21miss、Morning readiness line84/94・method7/8・branch75/81で**選択全四100ではない**。新条件とstrict/false-ready反例は通過したが必要fresh全体3908/563/1664・同source実native・四100・正式は別未実施。

設計四文書だけは63e8cfde4→main f6d9fe71b1bc62c23922e98f2248e9e0624ef0fe/PR164で通常merge/remote確認、コード/証跡/工具混入0。PR添付100上限エラーを保持し迂回しない。

5712元43092 actual0/76c79b98c47309fd12807ead3981e3153d7fa9537a1a2837edf61d202be29d8a、15:21:34UTCのfresh read。実配備は**旧0ea/PG5598/BOM1aa187**、全十設定/Unitfile・全24二読/原本Backup/鍵/97native安定・十Ref正常返却、DBpeer/advisory/flock0、Root真正30/.done無し。生存actorは同Artemis967597/t41807207/INV696929のみ、全NSS/caps/NNP/166FDを二読。startupは62entry/permit-start.intent有/service intent一、旧normal33/37等へ正規化しない。読取は回収権限でも正常owned停止でもなく、回収/別postまで未受入。原old94も保持対象として新97内の正確な差分とhost保存を次工程で照合する。
