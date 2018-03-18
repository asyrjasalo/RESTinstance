import sys

IS_PYTHON_2 = sys.version_info < (3,)

if IS_PYTHON_2:
  STRING_TYPES = (unicode ,str)
else:
  STRING_TYPES = (str)
