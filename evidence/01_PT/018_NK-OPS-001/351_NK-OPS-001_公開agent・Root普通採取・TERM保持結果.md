# NK-OPS-001 公開agent・Root普通採取・TERM保持結果

2026-10-06、限定host・native未認定。対象sourceは各manifestのdirty hashを正とし、後続sourceへ流用しない。

- checkpoint-v4/session93366 actual0：72PT/11suite/FES0/static6zero、manifest SHA941116fd69002c95417f7516a3e698eaf91e1be597e335602904c4ceb9e29e78。v1 NullAway境界compile、v2 portability3、v3旧main test checked IO宣言compileのactual1を不合格/not-runとして保存。BUG752/YKT532は3method限定の既固定Linux portability理由付け、NPE/coverage/他解析除外0。
- checkpoint-v5/session85767 actual0：78PT/12suite/FES0/static6zero/formatNullAwayWerror、03:38:48.569355795～03:41:06（終了詳細はmanifest）。SHA73ca6ffbd50ff98c36cac151b8641ffe1dcb27c80dba2f7472a33f3b4fdf022c。BUG753の独立race・interrupt/owner/knownunknown/閉状態と実host子TERM→旧hook帰還→追加hold待機→採取完了→143を実証。実API/Web VM TERM/native100の代用0。collector初稿はprivate.log suffix漏れでnooutput/actual1、修正稿actual0だけ採用。
- v5参考miss：profile全4counter0、checkpoint B1/L6/M1/C0、privateFile B61/L99/M12/C0、hold B1/L2/M0/C0。内側PublicAgent/record/adapter及びnative-only面も残る。累積開発execにつき正式100ではない。v5後のhold owner条件順序はclosed先行へ論理同値で整理（closeがinstalledを消費するため後段closed trueを到達不能にしない）、新source検証はfresh全6で行いv5 hashへ偽装0。

Source/実VMは別：VM signed/current D3/PG469、新checkpoint/hold groupは未配備、stop/start/permit/reset0。既同D3のfresh3301/親/Backup/原本DONE/A01/Log337・断5再送/4native streamsを保持。正式run24/1964PT53scope/48.3%は不変更、fresh全6/実native全100/CHR/DIF残/PGPT/ITST未完。意味あるgroup保存後も継続する。
