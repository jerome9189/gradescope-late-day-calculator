# gradescope-late-day-calculator
Script I used to track student late days when I was a TA for CSE 312 at UW

Setup
1. Make sure you have a spreadsheet in your google drive with Pset 1 late days in the format "email, late days used" (with a header row)
2. Copy the spreadsheet id (can be found in the url of the spreadsheet) and replace the SPREADHSHEET_ID variable in the python script.
3. Enable the Google Sheets API (https://developers.google.com/workspace/guides/enable-apis)
4. Get the credentials file from the Google Cloud Platform Console, place it in the top level of the repository, and name it "credentials.json" 
5. Run `pip install -r requirements.txt`
6. Download the relevant Pset grades files from Gradescope; these will contain the lateness of the submissions (some file names are hardcoded into the script).
7. Run the script as `./update_late_days.py <pset_num>`. If this is the first time running the script, you may have to login to the relevant Google account. 
8. If everything worked correctly, you should have a new sheet tab in your spreadsheet.
