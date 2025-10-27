-- ==========================================
-- 🌳 Tawi Tree Planting Project Database
-- ==========================================

-- 1️⃣ Create Database
CREATE DATABASE tawi_db;

-- 2️⃣ Connect to Database
\c tawi_db;

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'donor', 'volunteer')) DEFAULT 'donor',
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- PROJECTS TABLE
-- ==========================================
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    location VARCHAR(150),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) CHECK (status IN ('active', 'completed', 'upcoming')) DEFAULT 'active',
    created_by INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- TREE SPECIES TABLE
-- ==========================================
CREATE TABLE tree_species (
    id SERIAL PRIMARY KEY,
    species_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    growth_rate VARCHAR(50),
    ideal_conditions TEXT
);

-- ==========================================
-- LOCATIONS TABLE
-- ==========================================
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    county VARCHAR(100),
    description TEXT
);

-- ==========================================
-- TREE PLANTINGS TABLE
-- ==========================================
CREATE TABLE tree_plantings (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    volunteer_id INT REFERENCES users(id) ON DELETE SET NULL,
    tree_species VARCHAR(100),
    quantity INT CHECK (quantity > 0),
    planting_date DATE NOT NULL,
    location VARCHAR(150),
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- DONATIONS TABLE
-- ==========================================
CREATE TABLE donations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    method VARCHAR(20) CHECK (method IN ('mpesa', 'card', 'bank')) DEFAULT 'mpesa',
    transaction_code VARCHAR(50) UNIQUE,
    project_id INT REFERENCES projects(id) ON DELETE SET NULL,
    payment_status VARCHAR(20) CHECK (payment_status IN ('pending', 'success', 'failed')) DEFAULT 'pending',
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- REPORTS TABLE
-- ==========================================
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    submitted_by INT REFERENCES users(id) ON DELETE SET NULL,
    report_type VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- NOTIFICATIONS TABLE
-- ==========================================
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- AUDIT LOG TABLE
-- ==========================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255),
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- ✅ RELATIONSHIP INDEXES (for performance)
-- ==========================================
CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_project_status ON projects(status);
CREATE INDEX idx_donation_status ON donations(payment_status);
CREATE INDEX idx_notification_user ON notifications(user_id);

-- ==========================================
-- 🌱 SAMPLE DATA (OPTIONAL)
-- ==========================================
INSERT INTO users (full_name, email, phone, password_hash, role)
VALUES 
('Admin Tawi', 'admin@tawi.org', '+254700000000', 'hashed_password', 'admin'),
('John Doe', 'john@example.com', '+254711111111', 'hashed_password', 'donor'),
('Jane Tree', 'jane@example.com', '+254722222222', 'hashed_password', 'volunteer');

INSERT INTO projects (name, description, location, start_date, status, created_by)
VALUES
('Tawi Green Initiative', 'Main reforestation drive in Baringo County.', 'Baringo', '2025-01-10', 'active', 1);

INSERT INTO donations (user_id, amount, method, transaction_code, project_id, payment_status)
VALUES
(2, 500.00, 'mpesa', 'MPESA12345ABC', 1, 'success');

INSERT INTO tree_plantings (project_id, volunteer_id, tree_species, quantity, planting_date, location)
VALUES
(1, 3, 'Acacia', 30, '2025-02-15', 'Baringo Forest Zone');

INSERT INTO notifications (user_id, title, message)
VALUES
(2, 'Thank You for Your Donation', 'Your contribution has helped plant 30 trees in Baringo.'),
(3, 'Volunteer Activity', 'Your next planting event is scheduled for next weekend.');

-- ==========================================
-- 🎉 Done: All tables created successfully
-- ==========================================
