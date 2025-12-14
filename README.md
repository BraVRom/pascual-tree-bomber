# 🎄 pascual-tree-bomber

Script asíncrono en **Python** para enviar mensajes automatizados a árboles virtuales en **Deco My Tree** usando **aiohttp**. Incluye renovación automática de token y manejo de errores.

> ⚠️ **Aviso importante**
>
> Este script puede enviar el mismo mensaje muchas veces al mismo árbol (potencialmente spam). Lo ideal es que no sea ofensivo y sea una pequeña broma.
>
> El uso de este tipo de automatizaciones para enviar mensajes no deseados, repetitivos o inapropiados **viola las normas de uso de Deco My Tree**, puede considerarse acoso y podría derivar en bloqueos o acciones legales.
>
> **No se recomienda su uso con fines maliciosos.** Si decides usarlo, hazlo únicamente con consentimiento y mensajes positivos.

---

## 📌 Descripción

Este script utiliza **asyncio** y **aiohttp**, así como **Brotli** para enviar mensajes de forma automatizada y concurrente a un árbol virtual en el servicio **Deco My Tree**, una aplicación web navideña donde las personas crean árboles de Navidad virtuales y reciben decoraciones y mensajes de amigos que se revelan el día de Navidad.

---

## ✨ Funcionalidades principales

* Envío de peticiones **POST concurrentes** a la API de mensajes.
* Renovación automática del **token de autenticación** cuando expira (detección de error 403).
* Manejo de errores de red, timeouts y respuestas inesperadas.
* Ejecución indefinida hasta detener manualmente con **Ctrl + C**.
* Logs detallados en consola con emojis para seguir el estado del script.

---

## 🧰 Requisitos

* **Python 3.11 o superior**
* Dependencias de Python:

```bash
pip install aiohttp brotli
```

---

## ⚙️ Configuración

### Parte editable del código

En la sección **CONFIGURACIÓN** puedes modificar:

```python
PythonURL_MENSAJE = "https://deco-my-tree-web.com/api/v1/message/URL_ID_DEL_ARBOL?by_app=false"
```

Cambia `URL_ID_DEL_ARBOL?` por el `hashedId` del árbol objetivo. Puedes obtenerlo desde la URL del árbol, por ejemplo:

```
https://decomytree.com/home?hashedId=TU_ID_AQUI
```

Configuración del mensaje:

```python
Pythondata_mensaje = {
    "name": "ViejitoPascual",            # Nombre que aparecerá en el mensaje
    "content": "Feliz navidad", # Contenido del mensaje
    "deco_index": 20,                    # Índice de la decoración (normalmente entre 0 y ~50), pone la galletita de jengibre
    "only_for_user": False,              # False = mensaje público en el árbol
}
```

### CONFIGURACIÓN 2 (parámetros avanzados)

* **NUMERO_PETICIONES**: número de tareas concurrentes.

  * Recomendado: 1 a 5 para reducir riesgo de bloqueo.
* **TIEMPO_ENTRE_PETICIONES**: segundos de espera entre envíos por tarea (por ejemplo 0.5 a 2.0).
* **INTENTOS_MAXIMOS_RENOVACION**: número máximo de intentos para renovar el token.

El token inicial está hardcodeado, pero el script lo renueva automáticamente usando el endpoint `/fake-token`, que parece ser público y usado para testing o bots.

---

## 🧠 Funcionamiento interno

1. **Inicio**

   * Comprueba si el token inicial es válido.
   * Si no lo es, solicita uno nuevo.

2. **Tareas concurrentes**

   * Se crean `NUMERO_PETICIONES` tareas asíncronas.
   * Cada tarea envía mensajes en un bucle infinito.

3. **Envío del mensaje**

   * Se utilizan headers que imitan un navegador real.
   * Autenticación mediante token Bearer.

4. **Detección de token expirado**

   * Si la API responde con 403, se intenta renovar el token.
   * Se reintenta el envío hasta el límite configurado.

5. **Manejo de errores**

   * Timeouts, errores de conexión y respuestas inválidas se gestionan con reintentos y pausas.

6. **Token compartido**

   * Todas las tareas utilizan el mismo token, actualizado en memoria compartida.

---

## ▶️ Ejecución

Guarda el código en un archivo, por ejemplo:

```bash
pascualbomber.py
```

Ejecuta el script con:

```bash
python pascualbomber.py
```

Verás logs en tiempo real en la consola. Para detener la ejecución, usa **Ctrl + C**.

---

## 📝 Notas finales

* El script es robusto gracias al uso de asincronía y renovación automática de token.
* Actualmente la API parece permitir envíos sin captcha, aunque esto puede cambiar.
* Para un uso ético:

  * Usa mensajes positivos.
  * Limita el número de envíos.
  * Envía mensajes solo a árboles de personas que hayan dado su consentimiento.

🎄 **Usa con responsabilidad y disfruta las fiestas de forma positiva.**
¡Feliz 2025!
