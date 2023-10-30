## v0.9.1 (2023-10-30)

### Fix

- try with two workflows

## v0.9.0 (2023-10-30)

### Feat

- Add support for datetime and category index types

### Fix

- try again
- try with pat
- retry workflow fix
- Fix broken workflow. Remove custom token
- merge

## v0.8.1 (2023-10-30)

### Fix

- remove local refs

## v0.8.0 (2023-10-26)

### Feat

- Support check_index_name param passed to index field

## v0.7.1 (2023-10-23)

### Fix

- add df=df.copy() in validate method, to fix override bug
- Refactor check_schemas decorator to use more specific type hints

## v0.7.0 (2023-10-23)

### Feat

- support defining `unique` in Field

## v0.6.1 (2023-10-20)

### Refactor

- Create FieldInfo type. Some ad-hoc refactoring too

## v0.6.0 (2023-10-20)

### Feat

- Index series are now also coerced, whether they are df.index or level in multiindex

### Fix

- resolve merge with main

## v0.5.1 (2023-10-20)

### Fix

- recursive filtering did not play nice with *args and **kwargs. fix that

## v0.5.0 (2023-10-20)

### Feat

- Support recursive filtering to function i/o

## v0.4.0 (2023-10-20)

### Feat

- 1) Add support for `Optional` columns in schema definitions. Add tests too. 2) Add custom errors when columns are missing and when schema definition is wrong. 3) Non-small refactor in model.py. Move colunm checks to top and simplify some things (more can be done though)

### Fix

- Remove `regex` optional argument from `check` custom check decorator

### Refactor

- Decreate nesting in _select_matching_names
- Refactor `_validate_multiindex` so it works like `_validate_columns` (also refactored a bit), and overall simplifies the code

## v0.3.3 (2023-10-17)

### Fix

- Do not coerce order when when Config.filter = True
- remove typo
- Cast df.index as series

### Refactor

- StrictConfig not reused, move into schema

## v0.3.2 (2023-10-13)

### Fix

- Rename pandabear.typing -> pandebear.typehints

## v0.3.1 (2023-10-13)

### Refactor

- Clean up imports

## v0.3.0 (2023-10-13)

### Feat

- Implement custom check functionality in schema definitions

## v0.2.4 (2023-10-12)

### Refactor

- **tests**: Refactor tests to split test classes on success/failure and dataframe/series

## v0.2.3 (2023-10-12)

### Fix

- `check_schemas` did not work for many use cases. This commit greatly simplifies how it works: now uses recursive function to check inputs at arbitrary depth, both in input and output

### Refactor

- **BaseModel-and-children**: Move `_validate_series` to BaseModel parent class

## v0.2.2 (2023-10-12)

### Fix

- **fix-import**: import CHECK_NAME_FUNCTION_MAP from pandabear.column_checks, not pandabear.model_components

## v0.2.1 (2023-10-11)

### Fix

- isort
- **fix-output-validation**: added a recursive output validation check

## v0.2.0 (2023-10-11)

### Feat

- **add-support-for-Series-runtime-type-checking**: added Series and SeriesModel classes, as well as tests demonstarting their basic function

## v0.1.0 (2023-10-11)

### Feat

- first commit
