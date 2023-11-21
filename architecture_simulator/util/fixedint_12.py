import fixedint

__all__ = []
cls = fixedint.FixedInt(12, signed=False, mutable=True)
cls.__module__ = __name__
__all__ += [cls.__name__]
globals()[cls.__name__] = cls
