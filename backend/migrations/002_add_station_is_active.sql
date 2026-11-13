-- Migration 002: Add is_active column to stations table
-- Idempotent check or direct alter for MySQL 8

ALTER TABLE stations ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
