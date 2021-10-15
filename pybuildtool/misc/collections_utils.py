def data_merge(a, b):
    """
    Merges b into a and return merged result.

    see http://stackoverflow.com/a/15836901

    NOTE: tuples and arbitrary objects are not handled as it is totally
    ambiguous what should happen.
    """
    if b is None:
        return a
    key = None
    try:
        #if a is None or isinstance(a, str) or isinstance(a, unicode) or
        #isinstance(a, int) or isinstance(a, long) or isinstance(a, float):

        if a is None or isinstance(a, (str, int, float)):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                for c in b:
                    if not c in a:
                        a.append(c)
            elif not b in a:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise Exception('Cannot merge non-dict "%s" into dict "%s"' %\
                (b, a))

        else:
            raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise Exception(
                'TypeError "%s" in key "%s" when merging "%s" into "%s"' %\
                (e, key, b, a)) from e

    return a


def is_non_string_iterable(data):
    """Check if data was iterable but not a string."""
    # http://stackoverflow.com/a/17222092
    try:
        if isinstance(data, (unicode, str)):
            return False
    except NameError:
        pass
    if isinstance(data, bytes):
        return False
    try:
        iter(data)
    except TypeError:
        return False
    try:
        hasattr(None, data)
    except TypeError:
        return True
    return False


def make_list(items, nodict=False):
    """If items was not a list, create a list with it as a member."""
    if items is None:
        return []
    if not is_non_string_iterable(items):
        return [items]
    if nodict and isinstance(items, dict):
        return [items]

    return items
