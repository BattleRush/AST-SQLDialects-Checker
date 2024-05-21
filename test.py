import ast
from ast import literal_eval as make_tuple

expected = "(1, 2)"
expected = make_tuple(expected)

print(expected)