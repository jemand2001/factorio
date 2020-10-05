class _ShortInt(int):
    def __init__(self, *args, length, name, **kwargs):
        super().__init__()
        if self.bit_length() > length:
            raise BytesWarning(f'value `{self}` does not fit into a {name} ({length} bytes)')


class byte(_ShortInt):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, length=8, name='byte', **kwargs)


class short(_ShortInt):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, length=16, name='short', **kwargs)


class single(float):
    @classmethod
    def fromhex(cls, s: str) -> float:
        if len(s.strip('0x')) > 8:
            raise ValueError('not a single precision float')
        return super().fromhex(s)


double = float
boolean = bool
