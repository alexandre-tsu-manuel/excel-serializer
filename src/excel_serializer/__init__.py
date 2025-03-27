"""
Excel Serializer
================

Excel Serializer is a Python package that provides a set of functions and classes to serialize and deserialize Python
objects to and from Excel files. The API is designed to be intuitive and familiar, closely mirroring the interface of
the built-in `json` module. This makes it easy to configure and use for developers who are already accustomed to working
with JSON serialization.

Key Features:
-------------

- **load**: Deserialize an Excel file to a Python object.
- **loadw**: Deserialize an openpyxl workbook to a Python object.
- **dump**: Serialize a Python object to an Excel file.
- **dumpw**: Serialize a Python object to an openpyxl workbook.

Dependencies:
-------------

- **openpyxl**: This module relies on the `openpyxl` library for reading from and writing to Excel files. Ensure that
`openpyxl` is installed in your environment to use this module.

Builtin Types:
--------------
This module has four builtin types:
- `List`: A list of values.
- `Tuple`: A tuple of values.
- `Dict`: A dictionary of key-value pairs.
- `DictList`: A list of dictionaries all having the same keys.

You can easily add your own types by subclassing `ExcelEncoder` and `ExcelDecoder` classes. See how to do so in examples
below.


Examples:
---------

Encoding basic Python object hierarchies::

    >>> import excel_serializer as es
    >>> data = {'name': 'John', 'age': 30, 'city': 'New York'}
    >>> es.dump(data, 'data.xlsx')

Decoding Excel files::

    >>> import excel_serializer as es
    >>> data = es.load('data.xlsx')
    >>> print(data)
    {'name': 'John', 'age': 30, 'city': 'New York'}

Using a custom encoder:

You can either convert the custom object to a built-in type::

    >>> import excel_serializer as es
    >>> class CustomEncoder(es.ExcelEncoder):
    ...     def default(self, obj):
    ...         if isinstance(obj, set):
    ...             return list(obj)
    ...         return super()._default(obj)
    ...
    >>> data = {'numbers': {1, 2, 3}}
    >>> es.dump(data, 'data.xlsx', cls=CustomEncoder)

or implement a custom encoder to handle the serialization of the custom object::
    >>> import excel_serializer as es
    >>> class CustomEncoder(es.ExcelEncoder):
    ...     def write_set(self, sheet, type_cell, st):
    ...         cols = ('Value',)
    ...         type_cell.value = f'Set {type_cell.value}'
    ...         sheet.append((type_cell,))
    ...         sheet.append(cols)
    ...         for i, e in enumerate(st):
    ...             sheet.append((i + 1, self.encode(sheet, i + 3, 2, str(i + 1), e)))
    ...         return 2 + len(st), 2, cols
    ...     def write_custom_type(self, sheet, type_cell, obj):
    ...         if isinstance(obj, set):
    ...             return self.write_set(sheet, type_cell, obj)
    ...         return super().write_custom_type(sheet, type_cell, obj)
    ...
    >>> data = {'numbers': {1, 2, 3}}
    >>> es.dump(data, 'data.xlsx', cls=CustomEncoder)

Using a custom decoder::
    >>> import excel_serializer as es
    >>> class CustomDecoder(es.ExcelDecoder):
    ...     def read_set(self, sheet_name, rows):
    ...         headers = next(rows)
    ...         if len(headers) != 2:
    ...             raise ExcelDecodeError(
    ...                 f'Invalid list headers. Expected 2, found {len(headers)}', self.workbook, sheet_name, 2,
    ...                  len(headers) + 1
    ...             )
    ...         if headers[0].value != 'Value':
    ...             raise es.ExcelDecodeError(f'Invalid list headers. Expected "Value", found "{headers[0].value}"',
    ...                                       self.workbook, sheet_name, 2, 1)
    ...         return set(self.read_value(row[0]) for row in rows)
    ...     def read_custom_type(self, sheet_type, sheet_name, rows):
    ...         if sheet_type == 'Set':
    ...             return self.read_set(sheet_name, rows)
    ...         return super().read_custom_type(sheet_type, sheet_name, rows)
    ...
    >>> data = es.load('data.xlsx', cls=CustomDecoder)
    >>> print(data)
    {'numbers': {1, 2, 3}}
"""

__version__ = "1.1.0"
__all__ = [
    "dump",
    "dumpw",
    "load",
    "loadw",
    "ExcelDecoder",
    "ExcelDecodeError",
    "ExcelEncoder",
]

__author__ = "Alexandre Manuel <tsu@sulvia.fr>"

from typing import IO, Callable, Optional, Type, Union

import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_workbook

from .decoder import ExcelDecodeError, ExcelDecoder
from .defaults import LINK_FONT, ROOT_SHEET_NAME, SEPARATOR, TABLE_STYLE_INFO
from .encoder import ExcelEncoder


