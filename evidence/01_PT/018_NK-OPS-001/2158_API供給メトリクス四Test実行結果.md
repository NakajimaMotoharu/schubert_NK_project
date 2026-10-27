# API供給メトリクス四Test実行結果

2026-10-27 09:46 JST、branch dev-foundation/source **aafcc38d2d48627e10f816dd45bfaeb20bf5e415**、Main21d不変。仕様2157/群2520開始1/4/8cap10、BUG1900/YKT1651/PG-D696。変更は39String定数291参照＋第二factory呼出2の四定数（計43、参照295）、Main/外部仕様/独立oracle不変更。

|段階|実結果・manifest SHA-256|
|---|---|
|11154 plan|全元literal入力/参照保持、525b6cea91ae9f61937075c96298dddcce2a3a0abafda3b8628f9d658087292a|
|11156 inverse|全元token逆復元・十六誤値/欠落/Test無効/境界改変反例、a7ca42f4610d8d066afaa7696098f528fa3d2d95fe1e2ce4675fb90607d4376a|
|11158 normal|六module通常package/NullAway/JSpecify/format/Werror成功、PT0、580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c|
|11160 host|元34method/四suite、F/E/S/aborted/container失敗0・JVM/producer exit0、d05927e75f8c56a1bd639ba2a2e49c511d80f46f9e773daa05ed80466670082c|
|11162 static|元55→実12（duplicate39/if4消滅）、CS/processing0、rawgate1保持、d5e5db629b48946657e44567fbfc37c2281ff19a8af5d3a879809b0bc89d7177|
|11164 post|元XML/一exec/CRC/source・全467API確認/六metadata反例、db7bc3836bfffbced40d486ba8de03f8a0483881c1c5d74eab8d62c872c29c98|
|11165/67 context|THREAD8/Map4の具体所有文脈・十反例、3b02041b948f03e6993b9bf2603bf943597c252bd8e0375ee5e5c12b3a761813 / fd3ac323594856c0d1b417d259957e845907bdfabe3c96c7c8fa890c458d009c|
|11166/68 trace|元主担当P01809四SHA更新/他979保持・六metadata反例、d6b06246b2ad94e41e2c611e9d66feb163ea0ca8dbecd6ce9f15d75de57f80dc / 1148062c569953c5f3985a8d7801488b43f940eba040dcb21646b87251764135|

公開証跡は各evidence/provisional/PG111xx-api-metric-fixture-...-v1/manifest.json。元command/終了日時/OS・JDK/tool/input/dependency/classpath/helper/exec/XML hashは11158/60/64各manifestを正とする。実行入口は `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg111xx_api_metric_fixture_....py`、lint0後だけ元entryをnoargで発行。Linux/JDK25.0.4/Maven3.9.12/JUnit5.13.4・Platform1.13.4/JaCoCo0.8.15/PMD7.28＋record1298patch/CS14.3/GJF1.36.1、全source/deps前後SHA不変。新所有空CWD/専用JVM240s、明示元34methodだけ、JUnit extension/parallel auto無効、実broker/SQL/HTTP/DB/VM/Root/鍵/Browser/native0。

MQEVENT001..008/8、MQTIME001..009/9、DBTIME001..009/9、INBOXMET001..008/8全34。正常/境界/空/未知/null/例外・partialstate/所有close・有限並行/別ownerと固定label/CDF/MAX独立oracleが成功。有限直積2688/768等は件数へ加算0。旧成功/execと合算0、変更に必要な通常再試験として区別する。

同一新session PG11160-APIREQ-JP・一execで完全API **467=447analyzed＋空package-info20**を照合。全Main1843byte/debug不変、当四SourceFile由来Test18物理差・他1944不変。八Main（MqMessage＋Stage、MqProcessing＋Outcome、DbQueryDuration＋Query＋Outcome、InboxReplay）は各四counter miss0。ExactDurationRegistryはL13covered/10miss・M3/3・B6/8、ExactSummaryはL22/1・M7/0・B8/2で未達。全APIはcovered/missed **L192/12547、M33/1809、C10/355、B78/4744**、全体100%未達。到達用新assert・除外・旧exec合成なし。

THREAD8は通常JUnit専用のTWR8worker64task・元内側deadlineと外側JVM240s、Map4はDbTime002のcaller逐次CDF写しとDbTime007のsubmission前expected整数Map三つで、workerはrecorder/query/outcome/nsだけをcaptureしMapを変更しない。raw12を保持・source-local contextレビュー完了、**current whole pending/PT免除false**。全F03未受入。

trace983sourceRowsの四元担当/費用ownerを保持しSHAだけ更新、登録1808/不明二・元941/943/全予算/acceptance/旧runtimeを保持、485/486整合検査と全WBSaudit前後1同HOLD。新source全回帰/native/実環境/CHR/全451は未受入、正式1964PT/53scope・個別17/190・工数null・QA051final・QA053元通知現存せず/全安全HOLD不変更。秘密実体/実token0、公開delta限定scanは別記し全G07合格へ拡大しない。
