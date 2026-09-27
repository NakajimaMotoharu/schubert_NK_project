# PG290 限定実行結果（正式不認定）

2026-09-27、branch dev-foundation、基点e6f20fd46＋PG290 dirty。横断triggerは共用Resource/security/POMのWeb結線（D01/02/05）。17:12:53頃～17:26:39 JST Production6 module回帰1,945PT、fail/error/skip0、SpotBugs0。共有71PT全counter missed0。API/Web native main各9instruction/3line/1methodが未網羅、必須gate未組立を除外しない。105負canary成功。formal全scope収集は未実行。

native001～006は実UID/LoadCredential/正SCRAM/誤password拒否/復元に成功。007/008もJava25への同OFD保持・受領後CLOEXEC・readonly・明示group/zeroCaps・競合拒否/close解除に成功。VM `/opt/pgpt-native` payload SHA256 `966fac9f9bba08efbba35a928e29cfc1ddd66f40a1a161ca96c898ce2c1e52a7`、used ServiceProcessResources.class SHA256 `fa6622a1e3ad2d6b2d387ec678ee7b368550456e0bc50933ec5cbae741ced8ed` とhost再compile一致、WebJdbcPool.class `b2fd930a5feaf6398d7cf07575bb05e0c09fa0788f0fe72dd3e45c148b125c16` 一致。payloadには旧WebMain等未使用classも含まれ、完全Production release/source一致やR2成功とは宣言しない。

初期WEB新規PTのexpected role誤記はSS331/DDLを独立照合して訂正、初回format違反runは不認定、通過runだけを上記暫定結果とする。BUG261～264/YKT195～198は限定再試験済み・正式gate待ち。SRC/PT/collector public hashとsanitized native結果はmanifest。Current baseline不変更。fullroot/Ops/schema/Expiry/fresh gate/単一instance/正常なProduction外部起動・停止/実NK CHR-A01/L01は未受入。
