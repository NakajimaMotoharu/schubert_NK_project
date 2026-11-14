"""Hand-written V002 constraint matrix independently checked against source DDL; never product methods."""
from pathlib import Path
import json,re,hashlib,datetime
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V002__account_session_and_master_tables.sql';s=ddl.read_text()
# name/type/conkey/reference/actions are independent literals; suffix is expanded only within its table.
raw={
'speakers':'''pk_speakers p 1 - -
uq_speakers_game_normalized_name u 2,4 - -
uq_speakers_id_game u 1,2 - -
fk_speakers_games_game_id f 2 schubert.games(1) a/r/s
ck_speakers_id_n12 c 1 - -
ck_speakers_name_bytes c 3 - -
ck_speakers_normalized_name_bytes c 4 - -''',
'script_files':'''pk_script_files p 1 - -
uq_script_files_game_storage_path u 2,4 - -
uq_script_files_game_display_order u 2,3 - -
uq_script_files_id_game u 1,2 - -
fk_script_files_games_game_id f 2 schubert.games(1) a/r/s
ck_script_files_id_n12 c 1 - -
ck_script_files_display_order_n12 c 3 - -
ck_script_files_storage_path_bytes c 4 - -
ck_script_files_storage_path_safe c 4 - -
ck_script_files_display_path_bytes c 5 - -
ck_script_files_file_name_bytes c 6 - -
ck_script_files_chapter_title_bytes c 8 - -
ck_script_files_sha256 c 9 - -
ck_script_files_byte_size c 10 - -''',
'script_entries':'''pk_script_entries p 1 - -
uq_script_entries_display_order u 4 - -
uq_script_entries_file_entry_index u 3,5 - -
uq_script_entries_id_game u 1,2 - -
fk_script_entries_games_game_id f 2 schubert.games(1) a/r/s
fk_script_entries_script_files_file_game f 3,2 schubert.script_files(1,2) a/c/s
fk_script_entries_speakers_speaker_game f 8,2 schubert.speakers(1,2) a/r/s
ck_script_entries_id_n12 c 1 - -
ck_script_entries_display_order_n12 c 4 - -
ck_script_entries_entry_index c 5 - -
ck_script_entries_line_number c 6 - -
ck_script_entries_entry_type c 7 - -
ck_script_entries_speaker_by_type c 7,8 - -
ck_script_entries_speaker_label_bytes c 9 - -
ck_script_entries_body_bytes c 10 - -''',
'audio_files':'''pk_audio_files p 1 - -
uq_audio_files_game_storage_path u 2,3 - -
uq_audio_files_id_game u 1,2 - -
fk_audio_files_games_game_id f 2 schubert.games(1) a/r/s
ck_audio_files_id_n12 c 1 - -
ck_audio_files_storage_path_bytes c 3 - -
ck_audio_files_storage_path_safe c 3 - -
ck_audio_files_display_path_bytes c 4 - -
ck_audio_files_file_name_bytes c 5 - -
ck_audio_files_basename_bytes c 6 - -
ck_audio_files_audio_role_bytes c 7 - -
ck_audio_files_duration_ms c 9 - -
ck_audio_files_byte_size c 10 - -
ck_audio_files_sha256 c 11 - -''',
'media_assets':'''pk_media_assets p 1 - -
uq_media_assets_logical_id u 2 - -
uq_media_assets_type_storage_path u 3,7 - -
fk_media_assets_media_assets_parent_logical_id f 13 schubert.media_assets(2) a/r/s
ck_media_assets_id_n12 c 1 - -
ck_media_assets_logical_id_bytes c 2 - -
ck_media_assets_media_type c 3 - -
ck_media_assets_title_bytes c 4 - -
ck_media_assets_category_bytes c 5 - -
ck_media_assets_section_bytes c 6 - -
ck_media_assets_storage_path_bytes c 7 - -
ck_media_assets_storage_path_safe c 7 - -
ck_media_assets_display_path_bytes c 8 - -
ck_media_assets_file_name_bytes c 9 - -
ck_media_assets_byte_size c 10 - -
ck_media_assets_sha256 c 11 - -
ck_media_assets_mime_type c 12 - -
ck_media_assets_pair c 3,14,15 - -
ck_media_assets_display_order c 16 - -''',
'entry_audio_links':'''pk_entry_audio_links p 1,2,4 - -
uq_entry_audio_links_entry_type_order u 1,4,5 - -
fk_entry_audio_links_script_entries_entry_game f 1,3 schubert.script_entries(1,2) a/c/s
fk_entry_audio_links_audio_files_audio_game f 2,3 schubert.audio_files(1,2) a/r/s
ck_entry_audio_links_link_type c 4 - -
ck_entry_audio_links_display_order c 5 - -'''}
columns=json.loads((i/'2901_master_column_independent_oracle.json').read_text())['tables'];positions={t:{row[0]:j+1 for j,row in enumerate(rows)} for t,rows in columns.items()};positions['games']={'id':1};matrix={};checks=[]
for table,block in raw.items():
 manual=[line.split() for line in block.splitlines()];assert all(len(row)==5 for row in manual);matrix[table]=sorted([[name,kind,keys,'true',ref,actions] for name,kind,keys,ref,actions in manual]);definition=s.split('CREATE TABLE schubert.'+table+' (',1)[1].split('\n);',1)[0];parsed=[]
 for name,body in re.findall(r'CONSTRAINT (\w+) (.*?)(?=,\n    CONSTRAINT|\Z)',definition,re.S):
  if body.startswith('PRIMARY KEY'):kind='p'
  elif body.startswith('UNIQUE'):kind='u'
  elif body.startswith('FOREIGN KEY'):kind='f'
  else:assert body.startswith('CHECK');kind='c'
  if kind=='c':
   clean=re.sub(r"'(?:[^']|'')*'",'',body);keys=','.join(map(str,sorted({num for col,num in positions[table].items() if re.search(r'\b'+re.escape(col)+r'\b',clean)})))
  else:keys=','.join(str(positions[table][col.strip()]) for col in re.search(r'\(([^)]+)\)',body).group(1).split(','))
  ref=actions='-'
  if kind=='f':
   target,names=re.search(r'REFERENCES schubert\.(\w+) \(([^)]+)\)',body).groups();ref='schubert.'+target+'('+','.join(str(positions[target][col.strip()]) for col in names.split(','))+')';actions='a/'+('c' if 'ON DELETE CASCADE' in body else 'r')+'/s';assert 'ON DELETE CASCADE' in body or 'ON DELETE RESTRICT' in body
  parsed.append([name,kind,keys,'true',ref,actions])
 assert sorted(parsed)==matrix[table],table;checks.append(dict(table=table,count=len(parsed),allManualRowsEqualIndependentDdlParse=True))
assert sum(map(len,matrix.values()))==75
prefix="SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='"
suffix="' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\""
queries=[prefix+table+suffix for table in matrix]
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceDdl=dict(path=str(ddl.relative_to(r)),sha256=hashlib.sha256(ddl.read_bytes()).hexdigest()),tables=matrix,queries=queries,ddlCrossChecks=checks,rows=75,fieldsPerRow=7,totalReads=525,productionMethodsCalled=0,actualDatabaseOperations=0,technicalSource='https://www.postgresql.org/docs/18/catalog-pg-constraint.html',notQualified=['CHECK_EXPRESSION','NOTNULL_CONSTRAINT_STATUS','CONNOINHERIT','INDEX_TRIGGER_ROLE','ACTUAL_DB'])
(i/'2928_constraint_independent_oracle.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,rows=75,counts=[len(v) for v in matrix.values()],manualMatchesDdl=True))
