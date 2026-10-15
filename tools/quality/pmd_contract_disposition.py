"""Per-finding technical assessment, never a rule suppression or automatic quality acceptance."""


def classify_contract(row,context,contract):
    if context.get('sourceSha256',{}).get(row.get('path'))!=row.get('sourceSha256'):
        raise ValueError('exact current source-bound finding required')
    rule=row.get('rule');path=row.get('path');disposition=None;basis=None;evidence=[]
    if rule in {'DoNotUseThreads','UseProperClassLoader'}:
        module=path.split('/')[1]
        if context.get('vendorExplicitJ2ee',{}).get(rule)is True and context.get('approvedDirectJavaProcess')is True and context.get('externalJavaEEManaged')is False and context.get('noManagedDeploymentDescriptors')is True and context.get('moduleRoles',{}).get(module)in {'STANDALONE_JAVA_SERVICE','LIBRARY_ONLY_IN_STANDALONE_GRAPH'}:
            disposition='CONTEXT_NOT_APPLICABLE_J2EE_RULE';basis='Exact primary vendor premise is J2EE server-managed execution/classloading; approved SS311/342 specifies direct Java standalone services and only their shared libraries.';evidence=context.get('architectureEvidence',[])
    key=(rule,path)
    proof=contract.get(key)
    if proof is not None:
        if proof.get('sourceSha256')!=row['sourceSha256']or proof.get('wholeSource')!=context.get('source')or proof.get('independentXmlQualified')is not True or not proof.get('evidence'):
            raise ValueError('contract and actual independent current-source Test/XML evidence required')
        if int(row['coordinates']['beginline'])not in proof.get('exactFindingLines',[]):
            raise ValueError('explicit reviewed statement line required')
        disposition=proof['disposition'];basis=proof['basis'];evidence=proof['evidence']
    if disposition is None:return None
    return {'disposition':disposition,'basis':basis,'evidence':evidence,'qualityGatePass':False,'rawWarningRemoved':False,'mainChangeRequiredByThisAssessment':False,'scope':'TECHNICAL_APPLICABILITY_ONLY_NOT_WHOLE_QUALITY'}
