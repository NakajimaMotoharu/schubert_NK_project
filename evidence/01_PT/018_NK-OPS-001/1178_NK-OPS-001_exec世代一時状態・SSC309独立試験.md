# PG5706/5708 exec世代一時状態・SSC309独立試験

2026-10-20、NK-OPS-001、RootStartupContext/MorningServiceReadiness、SS342/343/354・SSC164/309・BUG1470/YKT1233、WBS-P018-04.03。元Root43efe768は真正30の失敗として不変、正常後続/再起動を発行しない。

PG5704元98612は旧296の署名BOM85fb/六JarSHAと旧native14dcd6c8を旧source自身で解析し、現失敗native1c28beebと同byte classだけを診断比較。全六Jar/役割検証0、manifest8c1cf119f850a9fe2431a74734d2bf3c50b2b31bafa5df83217ee9e8dc63aeb6。同byte RootStartupContext392行state predicateと426行requireで現失敗だけ拒否側を通過。元raw stateは未採取なのでZと断定せず、旧成功の新source転用/coverage union0。

PG5706元57514は同bootで非leader execの独立Linux fixtureを一回実施し終了0。一試行でstat Z・pidfd非終端→同PID/startTicksでexec後R・自然終了0を確認。signal、業務Unit/Root/DB操作0。公開manifestは evidence/provisional/PG5706-exec-generation-kernel/manifest.json。初回未完成fixtureのunused importはtransport/static preflightで拒否されnamespace/SSH未作成、現process/出力不存在とemitted static一件を確認して除去後の初回guest発行。未完成TDD補助の準備拒否でありRootの新失敗としない。

独立期待値は手書きproc statのfield3/22・Unit/identity/HTTP golden。PT-OPS-EXECGEN309001はAPI/Webの一時Zを同世代pending、終了false、R復帰後も同世代、二回NoSuchだけtrue。002はRoot/self/PID1でZ拒否、X/x/未知、異ticks/cgroup/Unit漂移を拒否。003はguard通過だけでは空cmdlineをreadyへ昇格せずsocket/HTTP前false、復帰後は普通identity/同socket/HTTP200 UP/infoが必要で503拒否。既存のnull/IO/境界/世代・期限試験も全件選択。

実行commandは所定PYTHONPATH付き `python3 -B tools/quality/pg5708_exec_generation_selected.py red|green --version v1`。各入力はclean commitをarchiveし、実XMLの全選択TestID/失敗・error・skip/rerunと六moduleformat/static、全1664実class差分を照合する。redは001/003の二件だけの期待するassert失敗、greenは全選択成功とRootStartupContext内の差分だけを要求。限定coverageと全体/正式/正常nativeを分離し、全四100の宣言はしない。

状態：独立kernel反例は終了0。選択red/green・新全体/同source native・failed-cohort回収/全資源postは未実施、後記する。原/v3/v4未較正597.25ppは不変更、群1321の開始見積.5/2/6共有ppを固定し、Root失敗は新規発見/手戻りで前計画完了へ加算0。formal1964/53、工数率null、QA051finalHELDを維持。
