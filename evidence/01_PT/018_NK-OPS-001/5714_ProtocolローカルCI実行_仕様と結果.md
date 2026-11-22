# ProtocolローカルCI実行

NK-OPS-001、WBS-P018-02/2、RD171 SCM-004/005、UI201/243/261、SS352 §13、SS354。PT-OPS-CI-PRO005で現 `tools/quality/verify_protocol_ci.sh` を使い、空の隔離checkoutにProtocolの製品・試験と他moduleのPOMだけを置いた。JDK25.0.4、Maven3.9.12、PG42736の照合済みWrapper cacheをコピーし、既Maven repositoryでoffline。通常のJUnit目録と期待39 suite／171件は先行PG42624の固定XML確認から用意した。

PG42762では終了0、実171成功／39 suite、失敗・エラー・skip0、旧目録と全ID一致。現JARの176 classが比較元と同じクラスバイト列。ZIP全体のSHA-256は異なり、実際に生成したJARのSHA-256を記録した。SpotBugs指摘・処理エラー0。標準JaCoCoはline3551、method751、class162、branch1080で全未到達0。旧の生counterと合算していない。F02の六製品同時検証、SCM-005全体、外部CI、現配布承認、正式451は継続する。[PG42762](evidence/PG42762-p01802-protocol-real-local-ci-v1/manifest.json)
