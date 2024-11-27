-- Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS MIRA_DB;

-- Use the newly created database
USE MIRA_DB;

-- Table to store expert details (Experts)
CREATE TABLE IF NOT EXISTS Experts (
    expert_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each expert
    password VARCHAR(255) NOT NULl, -- Hashed password for security
    first_name VARCHAR(100) NOT NULL, -- First name of the expert
    last_name VARCHAR(100) NOT NULL, -- Last name of the expert
    email VARCHAR(255) NOT NULL UNIQUE, -- Expert's unique email address
    phone_number VARCHAR(15) NOT NULL, -- Contact phone number
    department VARCHAR(100) NOT NULL, -- Department the expert belongs to (e.g., 'AI', 'Research')
    availability VARCHAR(100), -- Availability status (e.g., 'Available', 'Not Available')
    date_of_birth DATE, -- Date of birth of the expert
    experience_years INT, -- Total years of professional experience
    resume LONGBLOB, -- Expert's resume stored in PDF format (binary format to store PDF data)
    skills TEXT, -- Comma-separated list of skills
    workload_hours INT, -- Available workload in hours (indicates the expert’s availability)
    completed_interviews INT DEFAULT 0, -- Number of completed interviews by the expert
    scheduled_interviews INT DEFAULT 0, -- Number of interviews scheduled for the expert
    profile_image LONGBLOB, -- Expert's passport-size profile photo (binary data)
    expertise TEXT  -- Areas of expertise (comma-separated list of fields the expert specializes in)
);

-- Table to store interview details, linking applicants and experts, with department segregation
CREATE TABLE IF NOT EXISTS Interview (
    interview_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each interview
    applicant_id INT NOT NULL, -- Reference to the applicant participating in the interview
    expert_id INT NOT NULL, -- Reference to the expert conducting the interview
    panel_members TEXT NOT NULL, -- Comma-separated list of official IDs for panel members
    department VARCHAR(100) NOT NULL, -- Department conducting the interview (e.g., 'AI', 'Research')
    post VARCHAR(100) NOT NULL, -- Post or position the applicant is being interviewed for
    interview_date DATE NOT NULL, -- Date of the interview
    interview_time TIME NOT NULL, -- Time of the interview
    venue TEXT NOT NULL, -- Venue for the interview (e.g., office address or online platform details)
    mode ENUM('Online', 'Offline', 'Hybrid') NOT NULL, -- Mode of the interview (e.g., 'Online', 'Offline', 'Hybrid')
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending', -- Status of the interview
    finalized_by VARCHAR(100), -- HR or official who finalized the interview panel
    finalized_date DATETIME, -- Date and time when the interview panel was finalized
    FOREIGN KEY (applicant_id) REFERENCES Applicants(applicant_id) ON DELETE CASCADE, -- Reference to the applicant
    FOREIGN KEY (expert_id) REFERENCES Experts(expert_id) ON DELETE CASCADE -- Reference to the expert
);

-- Table to store HR user details, segregated by department
CREATE TABLE IF NOT EXISTS HR (
    hr_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each HR user
    first_name VARCHAR(100) NOT NULL, -- First name of the HR user
    last_name VARCHAR(100) NOT NULL, -- Last name of the HR user
    password VARCHAR(255) NOT NULL, -- Hashed password for security
    email VARCHAR(255) NOT NULL UNIQUE, -- HR user’s unique email address
    phone_number VARCHAR(15) NOT NULL, -- Contact number
    department VARCHAR(100) NOT NULL, -- Department the HR user belongs to (e.g., 'AI', 'Research')
    post VARCHAR(100), -- Position or role of the HR user (e.g., 'Recruiter', 'Manager')
    profile_image LONGBLOB -- Binary data for storing HR user’s profile image
);

-- Table to store action history (audit logs) with department segregation
CREATE TABLE IF NOT EXISTS ActionHistory (
    action_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each action log entry
    user_id INT NOT NULL, -- Reference to the user performing the action (HR, Expert, Admin)
    user_role ENUM('HR', 'Expert', 'Admin') NOT NULL, -- Role of the user performing the action
    action_type VARCHAR(255) NOT NULL, -- Type of action (e.g., "Create Interview", "Update Applicant")
    action_details TEXT, -- Detailed description of the action
    action_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, -- Timestamp for when the action occurred
    department VARCHAR(100) NOT NULL, -- Department where the action took place (e.g., 'AI', 'Research')
    FOREIGN KEY (user_id) REFERENCES HR(hr_id) ON DELETE CASCADE -- Foreign key reference to HR table
);

-- Table to store job posts
CREATE TABLE IF NOT EXISTS JobPosts (
    job_post_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each job post
    department VARCHAR(100) NOT NULL, -- Department for which the job post is (e.g., 'AI', 'Research')
    post_title VARCHAR(255) NOT NULL, -- Title of the job post (e.g., 'Software Engineer')
    job_description TEXT NOT NULL, -- Detailed description of the job post
    eligibility_criteria TEXT, -- Eligibility criteria for the job post (e.g., qualifications, experience)
    required_skills TEXT, -- Comma-separated list of skills required for the job (to be stored as bullet points in the UI)
    job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship') NOT NULL, -- Type of job (Full-time, Part-time, etc.)
    location VARCHAR(255), -- Job location (e.g., 'New York', 'Remote')
    application_deadline DATE, -- Deadline for applying to the job
    status ENUM('Open', 'Closed', 'On Hold') DEFAULT 'Open', -- Current status of the job post
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the job post was created
    updated_date DATETIME -- Timestamp for the last update to the job post
);




SET GLOBAL wait_timeout = 28800;  -- Set to a higher value (default is 28800 seconds, which is 8 hours)
SET GLOBAL interactive_timeout = 28800;  -- Same as above for interactive sessions

-- Table to store applicants details (applicants)
CREATE TABLE IF NOT EXISTS Applicants01 (
    applicant_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each applicant
    first_name VARCHAR(100) NOT NULL, -- First name of the applicant
    last_name VARCHAR(100) NOT NULL, -- Last name of the applicant
    phone_number VARCHAR(15) NOT NULL, -- Contact phone number
    email VARCHAR(255) NOT NULL, -- Applicant's email address
    date_of_birth DATE, -- Date of birth of the applicant
    address TEXT, -- Address of the applicant
    resume TEXT , -- Path or content of the resume (can be stored as a file path or as binary content)
    skills TEXT , -- Comma-separated list of skills
    date_applied DATE , -- Date when the applicant applied
    profile_image LONGBLOB, -- Column to store the applicant's profile image (stored as binary data)
    department VARCHAR(100) NOT NULL -- Department the applicant is applying to (e.g., 'AI', 'Research')
);
SELECT * FROM mira_db.applicants01;