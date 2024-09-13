INSERT INTO users (username, email, hashed_password, role)
SELECT 'admin', 'admin@admin.com', '$2b$12$7rcxxEJrl5IPHZH3PuJj8.UDHRL1j.ml4h2.0LaD7uzyaIQMRwXNO', 'ADMIN'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'admin' OR email = 'admin@admin.com'
);
