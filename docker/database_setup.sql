CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};

USE ${MYSQL_DATABASE};

CREATE TABLE IF NOT EXISTS word_counts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(50) UNIQUE,
    count INT DEFAULT 0,
    last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- The script will replace these placeholders at runtime
-- Note: The actual values will come from the CURSE_WORDS environment variable
INSERT INTO word_counts (word) 
VALUES ('${CURSE_WORD_1}'), ('${CURSE_WORD_2}'), ('${CURSE_WORD_3}')
ON DUPLICATE KEY UPDATE count = count;