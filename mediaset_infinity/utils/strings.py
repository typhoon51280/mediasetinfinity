from mediaset_infinity.utils import string_types

def string_join(ids, separator=","):
    if isinstance(ids, string_types):
        return ids
    elif hasattr(ids, '__iter__'):
        return separator.join(ids)
    else:
        return ""