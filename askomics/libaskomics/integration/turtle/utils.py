from inspect import stack

def refine_class(name, bases, dct):
    """Allow to monkey patch a previously defined class.

    Say you have a class T defined in scope :
    >>> class T:
    ...     def __init__(self):
    ...         print('original init %r' % self.classattr)
    ...     classattr = 'a T class attribute'
    >>> idT = id(T)

    You can patch it by declaring a class with the same name and with refine_class as metaclass :
    >>> class T(metaclass=refine_class):
    ...     def __init__(self):
    ...         print('new init %r' % self.classattr)

    The class is modified in place:
    >>> idT == id(T)
    True
    >>> instance = T()
    new init 'a T class attribute'
    """
    cls = stack()[1][0].f_globals[name]
    for k, v in dct.items():
        setattr(cls, k, v)
    return cls

