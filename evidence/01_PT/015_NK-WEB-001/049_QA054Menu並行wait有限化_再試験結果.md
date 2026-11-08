# QA054 Menu並行wait有限化・変更後元十五再試験結果

2026-11-08、dev-foundation。BUG2521/YKT2177、主G03.05/関連canonicalOwner P00603・P01602追加費0、REWORK開始1/3/7pp cap9不変。MenuAuditContractTest.menu005の無期限Future.get一siteを10SECONDSへ、所有executorのTWR closeを明示shutdownNow/awaitTermination10SECONDS+assertへ変更した。outer traceのfinally closeと、import/当block以外の全byte・全独立期待を前後逆変換で保持した。元snapshot24208/着手3861・015048参照。

format24212/compile24214は真正0、Java25/-proc:none/-implicit:none/-Xlint/-Werror。static24216のraw PMD11（J2EE thread規則9、定義元Model loader1、明示shutdownのCloseResource1）をsource/method/span別に個別分類し適用違反0、Checkstyle0/processing0/suppression0。既Main22084/六静的22086をbyte/source結合して再利用、Mainの不要なbuild再演0。preflight24218は元正実行Main20 CRCが現正常artifactと全一致、SDK12のdriver/compiler-plugin/manifestClass-Path無し、全元15/全target四physicalを確認0。

修正source f72114ac1c9e95a5ecc4d7286def4a3b554fcdeeをcommit/push後に、current Production Main7aed8eace7c844c2f79f2e39db766faf914890d5のWeb/Protocol normalを用い、MenuAuditContractTest全五+WebRequestTraceTest全十をpg24220-menu-audit-bounded-fifteen-unit-v1で一回実行。真正OS終了0/全15 found-started-success/F/E/skipped/aborted/container-failure0、append=false/単session PG24220-MENU-AUDIT-BOUNDED-FIFTEEN。report/classinfo/execinfoも0。これはTest変更後の必要回帰で、原19558の成功を確認する再演ではない。

独立24222はsource/Git input全pin・全十五case集合/原XMLhash/OS-JDK環境・全target normal byte/CRC/SourceFile全四physical・同exec/session・全method/branch counter・初期化logを確認0。line103/method30/class4/branch38はcovered全数・missed0。実hit Main20のCRC全一致、held四のpositive probe0/初期化0。Kindのrawprobe21/22等と公式compiler filter後のcounterを区別し、raw全probe100とはしない。manual除外/旧exec union0。他calleeのpartialを全体100へ合算0。

canonical `evidence/01_PT/015_NK-WEB-001/evidence/PG24222-menu-audit-bounded-fifteen-independent-v1/manifest.json` SHA256 361b1aa10765513568436d02faab6ecc3c36ffdbd0ae24a8efa69f751d0bdbc3。command・開始終了・OS/JDK/tool・unit/static/compile/hash・原XMLpin/safeXML/coverage/exec/actual/期待根拠は同manifest/各file/050～053へ一意対応。公開JUnitは必要case/timingだけ、class-init logは私有ownrunに保持しhashと初期化判定を公開。合成0-format Principalは表示fixtureのみで認証・session発行に使わず、実DB/JMS/HTTP/VM/Root/cohort/native/キー・原本操作0。SDK全syscall0は主張しない。

当BUGはPG修正と元全十五再資格が揃った限定閉鎖対象。YKT2177全体はOPENで、Question/UserCommandServiceの動的HOLD・全Testの型未確定等は残る。旧23952のMenu一entry（Adminと計二source）は歴史化、全解析再演0。新規unique試験0/製造Main0/新source成分0/新leaf0/正式更新0。unique517/候補114/pending12/旧whole93暫定/正式1964-53/工数null/QA051final/G07未分類3313+22actualSecretCountnullと全実操作HOLD不変。続いて原計画の未完criteriaへ進む。
