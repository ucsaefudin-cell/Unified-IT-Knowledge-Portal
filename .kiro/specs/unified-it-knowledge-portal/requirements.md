# Requirements Document

## Introduction

The Unified IT Knowledge Portal is a full-stack web application that serves as a centralized, bilingual (English/Bahasa Indonesia) knowledge base covering two main pillars: SAP Business One Solutions and AWS Cloud Infrastructure. The portal features a public infographic-style knowledge base accessible to all guests, and a gated section for advanced business best practices and case studies that requires user registration and email verification. The system is designed for deployment on AWS EC2 with static assets served from S3, backed by a PostgreSQL database on AWS RDS, and includes a FinOps automation script for EC2 scheduling.

## Glossary

- **Portal**: The Unified IT Knowledge Portal web application.
- **Guest**: An unauthenticated visitor browsing the Portal.
- **User**: A registered and email-verified account holder.
- **SAP_Pillar**: The SAP Business One Solutions section of the Portal.
- **AWS_Pillar**: The AWS Cloud Infrastructure section of the Portal.
- **Knowledge_Article**: A public infographic-style content item belonging to either the SAP_Pillar or AWS_Pillar.
- **Best_Practice**: A gated advanced scenario or case study content item belonging to either pillar.
- **Teaser**: A short excerpt of a Best_Practice visible to Guests, accompanied by a blur effect and lock icon.
- **Auth_System**: The authentication and authorization subsystem handling registration, login, and email verification.
- **Search_Engine**: The live search subsystem that queries Knowledge_Articles and Best_Practices across both pillars without page reloads.
- **Language_Toggle**: The UI control that switches the Portal's display language between English and Bahasa Indonesia.
- **Scheduler_Script**: The standalone Python/Boto3 script that automates EC2 instance start/stop scheduling.
- **Seeder**: The data seeding script that populates the database with initial placeholder content.
- **Dashboard**: The homepage Bento Box/Grid layout presenting both pillars.

---

## Requirements

### Requirement 1: Dashboard Homepage

**User Story:** As a Guest, I want to see a modern Bento Box/Grid dashboard on the homepage, so that I can quickly navigate to either the SAP Business One or AWS Cloud pillar.

#### Acceptance Criteria

1. THE Portal SHALL render a responsive Bento Box/Grid dashboard as the homepage using Tailwind CSS grid layouts.
2. THE Dashboard SHALL display two clearly labeled primary sections: SAP_Pillar and AWS_Pillar.
3. WHEN the viewport width changes, THE Dashboard SHALL reflow its grid layout to remain readable on mobile, tablet, and desktop screen sizes.
4. THE Dashboard SHALL include a professional footer displaying the text "© 2026 Ucu Saefudin. All rights reserved."
5. WHEN new Knowledge_Articles are added to the database, THE Dashboard SHALL auto-generate the corresponding cards without requiring code changes.

---

### Requirement 2: Public Knowledge Base (SAP Pillar)

**User Story:** As a Guest, I want to browse SAP Business One knowledge articles in an infographic style, so that I can learn about Master Data, Purchasing (A/P), Sales (A/R), and Inventory topics.

#### Acceptance Criteria

1. THE Portal SHALL display Knowledge_Articles for the SAP_Pillar covering the topic categories: Master Data, Purchasing (A/P), Sales (A/R), and Inventory.
2. WHEN a Guest visits the SAP_Pillar section, THE Portal SHALL render all SAP Knowledge_Articles as card components populated from the database.
3. THE Portal SHALL present SAP Knowledge_Article content using SAP Business One v10 or newer standards.
4. WHEN the database contains no SAP Knowledge_Articles, THE Portal SHALL display a placeholder message indicating no content is available.
5. THE Portal SHALL make all SAP Knowledge_Articles accessible to Guests without requiring authentication.

---

### Requirement 3: Public Knowledge Base (AWS Pillar)

**User Story:** As a Guest, I want to browse AWS Cloud infrastructure knowledge articles in an infographic style, so that I can learn about EC2, S3, RDS, and CloudFront fundamentals.

#### Acceptance Criteria

1. THE Portal SHALL display Knowledge_Articles for the AWS_Pillar covering the topic categories: EC2, S3, RDS, and CloudFront.
2. WHEN a Guest visits the AWS_Pillar section, THE Portal SHALL render all AWS Knowledge_Articles as card components populated from the database.
3. THE Portal SHALL present AWS Knowledge_Article content following modern AWS Cloud best practices.
4. WHEN the database contains no AWS Knowledge_Articles, THE Portal SHALL display a placeholder message indicating no content is available.
5. THE Portal SHALL make all AWS Knowledge_Articles accessible to Guests without requiring authentication.

