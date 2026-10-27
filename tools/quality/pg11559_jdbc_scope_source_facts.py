"""Lexical facts from existing two repository sources only; never initializes or calls JDBC/Root code."""
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11370_source_constructor_owner_audit import close,functions

def span(text,attributes):
    lines=text.splitlines(keepends=True)
    start=sum(map(len,lines[:int(attributes['beginline'])-1]))+int(attributes['begincolumn'])-1
    end=sum(map(len,lines[:int(attributes['endline'])-1]))+int(attributes['endcolumn'])
    if not 0<=start<end<=len(text):
        raise ValueError('exact existing source coordinates')
    return start,end,text[start:end]

def decode_finally(values):
    for resource in ('statement','rows'):
        for primary in ('statementFailure','rowFailure','rowsFailure'):
            for secondary in ('failure','secondary'):
                core='try{'+resource+'.close();}catch(SQLException|RuntimeException|Error '+secondary+'){if(JdbcResourceFailures.replace('+primary+','+secondary+'))throw '+secondary+';}'
                for braced in (False,True):
                    expected='if('+resource+'!=null)'+('{' if braced else '')+core+('}' if braced else '')
                    if values==canonical(expected):
                        return dict(resource=resource,primary=primary,secondary=secondary,nonnullGuard=True,directCloseCount=1,closeTypes=['SQLException','RuntimeException','Error'])
    raise ValueError('specific nonnull one-direct-close and approved typed precedence structure required')

def fact(row):
    path=row['path'];text=(data.ROOT/path).read_text();point,_,fragment=span(text,row['attributes'])
    ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    values=[t for t,_ in ts]
    scopes=functions(ts)
    index=next((i for i,(_,offset) in enumerate(ts) if offset==point),None)
    if index is None:
        raise ValueError('diagnostic must begin at an actual current source token')
    ma,mb,method=min((s for s in scopes if s[0]<=index<=s[1]),key=lambda item:item[1]-item[0])
    if method!=row['attributes']['method']:
        raise ValueError('actual enclosing source method')
    finally_scopes=[]
    catches=[]
    for i,value in enumerate(values[:-1]):
        if value=='finally' and values[i+1]=='{':
            end=close(ts,i+1,'{','}');finally_scopes.append((i,i+1,end))
        elif value=='catch' and values[i+1]=='(':
            params=close(ts,i+1,'(',')');assert values[params+1]=='{'
            end=close(ts,params+1,'{','}');catches.append((i,params,params+1,end))
    typed_io=False
    if row['rule']=='AvoidCatchingGenericException':
        ci,params,body_open,body_end=next(c for c in catches if c[0]<index<c[1])
        header=values[ci+2:params];variable=header[-1];types=[v for v in header[:-1] if v!='|']
        if types not in (['SQLException','RuntimeException','Error'],['SQLException','IOException','RuntimeException','Error']):
            raise ValueError('approved exact typed SQL/unknown catch, not catch-all normalization')
        if fragment.strip() not in ('RuntimeException','Error'):
            raise ValueError('one actual broad-type diagnostic token')
        body=values[body_open+1:body_end]
        if len(body)==7 and body[1:]==['=',variable,';','throw',variable,';']:
            primary=body[0]
            if values[body_end+1:body_end+3]!=['finally','{']:
                raise ValueError('same protection must have its own following finally')
            end=close(ts,body_end+2,'{','}')
            ownership=decode_finally(values[body_end+3:end])
            if ownership['primary']!=primary:
                raise ValueError('same primary binding is retained and ranked')
            typed_io='IOException' in types
            if typed_io and ('throwsIOException' not in ''.join(values[ma:values.index('{',ma)]) or method!='references'):
                raise ValueError('declared original-reference IOException must propagate unchanged')
            kind='CURRENT_TYPED_PRIMARY_CAPTURE_AND_SAME_IDENTITY_RETHROW'
            reason=f'{method}: typed {"/".join(types)} capture {variable} into {primary}, then rethrow the same primary before its own nonnull one-close finally. Provider Runtime/NPE/Error are not normalized; SS332 SSC063/199/200 approved precedence applies.'
        else:
            fi,opening,ending=min((f for f in finally_scopes if f[1]<ci<f[2]),key=lambda f:f[2]-f[1])
            ownership=decode_finally(values[opening+1:ending])
            expected=canonical('if(JdbcResourceFailures.replace('+ownership['primary']+','+variable+'))throw '+variable+';')
            if body!=expected or ownership['secondary']!=variable:
                raise ValueError('secondary catch must only apply approved precedence, not swallow/return success')
            kind='CURRENT_TYPED_CLOSE_SECONDARY_PRECEDENCE'
            reason=f'{method}: this {"/".join(types)} catch belongs to the one direct close of owned {ownership["resource"]}; {variable} escapes only when JdbcResourceFailures.replace({ownership["primary"]},{variable}) requires the SS332 SQL/unknown precedence. Borrowed transaction is not closed or repaired.'
    elif row['rule']=='DoNotThrowExceptionInFinally':
        fi,opening,ending=next(f for f in finally_scopes if f[0]==index)
        ownership=decode_finally(values[opening+1:ending])
        kind='CURRENT_FINALLY_REQUIRED_DIRECT_CLOSE_PRECEDENCE'
        reason=f'{method}: finally closes only nonnull owned {ownership["resource"]}, once; a close failure is thrown only by the approved SS332 decision for retained {ownership["primary"]}. Returning the successful body value before close or suppressing required unknown failures would violate SSC063/199.'
    else:
        raise ValueError('this new point review covers typed catch/finally only')
    if not re.fullmatch(r'[A-Za-z_]\w*',method):
        raise ValueError('ordinary current Java method')
    return dict(kind=kind,method=method,ownership=ownership,declaredIOExceptionPreserved=typed_io,sourceSpanSha256=data.sha(fragment.encode()),
        methodTokenSha256=data.sha('\0'.join(values[ma:mb+1]).encode()),reason=reason,ptExecution=False,actualDatabaseOrRootStateProven=False)
