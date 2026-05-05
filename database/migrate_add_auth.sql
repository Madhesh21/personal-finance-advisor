-- Migration: Add password_hash column to users table
-- Safe to run on existing database — preserves all existing data.

USE personal_finance;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NOT NULL DEFAULT '' AFTER email;
