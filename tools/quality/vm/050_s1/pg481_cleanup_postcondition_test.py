"""Independent public full-row fixtures; no Production method or VM mutation."""
import copy,importlib.util,pathlib
p=pathlib.Path(__file__).with_name('pg481_cleanup_postcondition.py');s=importlib.util.spec_from_file_location('fixed_oracle',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
n=0
def check(v):
 global n
 assert v;n+=1
def refused(call):
 global n
 try:call()
 except (ValueError,KeyError,TypeError):n+=1;return
 raise AssertionError('changed retained value accepted')
rows=[{'id':'one','secret':'private-full-column','value':None},{'id':'two','secret':'other','value':7}]
check(m.canonical(rows)==m.canonical(rows[::-1]));check(m.survivors(rows,['one'],'id')==[rows[1]])
for deleted in [None,['missing'],['one','one'],[None],['']]:refused(lambda:m.survivors(rows,deleted,'id'))
for bad in [None,{},[None],[{}],rows+[rows[0]]]:refused(lambda:m.canonical(bad))
for bad in [[{'id':None}],[{'other':'one'}],[{'id':'one'},{'id':'one','other':True}]]:refused(lambda:m.survivors(bad,[],'id'))
old={table:[{'id':1,'run_id':'old-run','value':None}] for table in m.GENERATED}
for table in ['schubert.answers','schubert.app_users','schubert.async_jobs','schubert.audio_files','schubert.entry_audio_links','schubert.games','schubert.media_assets','schubert.script_entries','schubert.script_files','schubert.speakers','schubert_web_session.pending_context_revocations']:old[table]=[{'literal':'unchanged','value':None}]
expected={}
for table,(selector,key) in m.SELECTORS.items():
 amount=1381 if selector=='web_http_sessions' else 1 if selector=='auth_sessions' else 0
 old[table]=[{key:str(i),'allOtherColumns':['independent',None]} for i in range(amount)];expected[selector]=[str(i) for i in range(amount)]
old['schubert.request_inbox']=[{'message_id':str(i),'wire':'independent-public-vector'} for i in range(7)]
new=copy.deepcopy(old)
for table in m.SELECTORS:new[table]=[]
new['schubert.request_inbox']=[]
for table in m.GENERATED:new[table].append({'id':2,'run_id':m.RUN,'value':'new-not-accepted'})
oracle={'sameThroughoutAdmissionWindow':True,'inboxExpectedDeleted':[str(i) for i in range(7)],'expected':expected}
check(len(old)==24);check(m.evaluate(old,new,oracle)['schubert.auth_sessions']['deleted']==1)
for table in old:
 bad=copy.deepcopy(new)
 if bad[table]:bad[table][0]['tampered']=True
 else:bad[table].append({'id':'unexpected'})
 refused(lambda:m.evaluate(old,bad,oracle))
for table in m.GENERATED:
 bad=copy.deepcopy(new);bad[table][-1]['run_id']='foreign';refused(lambda:m.evaluate(old,bad,oracle))
bad=copy.deepcopy(new);del bad['schubert.answers'];refused(lambda:m.evaluate(old,bad,oracle))
print('PG481_CLEANUP_FULLROW_ORACLE assertions='+str(n)+' actual0=true productionPT0=true vmMutation0=true')
