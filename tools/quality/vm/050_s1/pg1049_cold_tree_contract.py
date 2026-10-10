"""SSC245 fixed two-generation recovery order. No concrete VM authority here.

The caller retains authenticated observer Ref/FD scope on any exception. Each
reservation must be durable/exclusive. No retry, fallback or inferred old close.
"""


def once_tree(parent, child, tree, orphan, reserve, open_pidfd, send, wait, close):
    if (type(parent) is not tuple or type(child) is not tuple or len(parent) != 2
            or len(child) != 2 or any(type(x) is not int or x <= 1 for x in (*parent, *child))
            or parent[0] == child[0]):
        raise ValueError('fixed tree generations refused')
    if not all(callable(f) for f in (tree, orphan, reserve, open_pidfd, send, wait, close)):
        raise ValueError('fixed tree callbacks refused')
    descriptors = []
    primary = None
    try:
        before = tree()
        if type(before) is not dict:
            raise ValueError('whole tree proof unavailable')
        for actor in (parent, child):
            if tree() != before:
                raise ValueError('tree changed before binding')
            descriptors.append(open_pidfd(actor[0]))
        if tree() != before:
            raise ValueError('tree changed after binding')
        reserve(parent, before)
        if tree() != before:
            raise ValueError('tree changed after parent reservation')
        send(descriptors[0])
        if wait(descriptors[0]) is not True:
            raise ValueError('parent terminal not confirmed')
        after_parent = orphan()
        if type(after_parent) is not dict:
            raise ValueError('orphan proof unavailable')
        if orphan() != after_parent:
            raise ValueError('orphan or server changed')
        # A child may already terminate with its supervisor. The caller must
        # prove child pidfd/PID/bus disappearance and all postconditions; never
        # send a signal to an already terminal generation or infer normal close.
        if after_parent.get('childGone') is True:
            return
        reserve(child, after_parent)
        if orphan() != after_parent:
            raise ValueError('orphan changed after reservation')
        send(descriptors[1])
        if wait(descriptors[1]) is not True:
            raise ValueError('child terminal not confirmed')
    except BaseException as failure:
        primary = failure
        raise
    finally:
        failures = []
        for descriptor in reversed(descriptors):
            try:
                close(descriptor)
            except BaseException as failure:
                failures.append(failure)
        if failures:
            if primary is not None:
                primary.add_note('pidfd close unknown; observer ownership must remain retained')
            else:
                raise failures[0]
