## v0.3.0 (2023-10-13)

### Feat

- Implement custom check functionality in schema definitions

## v0.2.4 (2023-10-12)

### Refactor

- **tests**: Refactor tests to split test classes on success/failure and dataframe/series

## v0.2.3 (2023-10-12)

### Fix

- `check_types` did not work for many use cases. This commit greatly simplifies how it works: now uses recursive function to check inputs at arbitrary depth, both in input and output

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
