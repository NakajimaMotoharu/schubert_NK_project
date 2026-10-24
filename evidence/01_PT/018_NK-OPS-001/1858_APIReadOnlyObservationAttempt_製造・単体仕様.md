# API readonly一回観測owner・製造/単体仕様

2026-10-25/PG-D632/NK-OPS-001/WBS-P018-09、RD171/UI252/SS311332342351、1856-57の同一API観測経路。開始HEADc0fb2203f/製品2ed81b14b、fresh共有枠は9062原receipt、低3/基準6/高10pp・群cap10を固定。元/v4/v5/正式1964-53/原190新受入0/工数null/全actualHOLDを維持。

ApiReadOnlyObservationAttemptはresource-free constructorで借用DataSource/Clock/既DAO/UNKNOWN policyと保持stateを準備する。一回だけreadを許し、独立checkoutのautoCommitを確認→readOnly=true/isolation READ_COMMITTED→setAutoCommit(false)→Clock/既DAO一回→rollback一回→Connection close確認後だけimmutable Snapshotを返す。setAutoCommit(false)呼出し前にTX attemptedを記録して曖昧失敗もrollbackする。初期非autocommitを勝手にcommit/rollbackしない。SELECT以外のSQL/業務変更/Pool mode変更/credential読取/worker/SDK/Clock実測は追加しない。

取得後のphase failureでも必要rollback/closeを一回試行し、close不確定はConnectionと全failureを保持して既UNKNOWN policy portへ通知する。実portは既ServiceProcessResourcesの非帰還保持契約に従う。普通PTだけのreturning診断でも同failure非成功・再取得/再close拒否を維持。合成Error優先・元checked/runtime identity・secondary/suppression-disabled/同instance/循環graphは既API TemporaryInfrastructureException helperを使用し、資源後始末後に分類する。provider message/log/secretを出力せず、NPEを成功扱いしない。publication/worker/callerへの組込は本群終了後の依存であり、キャッシュの旧借用conn保証を全Connection owner保証へ推定しない。

ROATTEMPT001～032を新規32件予定。constructor各null・取得0、正常vector/empty/close済後のみreturn、再読拒否、null取得/取得例外、初期TX拒否、各準備/時計/DAO/rollback/close/diagnosticのSQL-Runtime-Error/null、複合failure/fatal graph/抑制無効/同例外、close callback時保持state/再入、同時read二重取得拒否を独立fake JDBC/Clock/有限policyで検証する。expectedは明示phase順とliteral3/5/7・2/4/6秒、返却前のrollback/close回数。製品methodでexpected生成0、sleep同期0/有限latch・finally解放。

source固定→9064正常六compile→9066新32のみ（既DAO fixture outer compile-only）→9068当全Main四counter/NPE/静的→9070全1839Main見込/既1838同byte/239owner見込/五architecture→1859結果・計測・公開scan・commit/push。未実装/TDD・工具構築失敗・実装済み障害を区別し、実装仕様違反は修正前915/共通原因916。実DB/VM/Root/native/拒否対象等には進まない。通常小区切り停止なし、所定利用枠/安全条件を維持。
