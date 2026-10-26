"""Independent source/diagnostic/occurrence identity checks, with ten metadata and two identity negatives."""
import copy
import pg11054_api_request_context as stage


def require_occurrences(rows,original,actual):
    for row in rows:
        node=next(n for path,n in actual if path==row['path'] and dict(n.attrib)==row['attributes'])
        if stage.original_match(row['path'],node,original,actual)['id'] != row['id']:
            raise ValueError('preserved same-signature occurrence identity required')


if __name__ == '__main__':
    stage.PRIMARY_SHA='88ede17e3d71b67ce4f761051ed20f07f4f11a67091a7af4038955da060ec668'
    primary=stage.data.read_checked(stage.OUT/'manifest.json',stage.PRIMARY_SHA)
    rows=stage.data.read_checked(stage.OUT/'contexts.json',primary['contextsSha256'])
    _,original,actual=stage.inputs()
    require_occurrences(rows,original,actual)
    assert stage.original_match(rows[0]['path'],next(n for p,n in actual if p==rows[0]['path'] and dict(n.attrib)==rows[0]['attributes']),list(reversed(original)),actual)['id']==rows[0]['id']
    bad=copy.deepcopy(rows)
    pair=[r for r in bad if r['id'] in ('PMD-00649','PMD-00651')]
    assert len(pair)==2
    pair[0]['id'],pair[1]['id']=pair[1]['id'],pair[0]['id']
    for changed in (bad,[dict(r,id='PMD-00649') if r['id']=='PMD-00651' else r for r in rows]):
        try:
            require_occurrences(changed,original,actual)
        except ValueError:
            pass
        else:
            raise AssertionError('swapped or duplicated identical-message occurrence accepted')
    stage.post()
