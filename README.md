# keepass-to-env-vars

This action puts keepass entries into environment variables, 
entries whose title ends with the "_BASE64" postfix are exported once with their original name and value and once as
decoded string without the postfix if the decoded string only contains valid UTF-8 bytes, it also creates an env.json
file in the current working directory which contains all environment variables

## Inputs

## `keepass-file-path`

**Required** The path to the keepass file

## `keepass-master-password`

**Required** The password for the keepass file

## `keepass-group-filter`

**Not Required** The comma-separated list of keepass groups that should be used for this action,
concatenate nested groups with "/", the empty string as default selects all entries from the database

## Example usage

```yaml
uses: efficientIO/keepass-to-env-vars@v1
with:
  keepass-file-path: 'database.kdbx'
  keepass-master-password: 'secret'
  keepass-group-filter: 'cloud,app/dev'
```