---

### Requirement 4: Gated Best Practices Section

**User Story:** As a Guest, I want to see titles and teasers of advanced best practice articles, so that I understand what content is available and am motivated to register.

#### Acceptance Criteria

1. THE Portal SHALL display the title and Teaser of every Best_Practice to Guests regardless of authentication status.
2. WHEN a Guest views a Best_Practice listing, THE Portal SHALL apply a visual blur effect to the detailed content body and overlay a lock icon (🔒).
3. WHEN a Guest attempts to access the full content of a Best_Practice, THE Portal SHALL redirect the Guest to the registration or login page.
4. THE Portal SHALL seed initial Best_Practice placeholders for the SAP_Pillar covering: CSL02 Procurement, CSL06 CRM, and CSL08 Service case studies.
5. THE Portal SHALL seed initial Best_Practice placeholders for the AWS_Pillar covering: RDS Backup to S3, EC2 Troubleshooting, and FinOps Cost Optimization guides.
6. WHEN a User is authenticated, THE Portal SHALL display the full content of Best_Practices without blur or lock overlay.
7. THE Portal SHALL support unlimited Best_Practice entries per pillar without requiring schema changes.

---

### Requirement 5: User Registration and Email Verification

**User Story:** As a Guest, I want to register for an account with email verification, so that I can access the gated best practice content.

#### Acceptance Criteria

1. WHEN a Guest submits a registration form with a valid email address and password, THE Auth_System SHALL create a new unverified User account.
2. WHEN a new User account is created, THE Auth_System SHALL send an email verification link to the registered email address within 60 seconds.
3. WHEN a User clicks a valid email verification link, THE Auth_System SHALL mark the User account as verified and allow login.
4. IF a User attempts to log in with an unverified email address, THEN THE Auth_System SHALL deny access and display a message instructing the User to verify their email.
5. IF a registration form is submitted with an email address already registered, THEN THE Auth_System SHALL return an error message indicating the email is already in use.
6. IF a registration form is submitted with a password shorter than 8 characters, THEN THE Auth_System SHALL return a validation error before creating the account.
7. WHEN an email verification link has been unused for more than 24 hours, THE Auth_System SHALL treat the link as expired and prompt the User to request a new verification email.

---

### Requirement 6: User Login and Session Management

**User Story:** As a registered User, I want to log in securely, so that I can access gated content during my session.

#### Acceptance Criteria

1. WHEN a User submits valid credentials (email and password) for a verified account, THE Auth_System SHALL create an authenticated session and redirect the User to the Dashboard.
2. IF a User submits incorrect credentials, THEN THE Auth_System SHALL return an error message without revealing whether the email or password was incorrect.
3. WHEN a User logs out, THE Auth_System SHALL invalidate the session and redirect the User to the homepage.
4. WHILE a User session is active, THE Portal SHALL display the User's authenticated state in the navigation bar.
5. WHEN a session has been inactive for more than 60 minutes, THE Auth_System SHALL automatically invalidate the session and require re-authentication.

---

### Requirement 7: Live Search

**User Story:** As a Guest or User, I want to search for content across both pillars in real time, so that I can find relevant articles without navigating manually or reloading the page.

#### Acceptance Criteria

1. THE Search_Engine SHALL provide a search input field visible on the Dashboard and all content listing pages.
2. WHEN a user types at least 2 characters into the search input, THE Search_Engine SHALL query both Knowledge_Articles and Best_Practices across both pillars and return matching results without a page reload.
3. WHEN search results are returned, THE Search_Engine SHALL display each result with its title, pillar category, and content type (Knowledge_Article or Best_Practice).
4. WHEN a Guest's search returns Best_Practice results, THE Search_Engine SHALL display only the title and Teaser for those results, consistent with the gated access rules.
5. WHEN no results match the search query, THE Search_Engine SHALL display a "no results found" message.
6. WHEN the search input is cleared, THE Search_Engine SHALL restore the default content view.
7. THE Search_Engine SHALL return results within 500ms of the user stopping input for queries against a dataset of up to 10,000 articles.

---

### Requirement 8: Bilingual Language Toggle

**User Story:** As a user, I want to switch the portal's display language between English and Bahasa Indonesia, so that I can read content in my preferred language.

#### Acceptance Criteria