def load(
    fp: Union[str, IO],
    must_exist: bool = True,
    cls: Optional[Type] = None,
    root_sheet_name: str = ROOT_SHEET_NAME,
) -> Optional[object]:
    """
    Load an Excel file and return the decoded object.

    :param fp: File path to the Excel file, or file-like object, open in binary-read mode.
    :param must_exist: If True, raises FileNotFoundError if the file does not exist.
    :param cls: To use a custom ``ExcelDecoder`` subclass (e.g. one that overrides the ``.read_custom_type()`` method to
    decode additional types to a Python object); otherwise ``ExcelDecoder`` is used.
    :param root_sheet_name: Name of the root sheet.
    :return: Decoded object.
    """
    try:
        # Hyperlinks are not supported in read-only mode
        workbook = openpyxl.load_workbook(fp, read_only=False)
    except FileNotFoundError:
        if must_exist:
            raise
        return None
    return loadw(workbook, cls=cls, root_sheet_name=root_sheet_name)


def loadw(
    workbook: Workbook,
    cls: Optional[Type] = None,
    root_sheet_name: str = ROOT_SHEET_NAME,
) -> object:
    """
    Reads an Excel workbook and return the decoded object.

    :param workbook: an openpyxl workbook object
    :param cls: To use a custom ``ExcelDecoder`` subclass (e.g. one that overrides the ``.read_custom_type()`` method to
    decode additional types to a Python object); otherwise ``ExcelDecoder`` is used.
    :param root_sheet_name: Name of the root sheet.
    :return: Decoded object.
    """
    if cls is None:
        cls = ExcelDecoder
    decoder = cls(workbook, root_sheet_name=root_sheet_name)
    return decoder.decode()


def dump(
    obj: object,
    fp: Union[str, IO],
    keep_workbook_open: bool = False,
    skipkeys: bool = False,
    check_circular: bool = True,
    cls: Optional[Type] = None,
    sort_keys: bool = False,
    default: Optional[Callable[[object], object]] = None,
    separator: str = SEPARATOR,
    root_sheet_name: str = ROOT_SHEET_NAME,
) -> Optional[Workbook]:
    """
    Serialize an object to an Excel file.

    :param obj: Object to serialize.
    :param fp: File path to the Excel file, or file-like object, open in binary-write mode.
    :param keep_workbook_open: If True, returns the still-writable/still-savable workbook object instead of closing it.
    :param skipkeys: If True, dict keys that are not of an openpyxl-compatible type will be skipped.
    :param check_circular: If True, circular references will raise an exception.
    :param cls: To use a custom ``ExcelEncoder`` subclass (e.g. one that overrides the ``.default()`` method to
    convert additional types to a known-type); otherwise ``ExcelEncoder`` is used.
    :param sort_keys: If True, dict keys will be sorted.
    :param default: a function that should return a serializable version of obj or raise TypeError. The default simply
    raises TypeError.
    :param separator: Separator used in the sheet names.
    :param root_sheet_name: Name of the root sheet.
    :return: If keep_workbook_open is True, returns the workbook object.
    """
    workbook = openpyxl.Workbook(write_only=not keep_workbook_open)
    # A default sheet is created when not in write-only mode, so we remove it if it exists
    _ = workbook.active and workbook.remove(workbook.active)
    dumpw(
        obj,
        workbook,
        skipkeys=skipkeys,
        check_circular=check_circular,
        cls=cls,
        sort_keys=sort_keys,
        default=default,
        separator=separator,
        root_sheet_name=root_sheet_name,
    )
    save_workbook(workbook, fp)
    if keep_workbook_open:
        return workbook
    else:
        workbook.close()


def dumpw(
    obj: object,
    workbook: Workbook,
    skipkeys: bool = False,
    check_circular: bool = True,
    cls: Optional[Type] = None,
    sort_keys: bool = False,
    default: Optional[Callable[[object], object]] = None,
    separator: str = SEPARATOR,
    root_sheet_name: str = ROOT_SHEET_NAME,
) -> None:
    """
    Serialize an object to an openpyxl workbook.

    :param obj: Object to serialize.
    :param workbook: an openpyxl workbook object.
    :param skipkeys: If True, dict keys that are not of an openpyxl-compatible type will be skipped.
    :param check_circular: If True, circular references will raise an exception.
    :param cls: To use a custom ``ExcelEncoder`` subclass (e.g. one that overrides the ``.default()`` method to
    convert additional types to a known-type); otherwise ``ExcelEncoder`` is used.
    :param sort_keys: If True, dict keys will be sorted.
    :param default: a function that should return a serializable version of obj or raise TypeError. The default simply
    raises TypeError.
    :param separator: Separator used in the sheet names.
    :param root_sheet_name: Name of the root sheet.
    :return: None
    """
    if cls is None:
        cls = ExcelEncoder
    encoder = cls(
        workbook,
        skipkeys=skipkeys,
        check_circular=check_circular,
        sort_keys=sort_keys,
        default=default,
        separator=separator,
        root_sheet_name=root_sheet_name,
        link_font=LINK_FONT,
        table_style_info=TABLE_STYLE_INFO,
    )
    if encoder.encode(None, None, None, None, obj) is not None:
        raise TypeError(
            f"Cannot serialize root object. It needs to be a dict, list or tuple, not {type(obj)}"
        )
