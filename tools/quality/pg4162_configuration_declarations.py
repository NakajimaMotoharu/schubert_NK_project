"""BUG1341: keep all fixed declaration checks; runtime execution data has separate terminal proofs."""


def same_configurations(before,after,compare,parse):
    if type(before)is not dict or type(after)is not dict or len(before)!=10 or set(before)!=set(after):
        raise ValueError('all ten fixed declarations required')
    if not callable(compare)or not callable(parse):raise ValueError('qualified declaration comparators required')
    return all(compare(before[unit],after[unit],parse)is True for unit in before)
