import string
import _string


class EvalFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        try:
            value = super().get_value(key, args, kwargs)
        except KeyError:
            value = eval(key, globals(), kwargs)
        return value

    def get_field(self, field_name, args, kwargs):
        return self.get_value(field_name, args, kwargs), field_name
