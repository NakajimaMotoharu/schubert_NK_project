# Reference自己同一cleanup追補

BUG3136/YKT2607の同原因横展開。原161はFES0だがPG36930 rawでReference closeStatement:160の自己同一1branch未hit、raw544L/147M/7C/253Bhit1missを保持し品質未合格。新REFSELF002（同SelfSuppression Test class第二method）を追加する。旧160の全六Test file本文/期待、ASSETSELF001本体は不変。

空の公開合成DTOだけを事前構築し、Reference.verifyのsetQueryTimeoutとStatement.closeへ独立SQL/RTE/Errorの同一オブジェクトを与える。期待はsame primary、suppressed0、auto/create/statementClose各1、query/resultClose0、connection close/commit/rollback等はfixture拒否。既FixtureはJDK java.sql Proxyのみ、実DB/master/key/native/Root操作なし。三型を一JUnit定義として新二定義＋元160＝162を一source/run/execへ固定し、旧80/161の成功を算術加算/exec合算しない。全六sourceの未filter四counter、全component未達、全12self条件を再照合する。Source/Core/Unit/command/exit/input/XML/raw SHAは新profile/manifestを正とする。元A1.2/cap4/全品質/元見積/各HOLD不変更、実費不明を0にしない。
