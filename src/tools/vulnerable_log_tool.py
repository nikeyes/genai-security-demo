import os


def leer_log(nombre_fichero: str) -> str:
    """
    Lee y devuelve el contenido de un fichero de log especificado.
    ¡IMPORTANTE! Solo debe usarse para leer ficheros con extensión '.log'.
    Por ejemplo: 'system.log' o 'application.log'.
    """
    print(f"🤖 DEBUG: La herramienta ha sido llamada con el argumento: '{nombre_fichero}'")

    # --- LA LÍNEA VULNERABLE ---
    # La función construye un comando de shell concatenando texto sin validar la entrada.
    # Esto es una vulnerabilidad de Inyección de Comandos.
    comando = f'cat {nombre_fichero}'

    print(f"🐚 DEBUG: Ejecutando el siguiente comando en la shell: '{comando}'")

    # Usamos os.popen para capturar la salida del comando y devolverla al LLM
    # os.system() también funcionaría pero no captura la salida tan fácilmente.
    with os.popen(comando) as p:
        resultado = p.read()
    return resultado
