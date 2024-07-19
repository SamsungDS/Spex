from re import DOTALL, compile

STRUCT_LABEL_REGEX = compile(
    r"^(?P<label>[\w\s.,-/&]*)\(?(?P<acronym>[\w\s\d]*)?\)?:?(?P<brief>.+)?$",  # noqa
    DOTALL,
)
VALUE_LABEL_REGEX = compile(
    r"^(?P<label>[\w\s/]*):?(?P<brief>.+)?$",  # noqa
    DOTALL,
)
ELLIPSIS_LABEL_REGEX = compile(r"^[\s]*\.\.\.[\s]*$")
