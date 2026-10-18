"""Prior fixed names are only a whitelist; every current qualification and source is rechecked."""
import json
import subprocess
import pg5146_scope_classification as inventory

ORIGINAL_SHA='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344'
NATIVE_FIXED={'LinuxFileLock.java','LinuxSealedProof.java','LinuxStartupAdmission.java'}


def fixed_names(rows):
    seen=set();fixed=set()
    for row in rows:
        name=row['path'].rpartition('/')[2]
        if name in seen:raise ValueError('original inventory basenames must remain unambiguous')
        seen.add(name)
        classes={site['classification'] for site in row['sites']}
        if not classes or not classes<={'FIXED_LIMITED','NON_APPLICABLE_BORROWED','UNKNOWN'}:
            raise ValueError('all original sites require explicit known classification')
        if 'FIXED_LIMITED' in classes:
            if classes!={'FIXED_LIMITED'}:raise ValueError('partial unknown file cannot inherit whole-file whitelist')
            fixed.add(name)
    return fixed


def continue_current(*,root,sha,previous_ref,previous_sha,previous_source,source,
                     qualified_ref,tests,suites,new_files,expected_counts):
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if sha(original)!=ORIGINAL_SHA:raise ValueError('immutable original237 inventory')
    previous_path=root/('evidence/01_PT/'+previous_ref)
    if sha(previous_path)!=previous_sha:raise ValueError('exact previous classification input')
    old=json.loads(previous_path.read_bytes())
    if old['source']!=previous_source or old['formalAccepted'] is not False:
        raise ValueError('previous limited classification, never formal acceptance reuse')
    qualified_path=root/('evidence/01_PT/'+qualified_ref);proof=json.loads(qualified_path.read_bytes())
    if type(proof['actualExit']) is not int or proof['actualExit']!=0 or proof['productionCandidateSource']!=source:
        raise ValueError('new exact source qualification required')
    if proof['tests']!=tests or proof['suites']!=suites or proof['formalAccepted'] is not False:
        raise ValueError('complete current selected inventory required')
    fixed=fixed_names(old['files'])
    original_value=json.loads(original.read_bytes())
    names={row['path'].rpartition('/')[2] for row in original_value['files']}
    if not new_files<=names or new_files&fixed:raise ValueError('only explicitly new original candidates')
    extra=(fixed|new_files)-inventory.ROOT_FIXED-inventory.CALLER_FIXED-NATIVE_FIXED
    counts=inventory.classify(original_value['files'],
        lambda path:subprocess.check_output(['git','show',source+':'+path],cwd=root),
        native=True,evidence_ref=qualified_ref,extra_fixed=extra)
    if counts!=expected_counts or sum(counts.values())!=237:
        raise ValueError('all original237 current-source sites must partition exactly')
    original_value.update(source=source,originalSource=original_value['source'],originalInventorySha256=sha(original),
        previousClassificationSha256=sha(previous_path),qualificationSha256=sha(qualified_path),classificationCounts=counts,
        newSiteReview=old['newSiteReview'],extraNativeOwnerTransfer=old['extraNativeOwnerTransfer'],
        previousNamesWhitelistOnly=True,currentInventorySourceChecked=True,currentSelectedQualificationChecked=True,
        wholeSourceQualified=False,
        wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    return original_value,proof
