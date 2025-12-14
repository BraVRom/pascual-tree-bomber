import aiohttp
import asyncio
import time
import json

# ========== CONFIGURACIÓN ==========
URL_MENSAJE = "https://deco-my-tree-web.com/api/v1/message/URL_ID_DEL_ARBOL?by_app=false"
URL_TOKEN = "https://deco-my-tree-web.com/api/v1/user/fake-token"

headers_base = {
    "Host": "decomytree.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "*/*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Referer": "https://decomytree.com/home?hashedId=TU_ID_AQUI",
    "Origin": "https://decomytree.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
    "DNT": "1",
    "Sec-GPC": "1",
}

data_mensaje = {
    "name": "ViejitoPascual",
    "content": "Feliz Navidad",
    "deco_index": 20,
    "only_for_user": False,
}

# ========== CONFIGURACIÓN MEJORADA ==========
NUMERO_PETICIONES = 2
TIEMPO_ENTRE_PETICIONES = 0.5
TIEMPO_ESPERA_ERROR = 3.0
INTENTOS_MAXIMOS_RENOVACION = 3  # Máximo de intentos para renovar token
TIEMPO_ESPERA_RENOVACION = 5.0  # Espera antes de reintentar renovación

# Token inicial (se actualizará automáticamente)
token_actual = "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjU3NTMyOTEsImlhdCI6MTc2NTc0OTY5MSwidXNlcl9pZCI6MH0.PpwWu9JjK5q7JtzrDqXcnC72LZVaRCATadCeEYOjib3sGqkxra1Z5-g2-HMUhURI4-qrJ_LvMbP1mUT9XP07pg"


# ========== FUNCIONES DE TOKEN ==========
async def obtener_nuevo_token(session, intento=1):
    """Obtiene un nuevo token de acceso desde la API fake-token."""
    try:
        print(f"🔄 Intentando renovar token (intento {intento}/{INTENTOS_MAXIMOS_RENOVACION})...")
        
        async with session.get(URL_TOKEN, timeout=10) as respuesta:
            if respuesta.status == 200:
                datos = await respuesta.json()
                
                # Busca el token en la respuesta (puede estar en diferentes campos)
                nuevo_token = None
                
                # Busca en diferentes posibles campos
                campos_posibles = ["access_token", "token", "accessToken", "bearer_token"]
                for campo in campos_posibles:
                    if campo in datos:
                        nuevo_token = datos[campo]
                        break
                
                if nuevo_token:
                    # Asegura que tenga el formato "Bearer token"
                    if not nuevo_token.startswith("Bearer "):
                        nuevo_token = f"Bearer {nuevo_token}"
                    
                    print(f"✅ Token renovado exitosamente")
                    return nuevo_token
                else:
                    print(f"❌ No se encontró token en la respuesta: {datos}")
                    return None
            else:
                texto_error = await respuesta.text()
                print(f"❌ Error al obtener token: HTTP {respuesta.status} - {texto_error[:100]}")
                return None
                
    except Exception as e:
        print(f"❌ Excepción al obtener token: {type(e).__name__}: {e}")
        return None


def actualizar_headers_con_token(token):
    """Actualiza los headers con el nuevo token."""
    headers_actualizados = headers_base.copy()
    headers_actualizados["Authorization"] = token
    return headers_actualizados


# ========== FUNCIÓN PRINCIPAL DE ENVÍO ==========
async def enviar_peticion(session, id_tarea, token_compartido):
    """Envía peticiones con renovación automática de token en caso de 403."""
    contador = 0
    
    while True:
        try:
            inicio = time.time()
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Usa el token actual compartido
            headers_actuales = actualizar_headers_con_token(token_compartido["value"])
            
            async with session.post(
                URL_MENSAJE, 
                headers=headers_actuales, 
                json=data_mensaje, 
                timeout=timeout
            ) as respuesta:
                
                tiempo_respuesta = time.time() - inicio
                contador += 1
                texto_respuesta = await respuesta.text()
                
                # Manejo especial para código 403 (Forbidden)
                if respuesta.status == 403:
                    print(f"[Tarea-{id_tarea}] ⚠️  Token expirado (403). Intentando renovar...")
                    
                    # Intenta renovar el token
                    for intento in range(1, INTENTOS_MAXIMOS_RENOVACION + 1):
                        nuevo_token = await obtener_nuevo_token(session, intento)
                        
                        if nuevo_token:
                            # Actualiza el token compartido para todas las tareas
                            token_compartido["value"] = nuevo_token
                            print(f"[Tarea-{id_tarea}] ✅ Token actualizado. Reintentando petición...")
                            
                            # Espera un momento antes de reintentar
                            await asyncio.sleep(1)
                            break
                        else:
                            print(f"[Tarea-{id_tarea}] ❌ Falló renovación {intento}. Esperando {TIEMPO_ESPERA_RENOVACION}s...")
                            await asyncio.sleep(TIEMPO_ESPERA_RENOVACION)
                    else:
                        print(f"[Tarea-{id_tarea}] ❌ No se pudo renovar token después de {INTENTOS_MAXIMOS_RENOVACION} intentos")
                        await asyncio.sleep(TIEMPO_ESPERA_ERROR)
                    
                    # Vuelve al inicio del bucle para reintentar con nuevo token
                    continue
                
                # Para otros códigos de estado
                estado_color = "✅" if respuesta.status == 200 else "⚠️ "
                print(f"[Tarea-{id_tarea}] {estado_color} Petición #{contador}: "
                      f"Estado {respuesta.status} en {tiempo_respuesta:.2f}s")
                
                if len(texto_respuesta) < 100 or respuesta.status != 200:
                    print(f"   Respuesta: {texto_respuesta[:100]}...")
                
                # Espera antes de la siguiente petición
                await asyncio.sleep(TIEMPO_ENTRE_PETICIONES)
                
        except asyncio.TimeoutError:
            print(f"[Tarea-{id_tarea}] ⏱️  Timeout después de 30 segundos")
            await asyncio.sleep(TIEMPO_ESPERA_ERROR)
            
        except aiohttp.ClientConnectorError as error:
            print(f"[Tarea-{id_tarea}] 🔌 Error de conexión: {error}")
            await asyncio.sleep(TIEMPO_ESPERA_ERROR * 2)
            
        except aiohttp.ClientError as error:
            print(f"[Tarea-{id_tarea}] ❌ Error HTTP: {error}")
            await asyncio.sleep(TIEMPO_ESPERA_ERROR)
            
        except Exception as error:
            print(f"[Tarea-{id_tarea}] ⚠️  Error inesperado: {type(error).__name__}: {error}")
            await asyncio.sleep(TIEMPO_ESPERA_ERROR)


# ========== FUNCIÓN PRINCIPAL ==========
async def principal():
    """Función principal con mejor manejo de recursos."""
    print(f"🚀 Iniciando {NUMERO_PETICIONES} tareas concurrentes")
    print(f"📤 Enviando a: {URL_MENSAJE}")
    print(f"🔑 Token inicial: {token_actual[:50]}...")
    print(f"👤 Nombre: {data_mensaje['name']}")
    print(f"💬 Mensaje: {data_mensaje['content']}")
    print("Presiona Ctrl+C para detener\n")
    
    # Token compartido entre todas las tareas (usamos dict para mutabilidad)
    token_compartido = {"value": token_actual}
    
    # Verificar token inicial
    print("🔍 Verificando token inicial...")
    async with aiohttp.ClientSession() as session_test:
        headers_test = actualizar_headers_con_token(token_compartido["value"])
        async with session_test.post(URL_MENSAJE, headers=headers_test, json=data_mensaje, timeout=10) as resp_test:
            if resp_test.status == 403:
                print("❌ Token inicial expirado. Obteniendo uno nuevo...")
                nuevo_token = await obtener_nuevo_token(session_test)
                if nuevo_token:
                    token_compartido["value"] = nuevo_token
                else:
                    print("⚠️  No se pudo obtener token inicial. Continuando con el existente...")
    
    # Configuración del connector
    connector = aiohttp.TCPConnector(
        limit=NUMERO_PETICIONES * 2,
        force_close=True,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Crea las tareas con IDs y comparte el token
        tareas = [
            enviar_peticion(session, i, token_compartido) 
            for i in range(NUMERO_PETICIONES)
        ]
        
        try:
            await asyncio.gather(*tareas)
        except KeyboardInterrupt:
            print("\n\n🛑 Programa interrumpido por el usuario")
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")


# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    try:
        import sys
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        print("=" * 60)
        print("SCRIPT DE ENVÍO CON RENOVACIÓN AUTOMÁTICA DE TOKEN")
        print("=" * 60)
        
        asyncio.run(principal())
        
    except KeyboardInterrupt:
        print("\n✅ Programa finalizado por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar: {e}")