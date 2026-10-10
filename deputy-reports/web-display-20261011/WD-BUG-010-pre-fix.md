# WD-BUG-010 (副担当ローカル、正式915採番待ち)

UI222§6/SS313§6.1は新規50件/page一覧にも上下の前のN件/表示範囲/総件数/次のN件を求める。Question/Notification/User一覧は上の前へ/次へだけで共通契約を満たさない。UI222§3/SS313§10の900px以下/列見出し維持scroll containerも現tableにない。予約済み共通pagination.htmlへ50件fragment、CSSへ50件nav/scroll containerを追加し、画面への接続は各画面固有工程へ分ける。共通実装/PTはP015-07/C、CSS規則はP016-25.04/Bの同じ群予算参照とし、各画面へ二重計上しない。既存検索/Log100件fragmentを変更しない。新Production file追加0。
