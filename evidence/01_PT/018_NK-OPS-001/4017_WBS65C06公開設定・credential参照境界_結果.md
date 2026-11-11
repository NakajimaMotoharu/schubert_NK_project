# WBS65 C06 公開設定・credential参照境界 結果

2026-11-12、原1.5/4/8pp・cap8、PG26138 actual0（10b72b413cfd460705eebf82ca4c5848925d3342a8cca0cb325d5ec647e496f4）。Main7aed不変。

現descriptorのC06七owned resource/hashを固定。Common3/API20/Web17/Batch11＝非秘密51設定をSS343 §4–5と既固定goldenへexact比較。両.envは固定一行＋LFのみ、Inspector.envは既非秘密二行placeholderだけ。asset件数59627はSSC150の既Production設定値で、master実体やDB内容を読んで生成しない。max session2はDIF016の設定値対応で、実3件目Login/古session revokeの成功証明ではない。

両Unitの公開LoadCredentialはAPI五/Web五の順序・ID/source path一致、集合の重複0。Inspectorはbase四/optional0,1,1,2でprofile4/5/5/6をsource照合、既当変更後PG26100の原八＋owner六内のprofile成功だけを参照し再演0。ここで確認したのは公開ID/名前/参照/設定値であり、private fileの読取や暗号primitive/key/sessionの資格確認ではない。

実credential/source/runtimeの権限・inode/ACL/nlink/size・systemd配布/readiness、鍵長/current-previous版binding・保持session有効性・rotation/retire・redactionは未測定/HOLD。Sourceの固定文字列を実配布や実認証の成功へ換算しない。結論C06 NOT_ACCEPTED、製品PT/coverage新測定0、新元190受入0、正式1964/53と工数nullを維持。

manifestに七resource/両Unit/設計origin-main hash・golden51値・公開10ID・四profile・既proofhashを保存。次C07はcurrent descriptorでownedの監視八resourceを正に読む。旧481のowned空は歴史projectionなので、current projectionのC07八を欠落させず、主担当費は一度だけ。Prometheus/Grafana/data retention/実scrape/停止は既HOLDを維持。

資格追補（BUG2640/YKT2320）：26100の元14成功は保存するが、runtime CP旧Jar混入で同source資格はREOPENED。ここでの七template/公開IDの静的hash一致は不変であり、実配布/鍵/rotationを認定していない。是正後の当source再資格proofへ後続で結合する。

## 現source専有runtime資格の更新（2026-11-12）

BUG2640旧Jar排除後のPG26154全14成功/50receipt→PG26156独立a1b83f73で限定再試験資格を復帰。旧26096/26100は実成功の履歴で専有資格は撤回済みとして保持し、本current資格へ二重加算しない。追加Test定義0、Maincoverage/全C02/実認証等を認定しない。詳細4020。
