# 合成JMS境界原whole六：通常単体テスト仕様

PG15518/PG-D945、Production6b53/normal14216固定、基点7cf62f904190a613906ed4f73a14066c160f66ea、群3322開始0.5/2.5/6共有枠pp固定。原JmsMessageGuardTest全6、Main JmsMessageGuard/GuardedJmsMessage全2Source/2Code。Mainの正担当は実485のP005-03、protocol P00102/03はhelper参照・追加費用0。followup索引1930/1526/896、全Main/Test/helperを開始前に確認。ArtemisTransportContractTestは実broker起動を含むため別HOLDのまま・抽出しない。

NK-MSG-001、RD MQ003/008/040～045、UI231、SS321§4/8・322、PT-JMS-005/006。6methodの目的：immutable/redactedコピー、null/非Bytes、body長/コピー異常、permanent宛先と正確なqueue修飾、reply有無とallowlist、必須header/property欠落/blank/異常。fixtureは固定UUID二件・byte[1,2,3]、JDK Proxy、Artemis Destination値オブジェクトだけ。broker/Connection/Context/実JMS/native/DB/credential/鍵/Graph/外部操作なし。

期待値は承認SSから独立literalで固定：SYNC body最大1000000、async1000/log10000、宛先nk.sync.request/返信nk.sync.reply.web、固定queueはaddress+.q、wire LOGREQ01/001、deliveryCount>=1/expiration>=0、未知/dynamic/reply不一致はPermanentProtocolException。原Testの過大入力はLayoutDefinition.MAXIMUM_BODY_LENGTH+1を使うため、その定数1000000とBrokerTopology/SSの独立一致をpostで必ず確認する。生成expectedや本番codec oracleは使わない。

原Testを改作/抽出せず一fresh JVM/exec/session、XML6/FES0、現在source/snapshot/normalJar全class SHA/CRCを照合し四counterを実測する。不足は不足のまま、公式生成filter以外の除外0、helper既資格を再加算しない。同execの四held/六native prefix受動検証はHOLD解除ではない。専用post15520を実行前に固定し、独立15422ではなく新15522でliteral/境界/実全Source/限定effect反例を確認予定。commandはpg11123_checked_python_entry.py経由pg15518_synthetic_jms_guard_six_pt.py。環境・source/run/終了/hash/不足/BUGは2942へ。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変。
