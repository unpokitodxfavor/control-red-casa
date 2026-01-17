# Changelog

Todas las mejoras notables de "Control Red Casa Pro" se documentarán en este archivo.

## [2.2.0] - 2026-01-17
### Añadido
- **Dashboard Personalizable**: Integración de `react-grid-layout`.
- **Widgets Movibles**: Estadísticas, Tabla de Dispositivos y Mapa de Red ahora son widgets arrastrables y redimensionables.
- **Persistencia Visual**: La disposición del dashboard se guarda en la base de datos por usuario.
- **Configuración Local Global**: Correcciones menores en endpoints de configuración.

## [2.1.0] - 2026-01-17
### Añadido
- **Telegram Integrado**: Sistema completo de notificaciones al móvil.
- **Sensores Asíncronos**: Nuevo motor de escaneo (Ping, Puertos, HTTP) que NO bloquea la interfaz web. Rapidez extrema incluso con dispositivos offline.
- **Script Diagnóstico**: `backend/test_telegram.py` para depurar conexiones.
- **Modo Estricto Local**: El backend ahora se vincula a `127.0.0.1:8001` para evitar bloqueos del Firewall de Windows.

### Corregido
- Solucionado el bug de "Conectando..." infinito al inicio (causado por bloqueo de firewall y pings síncronos).
- Solucionado el error al enviar mensajes con caracteres especiales a Telegram (se eliminó Markdown V1 para mayor estabilidad).
- Solucionado el problema donde el botón "Probar Conexión" no funcionaba si las alertas globales estaban desactivadas.

## [2.0.0] - 2026-01-16
### Añadido
- **Base de Datos SQLite**: Persistencia de dispositivos y configuración.
- **Dashboard React**: Nueva interfaz moderna y oscura.
- **API FastAPI**: Backend robusto con documentación automática (/docs).
- **Escáner ARP**: Detección de dispositivos en tiempo real.
- **Identificación de Fabricantes**: Base de datos OUI integrada.

## [1.0.0] - 2026-01-10
### Inicial
- Versión prototipo inicial.
