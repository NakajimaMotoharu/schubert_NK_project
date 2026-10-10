# WD-BUG-003 (副担当ローカル、正式915採番待ち)

SS313§10はvalidation summary anchorを必須とする。search.htmlはli textだけでanchorもcontrol idもなく、error summaryから対象入力へ移れない。UI222§9 label/input対応と合わせ、固定field名に対応するcontrol idとsummary linkを作る。form/pageは直接の入力controlがないため検索formを対象にする。未知入力値は既存invalid view modelが閉candidateへ保持しth:text/valueでescapeするのでその契約は維持。Production修正前に新pure template fixtureでanchor欠落を再現する。対象search.html、P016-03だけ。controller/security/wireは対象外。
