# Excel Serializer ![PyPI](https://img.shields.io/pypi/v/excel-serializer?label=excel-serializer)

![Example](./example.png)

Excel Serializer is a Python package that provides a set of functions and classes to serialize and deserialize Python objects to and from Excel files. The API is designed to be intuitive and familiar, closely mirroring the interface of the built-in `json` module. This makes it easy to configure and use for developers who are already accustomed to working with JSON serialization.

## Key Features

- **load**: Deserialize an Excel file to a Python object.
- **loadw**: Deserialize an openpyxl workbook to a Python object.
- **dump**: Serialize a Python object to an Excel file.
- **dumpw**: Serialize a Python object to an openpyxl workbook.

## Dependencies

- **openpyxl**: This module relies on the `openpyxl` library for reading from and writing to Excel files. Ensure that `openpyxl` is installed in your environment to use this module.

## Installation

You can install the package using pip:

```sh
pip install excel-serializer
```

## Builtin types

This module has four builtin types:
- `List`: A list of values.
- `Tuple`: A tuple of values.
- `Dict`: A dictionary of key-value pairs.
- `DictList`: A list of dictionaries all having the same keys.

You can easily add your own types by subclassing `ExcelEncoder` and `ExcelDecoder` classes. See how to do so in examples
below.

## Usage

### Encoding basic Python object hierarchies

```python
import excel_serializer as es

data = {'name': 'John', 'age': 30, 'city': 'New York'}
es.dump(data, 'data.xlsx')
```

### Decoding Excel files

```python
import excel_serializer as es

data = es.load('data.xlsx')
print(data)
# Output: {'name': 'John', 'age': 30, 'city': 'New York'}
```

### Using a custom encoder

You can either convert the custom object to a built-in type:
```python
import excel_serializer as es

class CustomEncoder(es.ExcelEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super()._default(obj)

data = {'numbers': {1, 2, 3}}
es.dump(data, 'data.xlsx', cls=CustomEncoder)
```

or implement a custom encoder to handle the serialization of the custom object:
```python
import excel_serializer as es

class CustomEncoder(es.ExcelEncoder):
    def write_set(self, sheet, type_cell, st):
        cols = ('Value',)
        type_cell.value = f'Set {type_cell.value}'
        sheet.append((type_cell,))
        sheet.append(cols)
        for i, e in enumerate(st):
            sheet.append((i + 1, self.encode(sheet, i + 3, 2, str(i + 1), e)))
        return 2 + len(st), 2, cols
    
    def write_custom_type(self, sheet, type_cell, obj):
        if isinstance(obj, set):
            return self.write_set(sheet, type_cell, obj)
        return super().write_custom_type(sheet, type_cell, obj)

data = {'numbers': {1, 2, 3}}
es.dump(data, 'data.xlsx', cls=CustomEncoder)
```

### Using a custom decoder

```python
import excel_serializer as es

class CustomDecoder(es.ExcelDecoder):
    def read_set(self, sheet_name, rows):
        headers = next(rows)
        if headers[0].value != 'Value':
            raise es.ExcelDecodeError(f'Invalid list headers. Expected "Value", found "{headers[0].value}"',
                                      self.workbook, sheet_name, 2, 1)
        return set(self.read_value(row[0]) for row in rows)
    
    def read_custom_type(self, sheet_type, sheet_name, rows):
        if sheet_type == 'Set':
            return self.read_set(sheet_name, rows)
        return super().read_custom_type(sheet_type, sheet_name, rows)

data = es.load('data.xlsx', cls=CustomDecoder)
print(data)
# Output: {'numbers': {1, 2, 3}}
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

Alexandre 'Tsu' Manuel - [tsu@sulvia.fr](mailto:tsu@sulvia.fr)

## Links

- [Homepage](https://github.com/alexandre-tsu-manuel/excel-serializer)
