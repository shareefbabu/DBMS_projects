-- Add detailed fields to organizations table for Quick Launch flow

ALTER TABLE organizations
ADD COLUMN sector VARCHAR(50),
ADD COLUMN size_bucket VARCHAR(20),
ADD COLUMN country VARCHAR(50),
ADD COLUMN timezone VARCHAR(50);
