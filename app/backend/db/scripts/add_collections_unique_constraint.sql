-- Script para agregar constraint único a la tabla collections
-- Esto previene registros duplicados en la base de datos

-- Primero, eliminar duplicados existentes si los hay
-- (Solo ejecutar si es necesario)
/*
DELETE c1 FROM collections c1
INNER JOIN collections c2 
WHERE c1.id > c2.id 
AND c1.branch_office_id = c2.branch_office_id 
AND c1.cashier_id = c2.cashier_id 
AND c1.added_date = c2.added_date;
*/

-- Agregar constraint único
ALTER TABLE collections 
ADD CONSTRAINT uk_collections_branch_cashier_date 
UNIQUE (branch_office_id, cashier_id, added_date);
