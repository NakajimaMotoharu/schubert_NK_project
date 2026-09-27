# PG310 root親実接続 draft（2026-09-28、code未着手）

471/472のR1 D01/04/05を阻止する同経路の内部依存。PG309 source3002ab8f9のshared security6module回帰中はcode/test/tools/settingsを固定する。終了後SSC093を先に採番してSS341/343へ具体化し実装する。旧15pp/単位完了/PMO待ち停止なし。

## 接続する最小単位

既存RootStartupContextだけ固定MORNING（schubert-nk-morning-controller.service）を追加する。API/Web後段proofのservice enum/資格情報を増やさない。root親は固定Unit/MainPID/Invocation・kernel proc/PID1/bootを独立確認、M獲得後/A獲得後/変更前/終了前にも同contextを再確認する。

`MORNING context → M → root原本start/resume → 固定停止 → A → 全対象終端再確認 → startup current INVALID → schema/DB session advisory71419602/両backup step begin commit → new request → fixed worker start → fresh0/全子終端 → root config tar/credential age → 実size/hash/真正manifest → publish/recheck → DB両SUCCESS → 成功後7世代`

M/A/原本・DBhandleはroot親のみが所有。workerは再取得しない。起動unknown/終了不明はsource request/part/M/A/borrowed FDを保全した非復帰隔離とし、通常unwindしない。全backup30分は親起点の単調deadlineを各suboperation/manifest/DB commitへ通す。suboperation別30分の加算は禁止。既存BackupBundleCompletionは自分のstartだけなのでwithin overload/同startedの共有が必要、承認済外部仕様を変更しない。

## cold/post-stop全終端

現Probeは照会errorをemptyにしないまま保持。root親の別固定effective queryでSlice=system.slice、Delegate=no、ControlGroupが非空なら/system.slice/schubert-nk-backup.service一致を要求する。Unit本人がcgroupを移動できない固定sandbox/配備と、親以外の自動start/restart/migration禁止を別に確認する。

真正PID1 host viewを既存LinuxHostDirectoryCallsで保持→/sys/fs/cgroup/system.slice各segment NOFOLLOW/typed metadata/ACL/実cgroup2とnamespace同一性→保持system.sliceから固定leafをopenするその一点のMISSINGだけ不存在。祖先missing/権限/一般IO/symlink/close失敗は拒否。Unit状態/配置・rootcontext・祖先identityを前後で再確認。leaf存在時は既存全process/stable queryへ進む。recursive walkerや直下cgroup.procsだけの空推測は追加しない。不存在はquiescenceだけでfresh success/manifest/DB成功を代用しない。

Astra/high既存補助1名read-only reviewは同別Slice残子反例・この最短分岐を確認。root親のnew-onlyrequest prepare/retireはこの全終端の内側だけ。native025 test helperのkernel不存在確認をProduction親済みに読み替えない。新故障は915/必要916へ修正前起票。

## PT/実測

rootcontext固定MORNING、fixed effective argv/projection/冷Unit・別Slice/Delegate/ControlGroup/nonempty/timeout/unknown/前後変化、NOFOLLOW祖先/leafのMISSINGだけ/全typed属性/FS/ACL/全close/primary compound/null/interrupt/parallel。request準備・start・receipt0・stop・全終端・retireを一つの借用M/A callback内で独立latch確認し、unknown中のreturn/close/次job0をassertする。counter収集前にTest owner/JUnit/prefix/canaryを確認する。

実固定root親Unit/M+Aを隔離VMでProduction workerへ接続し、request作成/既存dated part保全・fresh worker code0・全終端・親後処理を実測。DB/manifest/fullarchive等未接続をwholebackup成功へ代用しない。そのまま既存3archive/bundle/step/retention/rootmorning/currentpermit/業務main/CHRへ進む。fullrelease BOM/親DB/cleanup/transfer/Broker/Expiry・currentpermitはまだ未実装である。
