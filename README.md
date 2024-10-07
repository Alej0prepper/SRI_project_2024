# Sistemas de Recomendación Híbridos: Una Visión Integral

## Descripción

Este proyecto presenta una visión integral sobre los sistemas de recomendación híbridos, destacando su importancia en el panorama digital actual. El objetivo es proporcionar una comprensión más profunda de cómo estos sistemas combinan diversas técnicas—como el filtrado colaborativo, el filtrado basado en contenido y el filtrado demográfico—para ofrecer recomendaciones más precisas, diversas y personalizadas.

El informe explora las limitaciones de los enfoques tradicionales y resalta las ventajas de los métodos híbridos, en particular aquellos con ajuste dinámico de pesos, en aplicaciones del mundo real como el comercio electrónico, los servicios de streaming y la investigación académica.

## Autores

- **Alejandro Álvarez Lamazares** - Especialista en sistemas de recomendación y optimización de modelos de machine learning.
- **Frank Pérez Fleita** - Ingeniero en software con experiencia en la integración de datos y arquitecturas de sistemas recomendadores.

## Problema

Los sistemas de recomendación tradicionales, como el filtrado colaborativo y el filtrado basado en contenido, enfrentan desafíos significativos:
- **Problema del arranque en frío**: Dificultad para recomendar a nuevos usuarios o con nuevos productos debido a la falta de datos previos.
- **Escasez de datos**: Los usuarios suelen interactuar con una pequeña fracción de los ítems disponibles, lo que dificulta la personalización.
- **Efecto burbuja de filtro**: Exposición limitada a contenido similar que reduce la diversidad en las recomendaciones.

Los sistemas de recomendación híbridos ofrecen una solución al combinar múltiples enfoques, logrando una mayor precisión y diversidad en las recomendaciones. Este proyecto explora la implementación de un sistema híbrido con ajuste dinámico de pesos para adaptar las recomendaciones en tiempo real y en función de la disponibilidad de datos.

## Requerimientos

Para el correcto desempeño de este proyecto, se requieren los siguientes componentes:
- **Python 3.8 o superior** - Lenguaje de programación principal.
- **Bibliotecas de Python** - Instaladas mediante `pip`:
  - `flask` - Para el despliegue de la API.
  - `pandas`, `numpy` - Para la manipulación de datos.
  - `scikit-learn` - Para técnicas de clustering y métricas de similitud.
  - `scipy` - Para procesamiento avanzado de datos.
- **Docker** (opcional) - Si deseas ejecutar el proyecto en un contenedor para mayor facilidad de despliegue y aislamiento de dependencias.

## APIs Utilizadas

El sistema hace uso de los siguientes endpoints para la recomendación de contenido:
- **Flask API**: Se utiliza para manejar solicitudes de recomendación en tiempo real:
  - `POST /ratings` - Añade o actualiza la calificación de una película.
  - `GET /recommendations/<user_id>` - Obtiene recomendaciones personalizadas para un usuario específico basadas en su perfil y preferencias.
  - `GET /movies/<movie_id>` - Recupera información detallada de una película específica.

Si deseas agregar más endpoints o funcionalidades, puedes modificar el archivo principal `app.py` en el directorio raíz.

## Ejecución del Proyecto

Para ejecutar este proyecto, se ha incluido un archivo `startup.sh` en la raíz del repositorio. Este script instalará todas las dependencias necesarias y ejecutará la aplicación Flask. Sigue estos pasos para ejecutar el proyecto:

1. Asegúrate de que tienes los permisos adecuados para ejecutar el archivo `startup.sh`. Si no los tienes, puedes conceder los permisos con el siguiente comando:

   ```bash
   chmod +x startup.sh
   ```
2. Luego ejecuta el archivo con el siguiente comando:

   ```bash
   ./startup.sh
   ```
