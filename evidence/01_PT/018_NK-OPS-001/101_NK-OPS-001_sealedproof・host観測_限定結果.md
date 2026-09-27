# sealedproof・host観測の限定結果（PG292、未認定）

保存基点734e7f12f/dev-foundation＋新Storage sealed proofとnative009工具。2026-09-27 18:11:30 JST、Linux7.0.0-34-generic/JDK25.0.4/Jacoco0.8.15/SpotBugs4.10.4.0。

Storage clean verify125PT、failure/error/skipped0、Java4指標各100%・instruction missed0、静的0/NullAway/Werror成功。新SEAL8件は限定成功、commandは097のStorage clean verify（最後はSpotless済みsourceでclean verify）、source/XML/coverageのhashはprovisional PG292 manifest。初回test fixtureのJunit generic overload/type推論・独立byte oracleは未認定試行で補正してから実検証。既存承認済み業務の違反は発見していないため仮BUG起票なし。

native009初回は仮説失敗: host保持FDでもJava FileStoreがprivate pathnameのROを返す。既存LinuxInodeSecurity native statvfsを使った再試験だけexit0: privateRO=true/hostRO=false/同devino・UID/GID/mode。root sandbox解除なし、Toolはtest-only、既存VM payloadのStorage ABI classを使用（同source保持）し新Production releaseではない。raw systemd output/実Invocation/private journalsはGit外、constant sanitized結果だけ保存。native009はProduction root由来/A/現在許可/全root gateを未認定のままにする。SSC087で別A/古いbind/現在hostRW/最終UID能力を先行補足し、次にread-only host adapterへ実装する。

正式run24/source858713c0b/1,964PT・中心48.3%は不変。全Production/security横断回帰・全scope/実NK CHRは未実行。必須起動gate未組立のためProduction mainは拒否のまま。100とTest ID対応、秘密を保存しない。
