CREATE TABLE IF NOT EXISTS emails( message_id VARCHAR(255) PRIMARY KEY , email_subject TEXT , sender TEXT ,body TEXT , dt TIMESTAMP);
CREATE TABLE IF NOT EXISTS processed_emails(message_id VARCHAR(255) PRIMARY KEY REFERENCES emails(message_id) ON DELETE CASCADE,category VARCHAR(255) ,priority VARCHAR(255),intent VARCHAR(255) ,entities JSON);
