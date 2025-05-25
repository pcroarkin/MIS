-- Add last_login column if it doesn't exist
ALTER TABLE users ADD COLUMN last_login DATETIME DEFAULT NULL;

-- Add is_active column if it doesn't exist
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;

-- Update all existing users to be active
UPDATE users SET is_active = 1 WHERE is_active IS NULL;
