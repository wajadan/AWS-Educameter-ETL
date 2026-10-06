import json
import boto3
import ftfy
import os
import re  

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # --- CONFIGURACIÓN ---
    bucket_name = 'opinion-est-crudo' 
    
    # Rutas definidas
    key_origen = 'input_S11/sabirmco_rldb13_12_2025.sql'
    key_destino = 'outputS11/sabirmco_rldb13_12_2025_limpio.sql'
    
    # Rutas temporales
    path_descarga = '/tmp/original.sql'
    path_limpio = '/tmp/limpio.sql'
    
    # Compilamos la regla de emojis una sola vez para que sea más rápido
    # Esta regla busca caracteres fuera del rango básico (0000-FFFF)
    # Esto elimina emojis pero MANTIENE las tildes y ñ.
    filtro_emojis = re.compile(r'[^\u0000-\uFFFF]') 
    
    print(f"Iniciando descarga de: {key_origen}")
    
    try:
        # 1. Descargar
        s3.download_file(bucket_name, key_origen, path_descarga)
        
        print("Descarga completada. Iniciando limpieza...")
        
        # 2. Lógica de limpieza
        with open(path_descarga, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(path_limpio, 'w', encoding='utf-8') as outfile:
            
            lineas_procesadas = 0
            for line in infile:
                # A. Arreglar codificación (Mojibake)
                line_fixed = ftfy.fix_text(line)
                
                # B. Arreglar nulos específicos
                if "values (," in line_fixed:
                    line_fixed = line_fixed.replace("values (,", "values (NULL,")
                
                # C. Eliminar literal "\r\n"
                line_fixed = line_fixed.replace("\\r\\n", "") 
                
                # D. NUEVO: ELIMINAR EMOJIS
                # Reemplaza cualquier caracter "astral" (emojis) por vacío
                line_fixed = filtro_emojis.sub('', line_fixed)

                outfile.write(line_fixed)
                lineas_procesadas += 1
                
        print(f"Limpieza finalizada. Líneas procesadas: {lineas_procesadas}")
        print(f"Subiendo archivo a: {key_destino}")
        
        # 3. Subir
        s3.upload_file(path_limpio, bucket_name, key_destino)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Éxito. Archivo sin emojis guardado en {key_destino}')
        }
        
    except Exception as e:
        print(f"Error CRITICO: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error procesando archivo: {str(e)}')
        }