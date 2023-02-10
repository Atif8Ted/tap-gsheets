# tap-gsheets
A meltano tap for ingest data from Google Sheets
## Meltano configuration:

```yaml
  - name: tap-gsheets
    namespace: tap_gsheets
    pip_url: git+https://github.com/Atif8Ted/tap-gsheets.git
    executable: tap-gsheets
    config:
      client_id: 
      refresh_token: 
      client_secret: 
      underscore_columns: True/False
      singular_table_name: True/False
      spreadsheets:
        - spreadsheet_id: <spreadsheet_id>
          sheets: [<Llist of sheets>]

```
## Configurations:
1. client_id: Client ID of the Google API
2. refresh_token: Refresh token of the Google API
3. client_secret: Client secret of the Google API
4. underscore_columns: If True, it will convert the column names to underscore separated
5. singular_table_name: If True, it will convert the sheet name to singular form
6. spreadsheets: List of spreadsheets to be ingested
7. spreadsheet_id: ID of the spreadsheet
8. sheets: it can be a list of sheets or a list of dictionaries with sheet name and final table name
   1. If it is a list of sheets, it will ingest all the sheets with the same name as the sheet 
    * ex: [sheet1,sheet2] will ingest the sheets as sheet1 and sheet2
   2. If it is a list of dictionaries, it will ingest the sheets with the name as the key and the value as the final table name
   * ex: [{'sheet1':'final_table1'},{'sheet2':'final_table2'}] will ingest the sheets as final_table1 and final_table2
