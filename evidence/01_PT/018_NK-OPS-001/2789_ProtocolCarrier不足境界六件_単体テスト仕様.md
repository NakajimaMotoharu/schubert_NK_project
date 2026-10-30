# 2789 ProtocolCarrier不足境界六件仕様

着手event3182、予算low/base/high .5/3/7pp（shared枠、実token/専有費null）、source6b53/normal14216固定。2788で実証した未網羅二Sourceを追加試験する。既31の確認再演・exec unionではない。原Main/Testは変更せず、新PT sourceをtools/quality/architecture/ProtocolCarrierBoundaryTest.javaに保存し、固定Main Jarに対しfresh javac/JUnitを行う。全6 methodを一回実施、own二reader threadは有限期限/finallyで閉じる。WBS-P001-02/P001-03、原関連RD/UI/SSとProgram class/methodは2787/原14360のtraceを継承する。

|Test ID（PT-OPS-2789-）|method/目的・独立期待値|
|---|---|
|01|textRedactionAndPrimitiveBoundaries: Textの固定redaction/UTF16 length14/0/2、null message=value、long極値、flag両値、enum固定INSTANCE|
|02|emptyAndAbsentHaveExplicitUnsetContract: size0/names空/未知Unset/toString固定/hash0、null name拒否|
|03|immutableOrderedDefensiveCopy: LinkedHashMapの二項目順とidentity、元map変更非反映、names変更拒否/不変を再確認|
|04|invalidMapsAndNullEntriesAreRejected: null map/key/valueの固定message、空/space/tab-newline/全角spaceのblank拒否|
|05|equalityAndHashFollowIndependentMapContract: self/equal/different/null/異型でequals全条件、Map契約から独立にhash82/83（ASCII x120 XOR long42/43）|
|06|independentReadersObserveSameImmutableSnapshot: own2thread/4reader、5秒期限で固定表示、future結果確認とfinally終了|

fixtureは公開合成値のみ、real secretなし。期待値は文字列literal/Java collection・primitive契約から独立に作成、Production methodによるexpected生成0。各Testは無引数JUnit、外部I/O/DB/JMS/Graph/OS/VM/鍵/permit/Rootなし。nullはtest assertionで拒否を確認し、実装でNPEを正常catchしない。新規試験・oracle全bodyおよびFieldValue/FieldValueSet/LayoutValidationExceptionの必要Mainを実施前に読む。

実行予定：checked Python entryのPG14868専用runner、一回ownJVM/新SLOT/180秒timeout。新execのみでFieldValue全5physicalとFieldValueSetの全closureを解析、interface metadataをN/Aと分離する。旧execへ合算せず、新結果のsource/CRC/独立post/全counterが揃うまで成功・受入に数えない。実行command/hash/OS-JDK/時刻/exit/coverage/関連BUGは2790へ保存する。全451/F03/正式/QA051final/HOLDは変更しない。
