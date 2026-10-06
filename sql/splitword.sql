SELECT 
    j.palabra_limpia AS palabra,
    COUNT(*) AS frecuencia
FROM 
    result_class, -- TU TABLA
    JSON_TABLE(
        -- 1. Truco: Convertir el texto en un Array JSON válido
        -- Reemplazamos espacios por "," para crear la estructura ["p1","p2"]
        CONCAT(
            '["', 
            REPLACE(
                REPLACE(REPLACE(LOWER(senti1), '"', ''), '.', ''), -- Limpieza básica de signos
                ' ', 
                '","'
            ), 
            '"]'
        ),
        -- 2. Extraer cada elemento del array como una fila
        "\([*]" COLUMNS (palabra_limpia VARCHAR(255) PATH "\)")
    ) AS j
WHERE 
    LENGTH(j.palabra_limpia) > 2 -- Filtra palabras de 1 o 2 letras (y, o, el, la...)
    AND j.palabra_limpia NOT IN (
        -- 3. TU LISTA NEGRA (Personalízala aquí)
        'los', 'las', 'una', 'unos', 'unas',
        'para', 'como', 'pero', 'por', 'sus', 
        'que', 'del', 'con', 'este', 'esta',
        'todo', 'toda', 'mas', 'muy', 'sin', 
        'sobre', 'cuando', 'estos', 'estas'
    )
GROUP BY j.palabra_limpia
ORDER BY frecuencia DESC
LIMIT 100;