1. THE Language_Toggle SHALL be accessible from the navigation bar on every page of the Portal.
2. WHEN a user activates the Language_Toggle, THE Portal SHALL switch all UI labels, navigation items, and static text to the selected language without a full page reload.
3. THE Portal SHALL support English (EN) and Bahasa Indonesia (ID) as the two available languages.
4. WHEN a user selects a language, THE Portal SHALL persist the language preference for the duration of the browser session.
5. WHEN a Knowledge_Article or Best_Practice has content available in both languages, THE Portal SHALL display the content in the currently selected language.
6. IF a Knowledge_Article or Best_Practice does not have a translation for the selected language, THEN THE Portal SHALL fall back to displaying the content in English.

---

### Requirement 9: Database Schema and Content Model

**User Story:** As a developer, I want a well-structured PostgreSQL schema, so that the Portal can store and retrieve all content types efficiently.

#### Acceptance Criteria

1. THE Portal SHALL use a PostgreSQL database hosted on AWS RDS as the sole persistent data store.
2. THE Portal's database schema SHALL include a `category` column on content tables to distinguish between SAP_Pillar and AWS_Pillar content.
3. THE Portal's database schema SHALL support storing Knowledge_Articles with at minimum: id, title, topic_category, pillar (SAP/AWS), summary, body_en, body_id, and created_at fields.
4. THE Portal's database schema SHALL support storing Best_Practices with at minimum: id, title, pillar (SAP/AWS), teaser, body_en, body_id, case_study_ref, and created_at fields.
5. THE Portal's database schema SHALL support storing Users with at minimum: id, email, password_hash, is_verified, verification_token, and created_at fields.
6. WHEN the Seeder is executed, THE Seeder SHALL populate the database with at least the initial placeholder Knowledge_Articles and Best_Practices defined in Requirements 2, 3, and 4.
7. WHEN the Seeder is executed on a database that already contains seed data, THE Seeder SHALL skip duplicate entries rather than inserting duplicates.

---

### Requirement 10: Flask Application Structure

**User Story:** As a developer, I want a clean, organized Flask project folder structure, so that the codebase is maintainable and ready for AWS EC2 deployment.

#### Acceptance Criteria

1. THE Portal SHALL be implemented as a Python Flask application following a clean modular folder structure separating routes, models, templates, and static assets.
2. THE Portal's static assets (CSS, JavaScript, images) SHALL be organized for deployment to AWS S3.
3. THE Portal SHALL use SQLAlchemy as the ORM layer for all database interactions with the PostgreSQL RDS instance.
4. THE Portal SHALL load all environment-specific configuration (database URL, secret key, email credentials, AWS credentials) from environment variables or a `.env` file, with no hardcoded secrets in source code.
5. THE Portal SHALL include a `requirements.txt` file listing all Python dependencies with pinned versions.

---

### Requirement 11: EC2 Scheduling Automation (FinOps)

**User Story:** As a cloud administrator, I want an automated script to start and stop the EC2 instance on a schedule, so that I can reduce compute costs during off-hours.

#### Acceptance Criteria

1. THE Scheduler_Script SHALL be a standalone Python script using the Boto3 library, designed to run as an AWS Lambda function.
2. WHEN the Scheduler_Script is invoked at 07:00 (local time), THE Scheduler_Script SHALL start the designated EC2 instance.
3. WHEN the Scheduler_Script is invoked at 19:00 (local time), THE Scheduler_Script SHALL stop the designated EC2 instance.
4. THE Scheduler_Script SHALL read the target EC2 instance ID from an environment variable rather than hardcoding it.
5. IF the EC2 instance is already in the target state (running when start is called, or stopped when stop is called), THEN THE Scheduler_Script SHALL log the current state and take no further action.
6. WHEN the Scheduler_Script starts or stops an EC2 instance, THE Scheduler_Script SHALL log the action, instance ID, and timestamp.

---

### Requirement 12: Code Comments in Bahasa Indonesia

**User Story:** As a developer learning the system, I want all inline comments, docstrings, and step-by-step explanations inside the code written in Bahasa Indonesia, so that I can understand the logic connecting routing, database, and UI.

#### Acceptance Criteria

1. THE Portal's Python source files SHALL include docstrings written in Bahasa Indonesia for all functions, classes, and modules.
2. THE Portal's Python source files SHALL include inline comments in Bahasa Indonesia explaining the logic of routing, database queries, and business rules.
3. THE Portal's JavaScript source files SHALL include inline comments in Bahasa Indonesia explaining UI interactions, AJAX calls, and DOM manipulation logic.
4. THE Scheduler_Script SHALL include docstrings and inline comments in Bahasa Indonesia explaining each step of the EC2 automation logic.
5. THE Seeder SHALL include inline comments in Bahasa Indonesia explaining the purpose of each data block being inserted.
