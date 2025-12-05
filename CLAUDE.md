# ESG Reporting Project - Development Rules

## Snowflake Streamlit-in-Snowflake (SiS) Edge Cases

### Streamlit API Compatibility
Snowflake runs an older version of Streamlit. Avoid these unsupported features:

| Feature | Don't Use | Use Instead |
|---------|-----------|-------------|
| DataFrame hide_index | `st.dataframe(df, hide_index=True)` | `st.dataframe(df)` |
| Button type param | `st.button("X", type="primary")` | `st.button("X")` |
| Form submit type | `st.form_submit_button("X", type="primary")` | `st.form_submit_button("X")` |
| Download button type | `st.download_button(..., type="primary")` | `st.download_button(...)` |
| Rerun | `st.rerun()` | `st.experimental_rerun()` |
| Page config in pages | `st.set_page_config()` in page files | Only use in main file |
| Data editor | `st.data_editor()` | Use `st.dataframe()` + form inputs |

### SnowCLI Deployment Issues
- **Don't use `snow streamlit deploy`** for creating apps - it adds default packages that can cause "TypeError: bad argument type for built-in operation" errors
- **Use raw SQL to create Streamlit apps:**
  ```sql
  CREATE STREAMLIT DB.SCHEMA.APP_NAME
    ROOT_LOCATION = '@DB.SCHEMA.STAGE/app_folder'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = WAREHOUSE_NAME;
  ```
- **Use PUT to upload files:**
  ```sql
  PUT file:///path/to/streamlit_app.py @DB.SCHEMA.STAGE/app_folder/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE
  ```

### File Structure
- Keep `streamlit_app.py` at root level, not in subdirectories
- Avoid multi-page apps with `pages/` folder - use tabs within single file instead

### CI/CD with GitHub Actions
- Use key-pair authentication (SNOWFLAKE_JWT)
- Clean whitespace from secrets: `CLEAN_VAR=$(echo "${VAR}" | tr -d '[:space:]')`
- Use `printf` instead of heredoc for TOML config generation (avoids YAML parsing issues)
- Base64 encode private key for GitHub secrets
- Use absolute paths for key files: `/home/runner/.snowflake/rsa_key.p8`

### Snowpark Session
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
```

### Table Column Names
- Snowflake uses UPPERCASE column names by default
- Access as: `df["COLUMN_NAME"]` not `df["column_name"]`

### Handling NaN/Null Values
- Pandas returns NaN for null database values
- Use helper functions to safely convert:
```python
def safe_int(val, default=0):
    try:
        if val is None or (isinstance(val, float) and str(val) == 'nan'):
            return default
        return int(val)
    except:
        return default

def safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, float) and str(val) == 'nan'):
            return default
        return float(val)
    except:
        return default
```

## Deploy Commands

### Local Deploy (Manual)
```bash
# Upload file to stage
snow sql -q "PUT file:///path/to/streamlit_app.py @ESG_REPORTING.PROD.STREAMLIT/esg_app/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE"

# Create/recreate app (if needed)
snow sql -q "CREATE OR REPLACE STREAMLIT ESG_REPORTING.PROD.ESG_APP
  ROOT_LOCATION = '@ESG_REPORTING.PROD.STREAMLIT/esg_app'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = COMPUTE_WH"
```

### Get App URL
```bash
snow streamlit get-url ESG_REPORTING.PROD.ESG_APP
```

## Project URLs
- **App:** https://app.snowflake.com/ZLOFVHD/si80049/#/streamlit-apps/ESG_REPORTING.PROD.ESG_APP
- **GitHub:** https://github.com/benjaminfauchald/snowflake_esg
