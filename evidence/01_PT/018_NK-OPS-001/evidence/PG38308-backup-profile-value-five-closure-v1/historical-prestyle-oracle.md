# BackupProfile公開値同値・キー検索単体試験仕様書

NK-BAT-001、PT-P01810-CATALOG-043-value-identity、UI251、SS343/SSC110・SS351・451、BUG-3220/YKT-2672。担当P017-06。対象は `BackupProfile.equals/hashCode` と、元四件で確認する公開claimの保存・境界・消去・診断。製品Core `47aeed19a157661363ffab5c4b5054f6b20230a1`。元仕様4201とBPROFILE001～004を保持する。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-P01810-CATALOG-043-value-identity | 元固定JSONから得たprofile、同内容を八つの版と七つのキーのリテラルで別構築したprofileを用意する。前者をキーに固定文字列をHashMapへ保存し後者で検索する。版とage hashの片方だけを変えたキーでも検索する | 同内容は双方向に等値で、別キーinstanceで固定文字列を取得。版のみ差とhashのみ差はそれぞれ不等値で、保存値を取得しない。実際のhash値を期待値に使わない |
| BPROFILE001～004 | 元全四・同じ固定JSON、空・DEL・上限超・未知・null・不正hash及び元の所有・出力確認 | 4201の固定JSON/診断、例外と消去・不変条件を変更しない |

Fixtureは非機密の公開値だけを使用する。並行、再送、実署名、DB、原本ファイルとnativeはこの値型に対する試験対象外。純Java公開値の1追加と元4を同じJDK25実行で測定する。現Mainを変えず、元execと合算しない。全2物理型のCRCを照合し、対象Profileの物理13メソッドと四指標・命令・複雑度の未達0を確認する。依存BackupVersionsの実測不足は別掲する。

実行は標準閉域runner、対象設定はinputのprofile、それぞれの静的・preflight・unit・独立postのcommand/環境/commit/xml/hashを結果書に記録する。
