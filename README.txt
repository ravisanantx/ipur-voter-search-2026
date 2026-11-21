IPUR VOTER SEARCH 2026 — deployment package

LOCAL TEST (Windows / Mac / Linux)
1. Extract the ZIP into a folder. Install Python 3 if needed.
2. Open a terminal in the extracted folder.
3. Run: python app.py  (or python3 app.py)
4. Visit http://127.0.0.1:8000 in your browser. No extra libraries needed for local testing.
Windows: double-click start_windows.bat if Python is installed and on PATH.

PUBLIC DEPLOYMENT (not yet published)
Use an authorized Python web hosting provider that supports WSGI, HTTPS,
and a private application directory. Upload this package via the provider's
private deployment mechanism. Do not upload voters.json to a public repository
or static file hosting. Set install command: pip install -r requirements.txt
Set start command: gunicorn --bind 0.0.0.0:$PORT app:application
Follow your provider's PORT configuration. The app has /health for health checks.
Once deployed, the provider assigns a public HTTPS URL.

PRIVACY AND PUBLICATION
The app contains names, relationship names, house numbers, ages and other voter
information. Confirm you are authorized to republish these fields and that public
access complies with applicable electoral-roll and privacy rules before deployment.
If public disclosure is not permitted, use private authenticated hosting or remove
fields that cannot be shared. Use HTTPS and configure host-level rate limiting,
request logging privacy and abuse controls before opening the app to the public.
No automated data export endpoint or whole-list browsing is included. Searches
are server-side and paginated, but this is not a guarantee against scraping.
The local server only listens on localhost; it is not for production use.
The workbook's 4,378 rows and eight fields are preserved, including one blank
relationship-name entry. Search is case-insensitive. Prefix mode accepts 4 or more
characters; exact mode also supports shorter complete names. All results retain
source ordering. No login is implemented. This is not an official election site.
