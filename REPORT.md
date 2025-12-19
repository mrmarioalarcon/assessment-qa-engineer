Informe de Pruebas – API de Gestión de Inventario

Alcance
Este informe documenta las pruebas funcionales y de API realizadas a la API de Gestión de Inventario.

El objetivo fue identificar defectos, validar el comportamiento esperado y medir la cobertura de las pruebas sin modificar el código fuente de la aplicación.

Restricciones
•	El directorio app/ no fue modificado.
•	Todos los hallazgos fueron detectados mediante pruebas automatizadas.
•	Los errores (bugs) se documentaron como "GitHub Issues" únicamente en el repositorio bifurcado (forked).

Herramientas Utilizadas
•	Pytest
•	Pytest-cov
•	FastAPI TestClient

Resumen de Ejecución de Pruebas
•	Total de pruebas ejecutadas: 19
•	Aprobadas: 18
•	Fallidas: 1 (defecto conocido)
•	Cobertura de código: 92%

Prueba Fallida Conocida
•	test_low_stock_logic_bug
o	Propósito: Demuestra un error lógico crítico en el cálculo de bajo stock (existencias bajas).
o	Estado: Falla consistentemente, confirmando el defecto.

Errores (Bugs) Identificados
1.	El endpoint de bajo stock devuelve productos con inventario suficiente (Crítico)
2.	La creación de productos permite cargas (payloads) inválidas sin validación (Alto)
3.	La creación de productos no autorizada devuelve un estado HTTP incorrecto (Medio)
4.	El endpoint de inicio de sesión (login) no existe o está expuesto incorrectamente (Medio)

Conclusión
La API contiene múltiples defectos funcionales y relacionados con la validación.
Las pruebas automatizadas detectan y documentan con éxito estos problemas, alcanzando al mismo tiempo una alta cobertura de código.
El conjunto de pruebas proporciona una base sólida para futuras correcciones y pruebas de regresión.
