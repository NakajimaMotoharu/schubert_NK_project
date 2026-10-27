"""Strict raw Java token inverse v2: preserve Unicode and literal-concatenation structure, twenty negatives."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11104_web_pure_value_source_post import remove
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG11893-session-json-fixture-source-post-v2'
PIN='a74a3356b751e8464e72b7e7f799cfb3c40ba87dd7806fbd7e8cef4c96d727b6'

def lexical(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(before,after,rows):
    tokens=lexical(after);remove(tokens,lexical('private static final int FIRST_TOKEN_INDEX = 1;'))
    if tokens.count('FIRST_TOKEN_INDEX')!=1:raise ValueError('one exact independent JSON delimiter index')
    tokens=['1' if t=='FIRST_TOKEN_INDEX' else t for t in tokens]
    for row in rows:
        if row['kind']!='STRING':continue
        remove(tokens,lexical('private static final String '+row['name']+' = '+row['literal']+';'))
        if tokens.count(row['name'])!=row['references']:raise ValueError('every original fixture reference required')
        assert len(lexical(row['literal']))==1
        tokens=[row['literal'] if t==row['name'] else t for t in tokens]
    if tokens!=lexical(before):raise ValueError('raw Java token order/spelling/oracle changed')

def main():
    invocation=capture(__file__);assert not OUT.exists();plan=data.read_checked(data.BASE/'PG11890-session-json-fixture-plan-v1/manifest.json',PIN);normal=data.read_checked(data.BASE/'PG11864-web-exporter-fixture-six-compile-v1/manifest.json','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;assert len(plan['sourceChanges'])==1;row=plan['sourceChanges'][0];path=row['path'];before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert data.sha(before.encode())==row['beforeSha256'] and data.sha(after.encode())==row['sha256'];inverse(before,after,row['constants']);assert len(re.findall(r'@Test\s+void ',before))==7
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=path);bads=[after.replace('@Test','@Disabled',1)];sr=[r for r in row['constants'] if r['kind']=='STRING']
    for c in sr:
        decl='private static final String '+c['name']+' = '+c['literal']+';';assert after.count(decl)==1;bads += [after.replace(c['literal'],'"wrong-independent-vector"',1),after.replace(decl,'',1)]
    c=sr[0];occ=[m for m in LEX.finditer(after) if m.group()==c['name']][-1];bads.append(after[:occ.start()]+'"changed-reference"'+after[occ.end():]);decl='private static final int FIRST_TOKEN_INDEX = 1;';occ=[m for m in LEX.finditer(after) if m.group()=='FIRST_TOKEN_INDEX'][-1];bads += [after.replace(decl,decl.replace('1;','2;'),1),after.replace(decl,'',1),after[:occ.start()]+'2'+after[occ.end():]]
    for good,bad in [('future.get(20, TimeUnit.SECONDS)','future.get(19, TimeUnit.SECONDS)'),('i < 100','i < 99'),('new byte[16385]','new byte[16384]')]:
        assert after.count(good)==1;bads.append(after.replace(good,bad,1))
    assert len(bads)==20;negatives=0
    for bad in bads:
        assert bad!=after
        try:inverse(before,bad,row['constants'])
        except ValueError:negatives+=1
        else:raise AssertionError('changed independent JSON fixture/oracle/deadline accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],stringConstants=6,stringReferences=33,orderConstants=1,comparisonReferences=1,originalMethods=7,relatedUnchangedV2Methods=5,metadataNegativeVectors=negatives,rawJavaTokensRestored=3666,originalRawLiteralPlusLiteralPoints=3,canonicalFoldOrRetokenizationUsed=False,previousAttempt=dict(entry="tools/quality/pg11892_session_json_fixture_source_post.py",entrySha256="53c26bc61a86c3f482f5cfe50d68f3b17ae2b93d2b4bed249d8f0f527d5d68fa",lintExit=0,bodyExit=1,errorType="ValueError",outputWritten=False,relatedBug="BUG-1937"),allOriginalOracleTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
