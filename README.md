# My test project (by Meta)

## How to install and run:
1. Create postgres tables via [pgAdmin](https://www.pgadmin.org/):
    1. **raw_data_storage** for raw json containing entire Airtable data
    2. **main_data_storage** for storing actual data from Airtable
2. Pull files from this repo, install necessary packages using requirements.txt
3. Launch your virtual environment
4. Command for cli_script.py:
`python cli_script.py [AIRTABLE_BASE_ID] [AIRTABLE_API_KEY] [AIRTABLE_TABLE_NAME] [POSTGRES_PASSWORD]`
5. After launching cli_script **main_data_storage** table gets fulfilled with Airtable values. You may now run the command:
`python app.py`
6. Open index.html page directly from folder or launch a live server

**Warning** Above tablenames are mandatory to use because they are hardcoded into scripts

## Things are yet to fix:
* Make a option to enter user's tablenames instead of hardcoded ones;
* Change methods rendering in frontend app from a stringified list to an actual list to draw its items correctly. 
