-- ============================================
-- FAMILY TREE DATABASE SCHEMA
-- MySQL/MariaDB Compatible
-- ============================================

-- Create database (uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS family_tree_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE family_tree_db;

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- FAMILIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS families (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    join_code VARCHAR(10) UNIQUE NOT NULL,
    subscription_plan ENUM('free', 'basic', 'standard', 'pro', 'elite') DEFAULT 'free',
    person_count INT DEFAULT 0,
    person_limit INT DEFAULT 50,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by),
    INDEX idx_join_code (join_code),
    INDEX idx_subscription (subscription_plan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- FAMILY MEMBERS TABLE (User-Family relationship with roles)
-- ============================================
CREATE TABLE IF NOT EXISTS family_members (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_family_user (family_id, user_id),
    INDEX idx_family_id (family_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PERSONS TABLE (Actual family tree members)
-- ============================================
CREATE TABLE IF NOT EXISTS persons (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    gender ENUM('male', 'female', 'other') NOT NULL,
    birth_date DATE,
    death_date DATE,
    birth_place VARCHAR(255),
    bio TEXT,
    profile_image_url TEXT,
    facebook_url TEXT,
    is_deceased BOOLEAN DEFAULT FALSE,
    is_orphan BOOLEAN DEFAULT FALSE,
    generation_level INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_name (first_name, last_name),
    INDEX idx_generation (generation_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- COUPLES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS couples (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    person1_id VARCHAR(36) NOT NULL,
    person2_id VARCHAR(36) NOT NULL,
    marriage_date DATE,
    divorce_date DATE,
    status ENUM('married', 'divorced', 'separated', 'partners', 'widowed') DEFAULT 'married',
    is_root_couple BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (person1_id) REFERENCES persons(id) ON DELETE CASCADE,
    FOREIGN KEY (person2_id) REFERENCES persons(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_person1 (person1_id),
    INDEX idx_person2 (person2_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- RELATIONSHIPS TABLE (Parent-Child)
-- ============================================
CREATE TABLE IF NOT EXISTS relationships (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    parent_couple_id VARCHAR(36),
    child_id VARCHAR(36) NOT NULL,
    relationship_type ENUM('biological', 'adopted', 'step', 'foster') DEFAULT 'biological',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_couple_id) REFERENCES couples(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES persons(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_parent_couple (parent_couple_id),
    INDEX idx_child (child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- FAMILY SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS family_subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) UNIQUE NOT NULL,
    plan ENUM('free', 'basic', 'standard', 'pro', 'elite') DEFAULT 'free',
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    person_limit INT DEFAULT 50,
    amount DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'PHP',
    billing_cycle ENUM('monthly', 'yearly') DEFAULT 'monthly',
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    purchased_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (purchased_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_family_id (family_id),
    INDEX idx_status (status),
    INDEX idx_period_end (current_period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PAYMENT TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS payment_transactions (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    subscription_id VARCHAR(36),
    payment_gateway VARCHAR(50) NOT NULL DEFAULT 'paymongo',
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PHP',
    status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    plan ENUM('basic', 'standard', 'pro', 'elite') NOT NULL,
    billing_cycle ENUM('monthly', 'yearly') NOT NULL,
    payment_details JSON,
    webhook_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES family_subscriptions(id) ON DELETE SET NULL,
    INDEX idx_family_id (family_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SUPPORT TICKETS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    family_id VARCHAR(36),
    ticket_type ENUM('feature', 'bug', 'issue') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    screenshot_url TEXT,
    status ENUM('pending', 'reviewing', 'approved', 'rejected', 'resolved') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    reward_slots INT DEFAULT 0,
    is_rewarded BOOLEAN DEFAULT FALSE,
    admin_notes TEXT,
    reviewed_by VARCHAR(36),
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_family_id (family_id),
    INDEX idx_status (status),
    INDEX idx_ticket_type (ticket_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- ACTIVITY LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS activity_log (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INVITATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS invitations (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by VARCHAR(36) NOT NULL,
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    accepted_at TIMESTAMP NULL,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_email (email),
    INDEX idx_family_id (family_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SUBSCRIPTION PLANS TABLE (Reference data)
-- ============================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    id VARCHAR(36) PRIMARY KEY,
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    person_limit INT NOT NULL,
    monthly_price DECIMAL(10, 2) NOT NULL,
    yearly_price DECIMAL(10, 2) NOT NULL,
    features JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plan_code (plan_code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INSERT DEFAULT SUBSCRIPTION PLANS
-- ============================================
INSERT INTO subscription_plans (id, plan_code, name, description, person_limit, monthly_price, yearly_price, features) VALUES
('plan-free', 'free', 'Free Plan', 'Basic family tree features', 50, 0.00, 0.00, '{"pdf_export": true, "watermark": true, "api_access": false, "premium_templates": false}'),
('plan-basic', 'basic', 'Basic Plan', 'Extended family tree', 100, 100.00, 1000.00, '{"pdf_export": true, "watermark": false, "api_access": false, "premium_templates": false}'),
('plan-standard', 'standard', 'Standard Plan', 'Large family tree with API', 200, 200.00, 2000.00, '{"pdf_export": true, "watermark": false, "api_access": true, "premium_templates": false}'),
('plan-pro', 'pro', 'Pro Plan', 'Professional features', 500, 400.00, 4000.00, '{"pdf_export": true, "watermark": false, "api_access": true, "premium_templates": true, "priority_support": false}'),
('plan-elite', 'elite', 'Elite Plan', 'Unlimited family tree', 999999, 600.00, 6000.00, '{"pdf_export": true, "watermark": false, "api_access": true, "premium_templates": true, "priority_support": true}')
ON DUPLICATE KEY UPDATE name=name;

-- ============================================
-- ADMIN COUNT TRACKING TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS family_admin_limits (
    family_id VARCHAR(36) PRIMARY KEY,
    admin_count INT DEFAULT 0,
    max_admins INT DEFAULT 5,
    min_admins INT DEFAULT 1,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    CONSTRAINT check_admin_limits CHECK (admin_count <= max_admins AND admin_count >= min_admins)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TRIGGERS FOR ADMIN COUNT TRACKING
-- ============================================
DELIMITER //

CREATE TRIGGER IF NOT EXISTS update_admin_count_insert
AFTER INSERT ON family_members
FOR EACH ROW
BEGIN
    IF NEW.role = 'admin' THEN
        INSERT INTO family_admin_limits (family_id, admin_count)
        VALUES (NEW.family_id, 1)
        ON DUPLICATE KEY UPDATE admin_count = admin_count + 1;
    END IF;
END//

CREATE TRIGGER IF NOT EXISTS update_admin_count_update
AFTER UPDATE ON family_members
FOR EACH ROW
BEGIN
    IF NEW.role = 'admin' AND OLD.role != 'admin' THEN
        INSERT INTO family_admin_limits (family_id, admin_count)
        VALUES (NEW.family_id, 1)
        ON DUPLICATE KEY UPDATE admin_count = admin_count + 1;
    ELSEIF OLD.role = 'admin' AND NEW.role != 'admin' THEN
        UPDATE family_admin_limits 
        SET admin_count = admin_count - 1
        WHERE family_id = NEW.family_id;
    END IF;
END//

CREATE TRIGGER IF NOT EXISTS update_admin_count_delete
AFTER DELETE ON family_members
FOR EACH ROW
BEGIN
    IF OLD.role = 'admin' THEN
        UPDATE family_admin_limits 
        SET admin_count = admin_count - 1
        WHERE family_id = OLD.family_id;
    END IF;
END//

DELIMITER ;

-- ============================================
-- SAMPLE DATA (Optional - Uncomment to use)
-- ============================================
-- INSERT INTO users (id, email, full_name, password_hash, is_admin) VALUES
-- ('user-admin-001', 'admin@familytree.com', 'Admin User', '$2b$12$hash...', TRUE);

-- ============================================
-- SCHEMA COMPLETE
-- Total Tables: 13
-- Total Triggers: 3
-- ============================================
