# NK-MED-001 Media五型の同一実行と未到達箇所

WBS-P009-04/2、SS333／351／354、SSC-476。他runのexec結合を行わず、現sourceの純parser、メモリ配信、閉じた値、元承認のPT-MED-006自己所有TempDirの11 Test classを、同じJUnitとJaCoCoで実行した。実Linux／Nativeを使うMediaRangeServiceTestは選択せず、実HTTP／実ファイル系の受入は保持する。

PG41256は計27成功（製品26、fixture1）、失敗／エラー／skip／未実行各0、終了0。JDK25.0.4／JUnit1.13.4／JaCoCo0.8.15。実行は入力5642。独立読取は入力5643。起動前のguardは純粋なURLEncoder参照を通信扱いして停止した。固定importの扱いを修正した後、一回だけJUnit起動。用意した自己所有TempDirは終了時空。

PG41258の当13物理。line 139/139、method 38/39、class 9/9、branch 73/74、instruction 725/736。未到達はMediaRangeService.respondの105行にJDK25が挿入するtableswitchのMatchException辺と、MediaDeliveryException.Reason.valueOf。coverageは未達。手動除外・合算・分母操作なし。

- [同一実行](../018_NK-OPS-001/evidence/PG41256-media-current-five-types-single-exec-v1/manifest.json) SHA-256 c23190b1eb8a0ebfa6a4e8efefbc0a758b11da2411144cb60b428933c8780755
- [独立測定](../018_NK-OPS-001/evidence/PG41258-media-current-five-types-single-independent-v1/manifest.json) SHA-256 74428097ca05f898775078a4005c02233dc123140b7b57fd88eed896a5a2eebe
