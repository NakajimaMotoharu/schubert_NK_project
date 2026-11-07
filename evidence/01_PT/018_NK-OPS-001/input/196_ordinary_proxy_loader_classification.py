"""Individual Test Proxy-loader applicability: data only, no Product or class loading."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
R=Path(__file__).resolve().parents[4]
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22392-ordinary-proxy-loader93-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
BLOCKED={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
TYPES={'java.sql.Connection','java.sql.PreparedStatement','java.sql.ResultSet','javax.sql.DataSource','jakarta.jms.JMSContext','jakarta.jms.JMSProducer','jakarta.jms.Message','org.apache.activemq.artemis.api.core.client.ClientSession','jakarta.servlet.http.HttpServletRequest','jakarta.servlet.http.HttpServletResponse','jakarta.servlet.http.HttpSession'}
PROFILE=re.compile(r'Proxy\.newProxyInstance\(\s*((?:[\w$.]+\.class|type)\.getClassLoader\(\)),\s*new Class<\?>\[\]\s*\{\s*([\w$.]+)\s*\},')
def inspect(text,path,line):
    if not path.startswith('src/') or '/src/test/java/' not in path or BLOCKED.intersection(Path(path).parts):return None
    if not re.search(r'^import java\.lang\.reflect\.Proxy;$',text,re.M) or 'setContextClassLoader(' in text:return None
    calls=[x for x in PROFILE.finditer(text) if text.count('\n',0,x.start(1))+1==line]
    if len(calls)!=1:return None
    match=calls[0];loader,target=match.groups();imports=re.findall(r'^import ([\w.]+);$',text,re.M);receiver=loader.removesuffix('.getClassLoader()')
    if receiver=='type':
        if target!='type' or not re.search(r'Class<\w+>\s+type\b',text):return None
        kind='CLASS_PARAMETER_SAME_INTERFACE_ARRAY';qualified='Class<T> type'
    else:
        if not target.endswith('.class'):return None
        target_name=target.removesuffix('.class');root=target_name.split('.')[0];options=[x for x in imports if x.rsplit('.',1)[-1]==root]
        if len(options)!=1:return None
        qualified=options[0]+target_name[len(root):]
        if options[0] not in TYPES:return None
        owner=receiver.removesuffix('.class');outer=Path(path).stem
        if owner not in [target_name,'Fixture',outer]:return None
        if owner=='Fixture' and not re.search(r'\bclass\s+Fixture\b',text):return None
        if not re.search(r'\bclass\s+'+re.escape(outer)+r'\b',text):return None
        kind='INTERFACE_DEFINING_LOADER' if owner==target_name else 'OWN_TEST_DEFINING_LOADER'
    return dict(loaderExpression=loader,interfaceExpression=target,resolvedInterface=qualified,profile=kind,callPrefix=match.group(),callPrefixSha256=hashlib.sha256(match.group().encode()).hexdigest(),classification='NOT_APPLICABLE',reason='Standalone Test-owned java.lang.reflect.Proxy creation; the explicitly bound loader and interface array define this synthetic port. This source is outside Production Main/J2EE application and does not modify the thread context loader; the J2EE TCCL preference is inapplicable at this exact call only.')
def negatives():
    text='import java.lang.reflect.Proxy;\nimport java.sql.Connection;\nclass ExampleTest { void port(){ Proxy.newProxyInstance(Connection.class.getClassLoader(), new Class<?>[] {Connection.class}, handler); }}'
    path='src/example/src/test/java/p/ExampleTest.java';line=3;assert inspect(text,path,line)
    vectors=[(text.replace('Proxy.newProxyInstance','Other.create'),path,line),(text.replace('Connection.class.getClassLoader()','Unknown.class.getClassLoader()'),path,line),(text.replace('new Class<?>[] {Connection.class}','new Class<?>[] {Unknown.class}'),path,line),(text,path.replace('/test/','/main/'),line),(text,path,line+1),(text.replace('import java.sql.Connection;',''),path,line),(text+'\nsetContextClassLoader(x);',path,line)]
    assert all(inspect(*x) is None for x in vectors);return len(vectors)
def main():
    assert not OUT.exists();bp=BASE/'manifest.json';assert sha(bp)=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';m=load(bp);rows=load(BASE/'unclassified-sites.json');assert len(rows)==347 and m['unclassifiedSites']==347;selected=[x for x in rows if x['attributes']['rule']=='UseProperClassLoader'];assert len(selected)==93;result=[];read={}
    for row in selected:
        path=row['path'];assert not BLOCKED.intersection(Path(path).parts);p=R/path;assert sha(p)==row['sourceSha256']==m['begin']['inputHashes'][path];text=p.read_text();read[path]=sha(p);out=inspect(text,path,int(row['attributes']['beginline']));result.append(dict(original=row,assessment=out,status='CLASSIFIED_INDIVIDUALLY' if out else 'UNCLASSIFIED_PROFILE_NOT_PROVEN'))
    count=sum(x['assessment'] is not None for x in result);OUT.mkdir();(OUT/'site-classifications.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',originalManifest=dict(path=str(bp.relative_to(R)),sha256=sha(bp)),inputHashes=read,rawSites=347,targetSites=93,newIndividualClassifications=count,subsetUnclassifiedAfter=347-count,negativeMetadataVectors=negatives(),productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,suppressionAdded=False,ruleConfigurationChanged=False,sourceBytesUnchanged=True,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files={'site-classifications.json':sha(OUT/'site-classifications.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
    (OUT/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=count,remaining=347-count,negativeMetadataVectors=value['negativeMetadataVectors'],manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
