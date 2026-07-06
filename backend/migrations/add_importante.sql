-- Migración: añadir columna 'importante' a la tabla tareas
-- Ejecutar UNA SOLA VEZ contra la base de datos

ALTER TABLE tareas ADD COLUMN IF NOT EXISTS importante BOOLEAN NOT NULL DEFAULT FALSE;

-- Verificar
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'tareas' AND column_name = 'importante';