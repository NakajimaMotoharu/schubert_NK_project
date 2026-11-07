# F03通常TestのProxy loader九三site個別適用性

WBS-F03、402/451/SS351352。着手見積1/3/7pp cap9。先行3654/3655の347 rawのうちUseProperClassLoader93siteを対象に、同Test source/hash・原XML ordinal/全属性・実引数式・import・明示型を個別照合する。原347/raw exit4は保持し、対象外254を未分類のまま残す。

同規則のJ2EE TCCL推奨に対し、対象はsrc/test/javaの独立JUnit/port helperで、製品Jarへ含まれない。判定対象はjava.lang.reflect.Proxy.newProxyInstanceの第一引数だけ。型のdefining loader、同loaderに載る自Test/Fixture、又はClass型parameterと同じinterface arrayを渡す限定形を確認する。JDK SQL/Jakarta Servlet/JMS/Artemis public interfaceの名前は明示importへ束縛し、Proxy以外・対応しない型/line/import・ClassLoader変更・Main/server source・来歴未確認は非該当へしない。rule名/pathだけの一括免除は禁止。

既個別静的判断の検索を拡大する代わりに、今回の93実source位置・call引数を直接確認する。scopeは元85内だけ、原held名はIO前拒否。製品/Test/fixture/compile/PMD再実行やreflection invocation、外部接続0。実sourceを静的データとして扱い、Root二Test/保護二fileを読まない。synthetic metadata反例で適用条件の拒否を検査する。

source編集・抑制・規則緩和なし。原rawレポートと新sidecarの個別reasonを分離し、独立postが元347・対象93・sourcehash・context/arg/import・否定条件・対象外不変を確認する。静的分類はProduct PT/coverage/新leaf/正式/工数率へ換算しない。全Test/global F03・451/全HOLDは維持し、未証明siteを成功へしない。


## 規約参照番号の追記訂正（2026-11-07、BUG2430/YKT2175）

上記402は411の誤記。実正本はdocuments/400_PGPT/410_工程標準/411_コーディング規約.md。元本文・event/予算/期待値は保全し、この番号訂正は仕様/規則設定/抑制/実装変更ではない。
