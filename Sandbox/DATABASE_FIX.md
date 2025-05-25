# Database Fix Instructions

This guide will help you resolve the database error related to missing columns in the users table.

## Quick Fix

### For Windows Users:
1. Open a command prompt in your project directory
2. Double-click on `fix_database.bat`
   - Or run it from command prompt: `fix_database.bat`

### For Mac/Linux Users:
1. Open a terminal in your project directory
2. Make the script executable: `chmod +x fix_database.sh`
3. Run the script: `./fix_database.sh`

## Manual Fix (If automated fix doesn't work)

1. Stop your Flask application if it's running

2. Locate your database file:
   - Default location: `instance/app.db`
   - In your case: `/Users/pcro/MIS/instance/app.db`

3. Backup your database:
   ```bash
   cp instance/app.db instance/app.db.backup
   ```

4. Run the Python fix script directly:
   ```bash
   python fix_db.py
   ```

5. Restart your Flask application

## Verifying the Fix

1. After running the fix, try logging in to your application
2. The error "no such column: users.last_login" should be resolved
3. Check that you can:
   - Log in successfully
   - See your last login time in your profile
   - Your account status (active/inactive) is displayed correctly

## Troubleshooting

If you encounter issues:

1. Check file permissions:
   - Ensure you have write access to the `instance` directory
   - Ensure you have write access to the database file

2. Check if database is locked:
   - Make sure no other process is using the database
   - Stop any running Flask applications
   - Close any database management tools

3. Common errors:
   - "Permission denied": Run the script with appropriate permissions
   - "Database is locked": Stop all processes that might be using the database
   - "No such file or directory": Make sure you're in the correct directory

## Need Help?

If you continue to experience issues:

1. Check the error messages in your terminal/command prompt
2. Make sure your virtual environment is activated
3. Verify that all required packages are installed
4. Contact support with:
   - The exact error message
   - The contents of your instance directory
   - The steps you've tried so far

## Prevention

To prevent similar issues in the future:

1. Always use Flask-Migrate for database changes
2. Back up your database before updates
3. Test changes in development before applying to production
4. Keep your application and dependencies up to date

## Additional Notes

- This fix adds two new columns to your users table:
  - `last_login`: Tracks when users last logged in
  - `is_active`: Controls whether users can log in
- Existing users will have `is_active` set to true by default
- `last_login` will be updated automatically on each login
