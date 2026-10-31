# InspectionAttempt原八 通常単体テスト仕様

2026-10-31/PG-D1012、主/計測leaf WBS-P004-04（481 cost.countsInTotal=true、元0.5/1.5/3.5予測不変更）、関連NK-BAT-001/OPS009/DAT009/UI251/SS311・331・341§7.3/SSC049/PG162/PT-BAT-122～129。HEAD3ea2d03e7133d752b925e458195e3c12cf80a22a/push9842終端7eafa3真正0。Production6b53/normal14216固定・未配備、現2164registryに当Main/原Test未登録。群開始0.75/3/6共有pp cap10は必要現source資格/工具証跡を含む群見積で元leaf costを上書き/親子併算しない。freshused57/rem43/reset1793774153/短期null/券0、専有N/Tnull。

## 選定と非対象

477の先行indexを実施し2078/79・289を参照、原Test213行/Main全体・依存BatchRun/CleanupCounts/InspectionSummary/MaintenanceCompletion全体を確認。PT_DEFAULT、固定架空UUID/UTC・非負件数/Optional/enumのみ、独立した原Test全八を変更せず使う。自己所有virtual-thread executor/64task、各Future.get10秒・外側JVM180秒。DB観測値という型名は実DB接続ではなく、純粋な照合結果をfresh child終端/親完了/業務処理成功の証明へ昇格しない。

直前候補のQuestionCommandMetadata null/redactionは2901/02で原QuestionCommandService wholeの実DB/Graph依存・部分抽出/新fixture迂回禁止が明記されていたため新fixtureを作成/実行0。WebRuntimeHealth.readyも2965のRemainder whole HOLD内で抽出しない。ExistingFileAccess原Testには実LinuxDirectoryCallsがあり非着手、Enum catalogは候補索引/本文読取のみで未実行。これらを新受入や失敗PTへ計上しない。

## 原Test IDと独立期待

|原method|入力/独立期待|
|---|---|
|matchingSuccessAndWarning|7/7/0→SUCCESS/0、7/3/4→WARNING/10、afterと同件数のattempt|
|zeroAndResumedAttemptCounts|0/0/0、before5/2/3→after9/5/4差4/3/1、同件数再開の差0/0/0|
|completedBaselineImmutability|complete基点は同値afterだけ、complete後の回帰/件数変更を拒否|
|countRegressionAndOverflow|target/deleted/skippedの各単調性、attempt<=cumulative、Long.MAX_VALUE境界で差1/0/1、非負差はoverflow無し|
|runIdentityAndMissingEnd|UUID/cutoff違い・end=false拒否、別object同値runは許可|
|receiptCodesAndNulls|許可receiptは結果に対応した0/10だけ、-1/1/20/30/50/70/整数端点とnull全境界を拒否|
|redactionAndValueOwnership|record同値/hashと不変値/件数差、固定InspectionAttempt[observation=<redacted>]、outcome不整合拒否|
|independentConcurrentObservations|64個の架空runごとafter(i+9,i+5,4)、before(5,2,3)→差(i+4,i+3,1)/WARNING、run間交差無し|

期待は原literal/long算術/enum固定0・10・明示String、Productionからexpectedを作らない。assert actual同士の比較は先行独立literal検査と組にし、単独oracleとしない。正常・境界・異常・null・例外・再開/再送相当・並行を元全八で維持。

## 実行と品質

16296 checked entry→既SharedSelectedJunitReporterV1と明示一class/八catalogの新launcher・単一JVM/exec、javac release25 proc:none-Xlint-Werror、既六normalJar/SDK・全input/原Test/依存byte前後照合。Main87e838668d69c083eaf0b9e9420a59f47ec344629a492c8002edd7adbfc8a8a7、Testf80fec36648c7a4934626d1f7820dedfa731d2fc79962108265ea41cb7d16780。実DB/JMS/FS/ネットワーク/OS/Root/VM/permit/鍵/Graph0、元wholeからの抽出0。

16298で全一Source一physical Code/四counter・CRC/session・四held六native無probeを受動測定し、16300で原XML/64件独立算術/承認SS/負例を別照合する。F/E/S/not-run/timeoutは合格へ算入しない。生成record filtersは公式既定のまま、到達不能化/手動除外/coverage合算0。3151にcommand・時刻/OS/JDK/branch/source/終了/coverage/BUG/hashを保存、3152/53のregistry/WBSは元全証拠/費用/正式を保持し技術だけ更新。新元計画受入0/正式1964-53/歴史17-190/工数null/QA051final/HOLD維持、通常区切り停止0・残10以下/取得不能保全。
