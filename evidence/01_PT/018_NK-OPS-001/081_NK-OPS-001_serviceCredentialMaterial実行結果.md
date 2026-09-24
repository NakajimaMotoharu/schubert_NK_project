# NK-OPS-001 service credential material実行結果

PG282/SSC-081、PT-OPS-CREDREAD-009～012。2026-09-25、branch`dev-foundation`、Linux/JDK25.0.4/Maven wrapper。API選択12 PTはfailure/error/skipped0、API全module verifyもexit0（API779PT、JaCoCo `ServiceCredentialReader` instruction/branch/line/method/class missed0、SpotBugs0）、collector自己試験103件PASS。全reactor正式run、53scope/hash・対象commit固定は未実施のため、この段階は正式合格ではない。選択試験の初期失敗はtest fixtureのbuffer長期待の誤りであり、test修正前結果は不認定。実systemd/OS配布、DB/MQ driver・外部main、実NK CHRは未認定。
