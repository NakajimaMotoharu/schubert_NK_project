# API/Web caller-held metric context PG/PT

NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D617、主P018-09/C07追加費0。group2045/開始fresh42残58/reset1793382075/3-5-9pp/cap10。1814/8734の正式SS3doc/public11sourceで必要依存を確定、各roleにApiMetricContext<T>/WebMetricContext<T>新Main2/Unit2、POM/上位/既Mainは不変更。

constructorはresource-free、callerが先にownerを保持してからinitializeする。固定custom SDK factoryとfresh standard ownerを保持、STDはfactory/setup/standard bind未読、DEBUGはcustom registryを即保持→setupの非resource bindingsを強保持→standard bind。missing/null/失敗やstop競合で成功render/再initializeを許さず、partial資源を残してcaller明示closeへ渡す。modeは各既role診断、renderは既full overloadへ借用して新data/全catalog充足やservice healthを捏造しない。setupはpre-acquired入力によるmetadata登録だけ、新DB/JMS/worker等の取得やcontext lifecycle再入をしない契約。bindingsは借用metadataであり暗黙closeしない。

closeはatomic stopを先に通知し、private lockの競合又は同thread再入を即時未確認として拒否する（無期限待機/強制解除なし）。新accessを拒否して全SDK ownerを保持、進行中の一回が終端した後にcallerが明示再closeする。取得できればstandard（GC含む）→customの逆順、失敗はinitialized/closed成功へ変換せずrefsを保持する。停止中のinitializeは各callbackの後に検査し新GC開始や初期化成功を抑止する。actual stop全budget/native資格をこのcomponentのSDK closeだけで認定しない。

APIMCTX001～026/WEBMCTX001～026各26、計52/2。各classのctor二種/initialize/bindings/render/rejectStopping/requireRunning/close/default custom factoryが対象。fixtureは固定mode/String・metadata/array・own SDK・package内custom/standard factory port、有限latch workerのみ。期待は手書きready/custom/standard literal、独立Runtime CPU値、固定count/order、元例外identity、private source保持とstop状態。production render/initializeをexpected算出に使用しない。

|末尾ID|目的・入力/操作|独立期待|
|---|---|---|
|001|STD constructor→initialize→render/bindings|両factory/setup未読、ready1/0固定byte、bindings空|
|002|default DEBUG、Gauge metadata強保持/値更新、公式SDK|binding同一性・7.5→9.5 literal/独立CPU値/借用source保持|
|003|未初期化/close-before-init|render/bindings拒否、以後initialize不可/取得0|
|004|constructor null/未知mode|各既mode契約で取得前拒否|
|005|null setup/factory/standard|constructor invariant拒否、取得0|
|006|custom factory Runtime|元identity/一回・再init/成功view0|
|007|custom factory Error|元identity/自動retry0|
|008|custom factory null|NPE契約違反・成功偽装0|
|009|closed custom candidate|setup/standard未読、明示cleanupだけ|
|010|setup Runtime|partial custom保持/標準未開始|
|011|setup Error|原Error保持/partial保全|
|012|setup null bindings|NPE拒否/partial保全|
|013|standard factory Runtime|bindings/custom先保持・元identity/未成功|
|014|standard factory Error|元Error保持/未成功|
|015|standard factory null|NPE拒否/partial custom保持|
|016|standard close失敗|custom未close・新access拒否・明示再closeで逆順解放|
|017|custom close失敗|standard成功を繰返さずcustom保持・明示再close|
|018|SDK取得callback時のowner捕捉|caller slotが両SDK取得より前に保持済み|
|019|initialize二回/close冪等|一回だけ取得/登録・二重close0|
|020|custom render故障と明示再render|原例外/owner保持・factory再取得0|
|021|render中の別thread close|即時未確認・新access拒否、進行中一回は所有資源で終端、後の明示cleanup|
|022|standard render Runtime/Error/null|原identity/nonnull境界拒否・構造owner保持/自動fallback0|
|023|custom factory又はsetup中stop|未確認close/partial保全・新standard開始0|
|024|standard factory中stop|SDK保持後のinit成功抑止・両資源保全/逆close|
|025|setupからのclose再入|即時未確認/partial保全・新standard開始0|
|026|render callbackからのclose再入|未確認を伝播/全owner保持・後の明示cleanup|

source固定後8740 normal六module→8742 actual52/2→8744当2Mainの全line/method/class/branch100/静的PMD-CS-SB/七metadata反例→8746全1830/旧1828-原1669同byte/全217owner/五edge・resource source非公開/stop-lock/強保持→1816/scan/保存push。既50/旧52ではない他unit/原4222確認再演0、旧exec union/抑制/除外0、failed/skipped/notrun合格化0。全source/command/環境/日時/branch/exit/input期待実際/coverage/BUG/hashはmanifest/result、障害修正前915/916。

着手時52 UNRUN。実manager/default socket/Root/VM/native/DB/JMS/Backup/鍵/privilege/配置/observer/job操作なし、scope拡張/終了条件緩和なし。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/全actualHOLD・元-v4-v5/原本等不変更、通常小区切りで停止しない。
