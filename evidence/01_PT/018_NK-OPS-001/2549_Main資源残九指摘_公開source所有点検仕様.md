# 2549 Main資源残九指摘 公開source所有点検仕様

2026-10-29/PG-D840予定/event2934/F03主、canonical P00403/P01712/P01706/P01804は原artifactの非加算費用参照のみ（P01804はsplit parentで費用leafにしない）。開始1/4/8cap10、source0061/normal13832/静的13838/trace13968を固定。

製品・新fixtureを実行せず、公開sourceと承認SS341/343・原static metadataだけを点検する。失敗cohortの実状態・回収追加調査/実装/実行、intent/permitの読取/取消/退役、Root/VM/Unit/DB/鍵/native/stop/startは全て保留のまま。ここでのsource変数名・記述を実操作の承認とみなさない。

対象はMaintenanceRunFiles.verifyStartupPrivate/current・parent/read.root（02845/846/856）、RootFailedStartRecovery.retirePair/marker（02918）、BackupUnitStartClient.beginNative/marker・awaitClient/stdout/stderr（03027/044/045）、MaintenanceUnitStopClient.awaitClient/stdout/stderr（03102/103）。具体取得元・借用・移管・返却と失敗出口を読取、原id/path/method/offset/現byte/485 ownerを13976に記録する。

Session/recursive listのrootは外Scopeから借用し、local closeは二重所有になる。pair markerは同一caller-rootを借りるmetadata wrapperでconstructorは新FDを取得せず、closeは共有rootを閉じるためlocal TWRにしない。native beginのowned markerはtokenと返却lease closureに移管、失敗はclose試行→throwで成功へ変換しない。両awaitの二streamはgetter失敗でも先行close、closeBothは先行失敗でも後続closeを試み、失敗はUNKNOWNのまま。試行flag/known client exitを成功close・Unit終端・unlock証明へ変換しない。

13978は原XMLから別span・十四typed反例/十二source文字列反例で所有/分岐順を検査するだけ。raw九件は保持・CURRENT_WHOLE_JOIN_PENDING、実PT/coverage/nativeは0/null、警告削除/抑制・拒否再演・代替実行0。真の設計/PG不備が確定したら先に台帳、未証明のnative例外順位や不確定closeを成功と断定しない。次traceは原WBS/全995歴史runtime不変で参照九件だけ追加、2550へcommand/環境/時刻/hash/個別根拠/残リスクを保存する。

正式1964/53・17/190・工数null/QA051final、原本/stash/二held工具/全HOLDを保持し通常区切りでは停止しない。
