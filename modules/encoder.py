# -*- coding: utf-8 -*-
import importlib
from json.encoder import (_make_iterencode, JSONEncoder,
                          encode_basestring_ascii, INFINITY,
                          encode_basestring)

discord = importlib.import_module('discord')
fortnitepy = importlib.import_module('fortnitepy')


class MyJSONEncoder(JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text


        _iterencode = _make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, _one_shot, isinstance=self.isinstance)
        return _iterencode(o, 0)

    def isinstance(self, obj, cls):
        if issubclass(getattr(obj, '_actual_enum_cls_', obj.__class__), discord.Enum):
            return False
        return isinstance(obj, cls)

    def default(self, obj):
        if isinstance(obj, fortnitepy.Enum):
            if isinstance(obj, fortnitepy.Platform):
                return obj.value.upper()
            return obj.name.upper()
        elif issubclass(getattr(obj, '_actual_enum_cls_', obj.__class__), discord.Enum):
            return obj.name.lower()
        elif isinstance(type(obj), type):
            return obj.__name__
        else:
            return None
