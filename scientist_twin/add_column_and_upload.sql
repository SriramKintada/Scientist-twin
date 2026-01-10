-- Step 1: Add image_url column to scientists table
ALTER TABLE scientists ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Verify column was added
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'scientists' AND column_name = 'image_url';
