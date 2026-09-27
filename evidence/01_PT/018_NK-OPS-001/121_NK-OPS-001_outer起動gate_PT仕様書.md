# 子outer起動gate PT仕様書（PG301、未認定）

Program NK-OPS-001、Bootstrap.ServiceStartupAdmission.create/execute/Configuration/NativeGate/NativeObservation、ChildStartupContext.isDescriptorKey、API/Web main・loader・Inputs。RD SYS-002/004・OPS009、UI212・251、SS311/342/343 SSC086～089、BUG266/268/269・YKT200/202/203、D04/05。

| Test ID PT-OPS-STARTADMIT | fixture・入力/操作・独立期待値 |
|---|---|
| 001 | 独立17行canonical公開packet、PID42/ticks12345/UID200/GID201/groups200,201,202。root2FD→proof close→config load→kernel/NSS/actual release→自己再観測→同immutable値factory→実ready A release→cleanup→outer A close。API/Web cgroup両方 |
| 002 | descriptor env欠落/同番号/0/未真正native gate。config source0/業務factory0/ready0、gate内拒否はA close |
| 003 | version/必須key/service/空packet不正、固定redacted IOException・cause0、自己/業務未読 |
| 004 | service/PID/A番号-dev-ino/config/release独立変更、自己再capture変更。検証後だけfactory、差分時factory0 |
| 005 | config読取IO/null、各kernel/NSS/manifest IO、未知例外identity。configもnative所有callback内、故障時factory0・全owner解放 |
| 006 | 業務callback失敗では業務cleanup後A解放、close失敗非成功、未知IACを設定不備へ変換しない |
| 007 | 全null/collection/hash長・canonical文字制約、固定2FD env名だけ認識、任意alias/秘密名は認めない。名前認識自体は入場ではない |
| 008 | 32並行独立scope、開発hostの未継承FD65534/65535を真正proof扱いしない、native adapterの残成功経路は隔離VM018/019へ対応付け |

両LOAD005: 正確な2FD名は設定入口の名前allowlistで認めるが不正値も設定loaderだけでは評価せず、native gateで拒否。lowercase/追加suffix/任意namespaceをsource読取前に拒否。両MAIN001～004/INPUT001～004の既存独立exit/診断/argv/env/null/unknown/source故障を再実行。Production runは非IO argv/env先行検証の70契約を保持し、source load/hashは2FD内。設定不正70/IO50、resource前失敗factory0。注入Startup試験は実root入場を主張しない。

実行command/日時/source/coverage/OS/version/BUG/SSC/証跡hashは122とprovisional manifest。fullissuer現在原本・root/Ops/schema・morning実step・業務runtimeは別必須未実装、unassembledStartupを成功にしない。Native018/019はpublic fixture/BOM=false、実NK/CHR受入へ加算しない。
