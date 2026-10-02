# 314 NK-OPS-001 署名boot設定固定BOM

選択実測：2026-10-03 01:59:36 JST、pg430-boot-bom-selected.log、exit0、100PT/15suite/FES0、SpotBugs6module各0。FULLBOM010とISSCOLD008を含む最終Source固定前の暫定試験。最終全6spotless:checkは02:12:45 exit0。全6freshとnativeの証拠を代替しない。

2026-10-03、RD SYS004/OPS009、UI251/253、SS343 SSC165/167、BUG536/YKT380。対象ReleasePayloadVerification.layout/全tree/file、AssembleReleaseFixtureの固定tmpfiles copy。既存署名/readonly/inventory/所有/再open/全jar/sql/未知path拒否は不変更。

FULLBOM010：独立public ASCII固定boot内容を `config/tmpfiles/schubert-nk-maintenance.conf` に保存し、独立MessageDigestでSHA/全artifact数を照合する。fixtureはsynthetic privileged metadataでありnative admissionではない。`other.conf`、`.conf.extra`、`private-key.pem`、`.service`は全拒否、同fixed pathの署名後TAMPEREDも拒否する。Production layout methodでexpectedを作らない。既存FULLBOM001..009及び署名/inventory負試験も回帰する。

PG429旧candidateはSourcec3/181artifact/61deps/25SQL/39983byte、原署名成功後全BOM拒否exit1、current/approval/permit不変。private拒否logとfrozen candidateを保全、上書き/再署名/permit迂回をしない。新Sourceでshared6全回帰→PG430新label/署名→正規verify/activate→通常Morning/freshBroker/親API ready→保持Webを次外部観測とする。導入tmpfilesを同梱のみで本番boot完了化せず、既存lockの再作成/稼働中tmpfiles再実行はしない。

環境/command：既存JDK25.0.4/Maven3.9.12・strict compile、選択15suite（既存6moduleの実在suite＋FULLBOM/同cold8/旧STOP）/static6/coverage、全6clean/format/PT/static/JAR/runtime inventoryは451と456所定。同Source全6実測は `evidence/provisional/PG430-full-boot-bom/manifest.json`（未存在時未実行）へ日時/source/branch/command/exit/FES/coverage/BUG/SSC/hashを集約する。signature秘密key・原電文・DB原本・credentialはGitに格納しない。native・coverage100/全正式scopeは未認定のまま。
