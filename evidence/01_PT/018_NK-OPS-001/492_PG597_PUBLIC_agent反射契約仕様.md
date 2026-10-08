# PG597 PUBLIC agent反射契約

Program NK-OPS-001、FixedNativeCoverageCheckpoint.PublicAgent、P018-08.01/.02、SYS002004/OPS009/TST004/UI212251/SS342343354451/SSC193/PG-D395。通常defaultの固定system loader/二FQN/AGENT_PATH/公開Method三本/nonreset falseを維持、private内部portだけを試験し、fixtureをnative authority/source認定にしない。

NCHECK597001 正常：実public Java reflection fixtureの版0.8.15・固定Session文字列・独立golden wire、Class二本/source検査順序・三method戻り値・false引数を確認。expectedはfixture literalでProduction生成0。

NCHECK597002 Constructor：null依存、Class未取得/欠落/例外、method欠落、getAgent null/wrongtype/InvocationTargetException、source refusal/URI失敗を別new instanceで拒否。raw private診断/causeを公開せずfixed拒否。

NCHECK597003 Result：version/session/dataのnull/型不一致/反射例外、正常public getterは閉じた型だけ受入。data portはfalse一回・reset呼出0。

NCHECK597004 Source：公開ClassLoader/ProtectionDomain/CodeSource fixtureでcode source無・location無・誤path・固定pathを分離。固定pathのmetadata受入は実agent hash/owner/read-only/実Unit認定ではない（別verifyPinnedAgent/nativeが必要）。

NCHECK597005 外側checkpointとのjoin：既checkpoint正常・point消費/再試行拒否/単Session・header/長さ/非reset・export失敗/観点を同選択へ含む。対象commit・実command・四coverage/static・実結果・BUG/evidence/hashは実後追記。中断/skip/flaky/別sourceは加算0。PG596六3450は旧main1600で保持し、新Production byteへ流用0。export-after-snapshotの未観測依存は別に保留する。
