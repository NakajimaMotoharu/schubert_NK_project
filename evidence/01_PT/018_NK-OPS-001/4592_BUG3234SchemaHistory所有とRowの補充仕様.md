# BUG-3234 SchemaHistory所有・Rowの補充仕様

SS331/332/343、UI243、PT-OPS-SCHEMA001..011、451、SSC461。query／rowsのnonnullを所有確立時に確認し、各closeは一回かつrow→queryの既順。借用connectionは無変更。SQLException/RuntimeException/Error原順とidentity、既known診断化は元whole10の独立matrix。PG38642で特定された正常／異常同一finallyの四条件重複は、非null所有とtyped closeへ整理し、除外は追加しない。

新011は合成SQL row rank1・版001・固定例示script・checksum19・成功true。success固定true、JDK25のrecord field順固定表示、独立31進fold値を照合する。実SQL／権限／Rootは別条件。十一件を同一新sourceで実行し、原独立証跡は別source。選択2 classとサポート全体の未到達をそれぞれ保存。

## SSC-474 借用資源の解放後の中断

BUG-3376／YKT-2721、SS343 §9.1、RD DAT-009/SYS-002、UI212/253。PT-OPS-SCHEMA012は借用JDK ProxyのResultSet.close、013はPreparedStatement.closeが正常に戻る際、呼出しスレッドの割込フラグだけを設定する。固定の正しい六列fixtureを返す。開始時と末尾nextでは割込なし。希釈せず両例でSQLSTATE 08001・固定診断、行→文各1 close、借用Connectionにclose/設定なし、割込flag保持を期待する。既007と例外優先・並行・全入力の原試験も修正候補で保持する。実DB・接続・配備を扱わない。
