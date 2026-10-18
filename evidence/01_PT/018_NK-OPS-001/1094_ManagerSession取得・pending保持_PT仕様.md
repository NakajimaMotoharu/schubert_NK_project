# Manager session取得・pending保持 PT仕様

NK-OPS-001/SystemManagerObservation.read、OPS009/SYS002/UI251/SS343354/SSC308・BUG1414/YKT1178/PG-D428/P01804.03（親04非加算・先行02未受入）。原1session factoryの全portを取得前に作り、action先頭の参照登録以外を先行させない。post-finallyは**releaseの後**にclosedを照会、未確認ならpending保持して次read拒否。固定八Unit/五秒whole budget/owner前後二読/固定property・ASCII/foreign-thread・interrupt/IO・unknown優先は既仕様を維持する。

新MANAGEROWN001はfactory IO/Runtime/Error/nullでresource未取得ならclose/body0・元例外identity、次のfresh取得が許可されることを固定counter/events/literalprefixで確認。002は実close後のclosed照会自体がunknownの場合も元例外が優先・pending保持・次factory再発行0・close一度を独立sessionで確認する。期待は固定callback/counter/文字列・元例外identityで独立算出、Production methodをexpected生成に用いない。既七methodの全八target/golden/全故障・期限・不正値/nullable/未確認close/並行threadを当sourceで再検証。新旧計九methodであり初稿の既九表記はsource宣言から訂正、実行予定1092を増減しない。Session内部FFM outpointer四は未完・当1の受入で加算しない。

command `python3 -B tools/quality/pg5348_manager_session_selected.py green --group factory`、予定1092invocation132suite/新独立2＋既78/固定反復1method10回。元source/archive/input/実時刻・OS/JDK/tool/隔離PG binary・command/owner/exit/XML/static/coverage/hashをprivate記録しallowlist公開、秘密0。六format先行/NullAway・ErrorProne0/三static0・全storage四100を確認、対象四counterはmiss含め記録し未網羅を100にしない。全764 actual差とfactory methodref/pending最初・post-finallyの順序を独立検証。whole予定3871PT561suite1661Main/currentnative/全四100は未実行、正式1964/53・leafdelta0/工数null、原本/VM業務DB0と隔離一時PG実働を分離する。
