# Main静的factoryからのDEBUG正常供給・限定単体仕様

2026-10-25/WBS-P018-05（P018-09参照追加費0）/PG-D639補完。群P01805_API_FACTORY_DEBUG_FAKE_SUPPLY_V1、開始0.5/1/2pp cap2固定。fresh59残41/元90捕捉下限84・不明2/正確null、84+2+保全2<=90。新大型群でなく同API供給経路の不足通常PTだけ。RD171/UI252/SS311342343351、1874-75の静的factory/release二入口のみ。

新APIOBSBOOT009を既FactoryTestへ追加、旧8本文不変更・再確認実行なし。新test-only typed HikariDataSource subclassはdefault resource-free constructorだけ、起動constructor/実pool/DB/ネットワーク/credentialアクセスなし。hikaricp.configurationFile propertyの存在を構築前に拒否し外部設定読取を防ぐ。getConnection/MXBean getterを全てfakeへoverrideしsuperのprovider起動に入らない。query/connection fixtureは成功専用、nativeUNKNOWN policyを故意に起動せず、停止確認まで所有を保持する。

入力は独立literalのERROR7/PENDING3/SENT5・age6/2/4秒とpool active3 idle5 pending2 max8、新workerをfactoryからinitializeし、10秒以内にreadonly query→rollback/close後にSDK文字列へ各countが現れることを確認する。動的ageは固定期待にせず許容時刻範囲、request開始/ready・HTTP試験とは別。SDK観測後のMain.closeObservationsでLife stopping、bindings/render停止・worker終端・全借用connection cleanup/Pool所有を確認。finallyは先に観測owner停止、次にfixture dispose。元life budget60秒を使用、新deadlineなし。

normal六は新test source固定後一回。選択新1/1・XML/log/exec/actual source・必要部分coverage/全1843 byte不変/251owner/架構を記録する。Main全体四100/Program PT/451/正式受入は未完のまま。Main object/main/run/hook/TERM/VM/Root/DB/Backup/native/配備はHOLD。失敗・tool費・再認証は別計上。1877へ結果・hash、456/460へ次commandを保存し通常区切りでは停止しない。
