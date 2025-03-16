#!/bin/bash

# Load environment variables
source config.env

# Get curse words from environment and split them
IFS=',' read -ra CURSE_WORDS_ARRAY <<< "$CURSE_WORDS"

# Create a copy of the database setup file
cp database_setup.sql database_setup_temp.sql

# Replace database variables
sed -i "s/\${MYSQL_DATABASE}/$MARIADB_DATABASE/g" database_setup_temp.sql

# Replace curse word placeholders
if [ ${#CURSE_WORDS_ARRAY[@]} -ge 1 ]; then
  sed -i "s/\${CURSE_WORD_1}/${CURSE_WORDS_ARRAY[0]}/g" database_setup_temp.sql
else
  sed -i "s/\${CURSE_WORD_1}/curse1/g" database_setup_temp.sql
fi

if [ ${#CURSE_WORDS_ARRAY[@]} -ge 2 ]; then
  sed -i "s/\${CURSE_WORD_2}/${CURSE_WORDS_ARRAY[1]}/g" database_setup_temp.sql
else
  sed -i "s/\${CURSE_WORD_2}/curse2/g" database_setup_temp.sql
fi

if [ ${#CURSE_WORDS_ARRAY[@]} -ge 3 ]; then
  sed -i "s/\${CURSE_WORD_3}/${CURSE_WORDS_ARRAY[2]}/g" database_setup_temp.sql
else
  sed -i "s/\${CURSE_WORD_3}/curse3/g" database_setup_temp.sql
fi

# Run the SQL script
echo "Running database setup with credentials from config.env..."
mariadb -h "$MARIADB_HOST" -u "$MARIADB_USER" -p"$MARIADB_PASSWORD" < database_setup_temp.sql

# Clean up
rm database_setup_temp.sql

echo "Database setup complete!"