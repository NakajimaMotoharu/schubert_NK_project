"""Read two existing recheckConsistent catch diagnostics as Java text, never call the session."""
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11370_source_constructor_owner_audit import functions
from pg11569_four_repository_scope_facts import span

PATH='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java'
REASON=('recheckConsistent: the createStatement result is immediately protected by a typed '
    'SQLException/RuntimeException/Error catch that records failure=primary and rethrows the '
    'same identity; its following finally closes only the nonnull owned statement once and '
    'uses JdbcResourceFailures.replace(failure,secondary). The statement executes the literal '
    'SET TRANSACTION READ ONLY before the separate reference read. Unknown provider failures '
    'cannot become a consistent result; only the outer SQLException is mapped to fixed '
    'unavailable. This source point review neither executes that SQL nor proves current '
    'transaction rollback, DB lock, Root ownership or successful completion.')

def fact(row):
    assert row['id'] in ('PMD-03398','PMD-03399') and row['path']==PATH
    assert row['rule']=='AvoidCatchingGenericException' and row['attributes']['method']=='recheckConsistent'
    text=(data.ROOT/PATH).read_text();point,_,fragment=span(text,row['attributes'])
    assert fragment.strip() in ('RuntimeException','Error')
    ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    index=next(i for i,(_,offset) in enumerate(ts) if offset==point)
    ma,mb,name=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0])
    assert name=='recheckConsistent';values=[t for t,_ in ts[ma:mb+1]]
    expected=canonical('''var statement=connection.createStatement();
      @Nullable Throwable failure=null;
      try {present(statement).execute("SET TRANSACTION READ ONLY");}
      catch(SQLException|RuntimeException|Error primary){failure=primary;throw primary;}
      finally {if(statement!=null){try {statement.close();}
        catch(SQLException|RuntimeException|Error secondary){
          if(JdbcResourceFailures.replace(failure,secondary))throw secondary;}}}''')
    assert sum(values[i:i+len(expected)]==expected for i in range(len(values)))==1
    assert ''.join(values).endswith('catch(SQLExceptionfailure){throwunavailable();}}')
    return dict(kind='CURRENT_TYPED_PRIMARY_CAPTURE_AND_SAME_IDENTITY_RETHROW',method=name,
        ownership=dict(resource='statement',primary='failure',secondary='secondary',nonnullGuard=True,
            directCloseCount=1,closeTypes=['SQLException','RuntimeException','Error']),
        sourceSpanSha256=data.sha(fragment.encode()),methodTokenSha256=data.sha('\0'.join(values).encode()),
        reason=REASON,ptExecution=False,actualDatabaseOrRootStateProven=False)
