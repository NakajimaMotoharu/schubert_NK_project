# 取得前準備是正・公開codec五試験 仕様

1487～1489、PG-D504/505、BUG1618/YKT1371。元4197/6784・原0e7d0f35・元28/6782は旧3c5の証跡として保存し再演しない。次候補の唯一のMain変更はWebManagementServer初期empty localをbind前へ移す一行移動、全旧Main/旧Test/gatesは固定。三codecのPG reviewはSS343/SSC111124137へ照合して正しく変更不要、実回収/原本/許可の正当性をこのdataから認定しない。

## 着手前予算・実行範囲

群1706の主担当は実leaf P017-07.02、component P018-03.02/P017-06、親P017-07/P018-03参照費0、低.2/標準.8/高2pp固定。Web1618是正は既群1700の追加発見/手戻りとして別記、原/v4や開始予算を書換えない。正式/工数率/個別受入を見積減額で作らない。

`pg6796_web_early_cleanup_proof.py`は公開source/JDKの構造確認のみ、heap枯渇を発生させず初期emptyがbind前であることを必須とし、元late配置とstarted成功化変異を拒否する。さらに旧d549の全state/lock/期限/割込/診断追加の例外領域へ厳密に逆展開。実Allocation failureのPT成功や拒否PT代替へ算入しない。

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<既pyflakes runtime> python3 -B tools/quality/pg6798_web_correlation_selected.py run`はPT_DEFAULT。既Web10/Unstarted1/Stop5＋batch旧Launch4/Expiry7/Fail4・新三Test五method＋六guard12=48件/16suiteを発行前の実declarationで固定。全six format-beforePT/compile-null/Werror/SpotBugsを維持する。自己所有Web factory/HTTP/executor/有限childと、メモリ中のpublic record/bytesだけ。実VM/DB/失敗cohort/原本Backup/鍵/permit/startup能力/native資格の操作0。fixture/expectedの生成にProduction methodを呼ばず、既手書きGOLD/新手書きfail literalを使用する。

## 五Testの独立oracle

|Test ID / class.method|入力/操作|期待値・根拠|
|---|---|---|
|PT-CORR-LAUNCH-001 / StartupLaunchBoundaryTest.launchBoundary001*|byte127及び既goldの最終LF後X（行数は同じ）をconsume|SS343/SSC137 ASCII/LF/末尾LF、固定IOException startup launch unavailable・cause null/suppressed0。旧255はsigned -1、LF削除は行数違いなので非重複|
|PT-CORR-EREQ-001 / ExpiryRequestBoundaryTest.expiryBoundary001*|run/activation/bootを個別NIL、brokerを32個のX。他の公開UUID/step42/attempt1/cutoff/startは有効で固定|SSC111 nonzero identity/nonzero32lowerhex、固定IllegalArgumentException cleanup request invalid/cause null/suppressed0。元recordからexpectedを生成0、constructor以外を呼ばない|
|PT-CORR-EREQ-002 / ExpiryRequestBoundaryTest.expiryBoundary002*|byte127及び通常/skip goldの最終LF後X|SS343のprintable ASCII/LF/canonical末尾、同fixed IllegalArgumentException/cause null、owned全byte0。旧profile/時刻/相関は既七Testを維持|
|PT-CORR-CFREQ-001 / FailedProfileBoundaryTest.failedBoundary001*|byte127及び独立手書きfail gold+X|SSC124、fixed IllegalArgumentException failed cleanup profile invalid/cause null、owned全byte0。DB/実failureとの比較なし|
|PT-CORR-CFREQ-002 / FailedProfileBoundaryTest.failedBoundary002*|別runの内部有効BackupFailureSnapshotを公開constructorで作り、outer runだけ異なるCleanupFailedBackupRequestへ渡す|SSC124同run必須、同fixed IllegalArgumentException/cause null/suppressed0。入力pair生成はassertThrowsの外で行い、前提失敗を当拒否と混同しない。verifyLatest/receiptMatchesは未呼出|

Web1618是正の通常/例外/並行/資源後条件は1487全既oracleを一byteも変更せず実行。NPEは正常化しない。初期emptyはnonnull immutable値で、helperの返値・未確認の公開throw・primary identity/診断表は不変更。新Java五Testは未実行、未実装fixture初回赤と既実装仕様違反のBUGを区別する。

## 環境・資格と結果保存

source/branch/commit/OS/JDK/command/開始終了/phase exit/input archive・期待/実値/XML/coverage/BUGは元begin/manifest、真正0後`pg6798_web_correlation_selected.py read`原6800へ一意追跡。固定all851/1669と唯一Web outer差を照合し、actual target四つ（Web/Launch/Expiry/Failed）のraw四counterは原XMLから抽出する。宣言/欠落を100へ補完0。FESflakySkippedNotRunは加点しない。必要新source全体4202-649は現段階予定で、旧4197+5算術を合格根拠にしない。

初回工具pyflakesはunused hashlib一件で1、Production PT/原proof発行0。修正前BUG1619/YKT1372起票後に新wrapperの不要importだけ削除（旧proofのhashlibは必要）、新三工具static0/管理二成功・format0。修正/実proofと当source原資格まで工具scope未完了。権限/経路/拒否条件を変えた再試行ではない。

次保存pushclean→6796構造証明保存pushclean→6798新only48-16/1669一回→真正0後read原6800→新candidate全4202/649・原/SQL/static/JVM/traceまでまとめる。既known source3c5へのWBS stage往復は未発行、旧current943 d549/95技術閉鎖・20gap・CHR1を歴史保全。正式1964/53・個別17/190・工数null・全実環境HOLD/PTALT代替0/QA051final/原-v4維持、通常小群停止0。
