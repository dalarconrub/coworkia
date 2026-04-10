# Inicio Rapido En Windows

## 1. Preparar el entorno virtual

Ejecuta:

[setup_venv.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/setup_venv.bat)

Esto:

- crea `.venv` si no existe
- actualiza `pip`
- instala las dependencias del proyecto

## 2. Iniciar Coworkia

Puedes arrancar el hub desde la raiz con:

[INICIAR_COWORKIA.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/INICIAR_COWORKIA.bat)

O desde `apps/` con:

[project_hub_gui.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/project_hub_gui.bat)

## 3. Si algo falla

- revisa que Python 3 este instalado
- vuelve a ejecutar `setup_venv.bat`
- comprueba que `.env` exista y tenga las credenciales necesarias
- ejecuta `apps\config_doctor.bat` para ver exactamente que variable o ruta falta

## Accesos principales

- Preparar entorno: [setup_venv.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/setup_venv.bat)
- Diagnostico de configuracion: [config_doctor.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/config_doctor.bat)
- Iniciar desde raiz: [INICIAR_COWORKIA.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/INICIAR_COWORKIA.bat)
- Iniciar desde apps: [project_hub_gui.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/project_hub_gui.bat)
