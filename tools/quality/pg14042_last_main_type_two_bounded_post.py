"""Independent XML and exact no-escape-prefix coordinate proof for two static references only."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg14040_last_main_type_two_bounded_references as selected

OUT=data.BASE/'PG14042-last-main-type-two-bounded-post-v1'
PIN='e8c5e0c68bec62316a450966069f70e141ebf9d6a2fbaaddf36afd2aa71cd6c7'
def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def main():
    invocation=capture(__file__);assert not OUT.exists()
    raw=data.read_checked(selected.OUT/'manifest.json',PIN);verify(raw['invocation'])
    assert raw['source']==selected.SOURCE and raw['actualExit']==raw['productTestsExecuted']==0 and raw['rawRetained']==2
    measured=data.read_checked(data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    assert measured['actualExit']==0 and measured['analysisComplete'] and not measured['processingErrors']
    xml=(data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();assert data.sha(xml)==measured['reports']['pmd']['sha256']
    actual=data.read_checked(selected.OUT/'review.json',raw['reviewSha256'])['rows']
    catalog=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==2 and {r['id'] for r in actual}==selected.IDS
    for row in actual:
        pin,owner,identities=selected.TARGETS[row['path']]
        old,=[r for r in catalog if r['id']==row['id']];text=(data.ROOT/row['path']).read_text()
        assert row['id'] in identities and data.sha(text.encode())==pin==row['sourceSha256']==old['inputSha256']
        assert row['originalRowSha256']==old['rowSha256'] and row['attributes']==old['attributes'] and row['rule']==selected.RULE
        file,=[f for f in ET.fromstring(xml) if f.tag.rpartition('}')[2]=='file' and f.get('name').endswith('/'+row['path'])]
        matches=[v for v in file if v.attrib==old['attributes']];assert len(matches)==row['rawDiagnosticMultiplicity']==1
        assert row['occurrenceOrdinal']==0 and type(row['occurrenceOrdinal']) is int
        attrs=matches[0].attrib;lines=text.splitlines(keepends=True)
        assert attrs['beginline']==attrs['endline']
        line=lines[int(attrs['beginline'])-1];a=int(attrs['begincolumn'])-1;b=int(attrs['endcolumn'])-1
        assert line[:b].isascii() and chr(9) not in line[:b] and chr(92)+'u' not in line
        expected_type='PSQLException' if row['id']=='PMD-00048' else 'StorageIoException'
        assert line[a:b]==row['typeToken']==expected_type
        start=sum(map(len,lines[:int(attrs['beginline'])-1]))+a;end=start+len(expected_type)
        assert (row['spanStart'],row['spanEndExclusive'],row['spanSha256'])==(start,end,data.sha(expected_type.encode()))
        assert text[start:end]==expected_type
        if row['id']=='PMD-00048':
            prefix=''.join(lines[:417]);assert len(prefix.splitlines())==417 and text.startswith(prefix)
            assert chr(92)+'u' not in prefix and chr(92)+'u' in text[len(prefix):]
            assert data.sha(prefix.encode())=='382bb161498bbd3d20250df0029f0241f5980ab866aba1a345334a19faedea52'
            expected_scope=dict(mode='ORIGINAL_NO_ESCAPE_PREFIX_THROUGH_SELECTED_LINE',prefixLines=417,prefixSha256=data.sha(prefix.encode()),suffixUnicodeEscapesNotTranslated=True,wholeJavaUnicodeTranslationValidated=False,spanProofIsPrefixOnly=True)
            anchor=text.index('catch (SQLException failure)',text.index('  private QuestionSubmitResponseData insertQuestion('))
        else:
            expected_scope=dict(mode='ORIGINAL_ORDINARY_LF_FULL_SOURCE',wholeJavaUnicodeTranslationValidated=False,spanProofIsPrefixOnly=False)
            assert chr(92)+'u' not in text
            anchor=text.index('catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure)',text.index('  private BundleSnapshot verifyAt('))
        assert wire(row['coordinateScope'])==wire(expected_scope) and row['catchAnchor']==anchor<start
        assert row['reason']==selected.reason(row['path'],attrs['method']) and row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['rawRetained'] is row['currentWholeJoinPending'] is True and row['sourceChanged'] is row['nativeRuntimeProven'] is False
        assert type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0
    expected=wire(actual)
    def assess(v):
        if wire(v)!=expected:raise ValueError('exact typed bounded source reference required')
    labels=[]
    for key,value in [('source','0'*40),('sourceSha256','0'*64),('typeToken','Other'),('spanStart',0),('spanEndExclusive',0),('spanSha256','0'*64),('catchAnchor',-1),('occurrenceOrdinal',1),('rawDiagnosticMultiplicity',2),('rawRetained',False),('rawRetained',0),('sourceChanged',True),('nativeRuntimeProven',True),('productTestsExecuted',False)]:
        bad=copy.deepcopy(actual);bad[0][key]=value
        try:assess(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered source binding accepted')
    prefix_labels=[]
    for key,value in [('prefixLines',418),('prefixSha256','0'*64),('spanProofIsPrefixOnly',False),('wholeJavaUnicodeTranslationValidated',True),('suffixUnicodeEscapesNotTranslated',False),('prefixLines',True)]:
        bad=copy.deepcopy(actual);bad[0]['coordinateScope'][key]=value
        try:assess(bad)
        except ValueError:prefix_labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('whole Unicode qualification invented')
    source_rejected=0
    for path in selected.TARGETS:
        text=(data.ROOT/path).read_text();selected.source_guards(path,text)
        for phrase in selected.GUARDS[path.rpartition('/')[2]]:
            assert phrase in text
            try:selected.source_guards(path,text.replace(phrase,'REMOVED_BOUND_CONTRACT'))
            except (AssertionError,ValueError):source_rejected+=1
            else:raise AssertionError('missing typed/retry/cleanup source guard accepted')
    assert len(labels)==14 and len(prefix_labels)==6 and source_rejected==14
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,reviewManifestSha256=PIN,reviewSha256=raw['reviewSha256'],sourceContexts=2,uniqueOperandSpans=2,uniqueCatchClauses=2,rawRetained=2,metadataNegativeVectors=len(labels),labels=labels,prefixQualificationNegativeVectors=len(prefix_labels),prefixLabels=prefix_labels,sourceGuardNegativeVectors=source_rejected,wholeJavaUnicodeTranslationValidated=False,selectedQuestionSpanValidatedByUnmodifiedToolOnOriginalPrefix=True,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
