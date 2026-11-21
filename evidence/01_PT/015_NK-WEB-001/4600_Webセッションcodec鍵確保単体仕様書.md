# Webセッションcodecの鍵確保 単体仕様

NK-WEB-001、WBS-P018-10.03、SS314／331／352、BUG-3485／YKT-2779。PT-WEB-016～023とTOKV206の既9件。既JSON／JCAのgolden、現/旧鍵とclose、null、例外、並行の本文を維持する。

PT-WEB-SESSIONKEY-001は構築bytecodeが全事前検査後の一回確保と固定32 byte領域の二copyになることを検査する。旧複数cloneは静的構造で再現し、実OOMを起こさない。GsonはWeb POM 2.14.0、Protocolは既正規同入力JAR。SessionAttributeCodecTestは既独立fixtureを提供するためにcompileする。製品の実Web/session/DB/鍵には接続しない。

再現 `python3 -B evidence/01_PT/016_NK-WEB-002/input/071_revoke_key_ownership.py baseline session` と同 `changes session`。既runの再起動を避ける。
