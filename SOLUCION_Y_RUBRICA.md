# SOLUCION DEL ASSESSMENT - QA ENGINEER
## Documento Confidencial para Evaluadores

---

## LISTA COMPLETA DE BUGS INTENCIONALES

### BUG #1: Token Expirado No Lanza Excepcion (CRITICAL)
**Ubicacion:** `app/main.py`, linea 68-71
**Descripcion:** Cuando un token JWT esta expirado, la funcion `verify_token` captura `jwt.ExpiredSignatureError` pero retorna `payload` (que no existe en ese scope) en lugar de lanzar una excepcion.
**Codigo defectuoso:**
```python
except jwt.ExpiredSignatureError:
    return payload  # ERROR: payload no existe, deberia lanzar HTTPException
```
**Comportamiento esperado:** Deberia lanzar `HTTPException(status_code=401, detail="Token expired")`
**Severidad:** CRITICAL - Permite bypass de autenticacion

---

### BUG #2: Low Stock Logica Invertida (HIGH)
**Ubicacion:** `app/main.py`, funcion `get_low_stock_products`
**Descripcion:** La comparacion usa `>` en lugar de `<`. Retorna productos con stock ALTO en vez de bajo.
**Codigo defectuoso:**
```python
if product["quantity"] > product["min_stock"]:  # ERROR: deberia ser <
```
**Comportamiento esperado:** `if product["quantity"] < product["min_stock"]:`
**Severidad:** HIGH - Funcionalidad critica de negocio invertida

---

### BUG #3: Calculo de Valor Total Incorrecto (HIGH)
**Ubicacion:** `app/main.py`, funcion `calculate_inventory_value`
**Descripcion:** Usa asignacion `=` en lugar de acumulacion `+=`. Solo retorna el valor del ultimo producto.
**Codigo defectuoso:**
```python
total = product["price"] * product["quantity"]  # ERROR: deberia ser +=
```
**Comportamiento esperado:** `total += product["price"] * product["quantity"]`
**Severidad:** HIGH - Reportes financieros incorrectos

---

### BUG #4: Division por Cero en Profit Margin (MEDIUM)
**Ubicacion:** `app/main.py`, funcion `calculate_profit_margin`
**Descripcion:** No valida que `cost` sea mayor a cero antes de dividir.
**Codigo defectuoso:**
```python
margin = (product["price"] - cost) / cost * 100  # ERROR: no valida cost != 0
```
**Comportamiento esperado:** Validar `if cost <= 0: raise HTTPException(400, "Cost must be greater than 0")`
**Severidad:** MEDIUM - Causa error 500

---

### BUG #5: Paginacion Incorrecta en list_products (MEDIUM)
**Ubicacion:** `app/main.py`, funcion `list_products`
**Descripcion:** El slice `[skip:limit]` es incorrecto. Deberia ser `[skip:skip+limit]`.
**Codigo defectuoso:**
```python
return products[skip:limit]  # ERROR: deberia ser [skip:skip+limit]
```
**Comportamiento esperado:** `return products[skip:skip+limit]`
**Severidad:** MEDIUM - Paginacion no funciona correctamente

---

### BUG #6: Update No Permite Valores Cero o Falsy (MEDIUM)
**Ubicacion:** `app/main.py`, funcion `update_product`
**Descripcion:** Las validaciones con `if product.name:` no permiten actualizar a valores como `0`, `""`, o `False`.
**Codigo defectuoso:**
```python
if product.price:  # ERROR: no permite actualizar price a 0
    existing["price"] = product.price
```
**Comportamiento esperado:** `if product.price is not None:`
**Severidad:** MEDIUM - No permite actualizar a ciertos valores validos

---

### BUG #7: Delete No Retorna 404 si No Existe (LOW)
**Ubicacion:** `app/main.py`, funcion `delete_product`
**Descripcion:** Si el producto no existe, no lanza error 404, simplemente no hace nada.
**Codigo defectuoso:**
```python
if product_id in fake_db["products"]:
    del fake_db["products"][product_id]
return None  # ERROR: no lanza 404 si no existe
```
**Comportamiento esperado:** `else: raise HTTPException(status_code=404, detail="Product not found")`
**Severidad:** LOW - Comportamiento silencioso

---

### BUG #8: Validacion de Precio Negativo Faltante (MEDIUM)
**Ubicacion:** `app/main.py`, funcion `create_product`
**Descripcion:** No valida que el precio y cantidad sean positivos.
**Comportamiento esperado:** Validar `price > 0` y `quantity >= 0`
**Severidad:** MEDIUM - Permite datos invalidos

---

### BUG #9: Search Case Sensitive (LOW)
**Ubicacion:** `app/main.py`, funcion `search_products`
**Descripcion:** La busqueda es case-sensitive, lo cual no es user-friendly.
**Codigo defectuoso:**
```python
if name in product["name"]:  # Case sensitive
```
**Comportamiento esperado:** `if name.lower() in product["name"].lower():`
**Severidad:** LOW - UX suboptima

---

### BUG #10: SECRET_KEY Hardcodeado (SECURITY)
**Ubicacion:** `app/main.py`, linea 13
**Descripcion:** La clave secreta JWT esta hardcodeada en el codigo.
**Codigo defectuoso:**
```python
SECRET_KEY = "secret123"
```
**Comportamiento esperado:** Usar variable de entorno `os.getenv("SECRET_KEY")`
**Severidad:** SECURITY - Vulnerabilidad de seguridad

---

## SUITE DE PRUEBAS COMPLETA (SOLUCION)

### tests/test_unit.py

```python
import pytest
from datetime import datetime, timedelta
import jwt
from app.main import (
    create_token, 
    verify_token, 
    SECRET_KEY, 
    ALGORITHM,
    fake_db
)


class TestTokenFunctions:
    def test_create_token_returns_valid_jwt(self):
        token = create_token("testuser", "admin")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert "exp" in decoded

    def test_create_token_sets_expiration(self):
        token = create_token("testuser", "user")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        assert exp_time > now
        assert exp_time < now + timedelta(hours=25)


class TestVerifyToken:
    def test_verify_valid_token(self, client, admin_token):
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import MagicMock
        
        creds = MagicMock(spec=HTTPAuthorizationCredentials)
        creds.credentials = admin_token
        
        result = verify_token(creds)
        assert result["sub"] == "admin"
        assert result["role"] == "admin"

    def test_verify_expired_token_should_raise_exception(self, client):
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        
        expired_payload = {
            "sub": "admin",
            "role": "admin",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        creds = MagicMock(spec=HTTPAuthorizationCredentials)
        creds.credentials = expired_token
        
        # BUG: Esto deberia lanzar HTTPException pero no lo hace
        # El test documenta el bug
        try:
            result = verify_token(creds)
            # Si llegamos aqui, el bug existe
            pytest.fail("Should have raised HTTPException for expired token")
        except (HTTPException, NameError, UnboundLocalError):
            pass  # Comportamiento esperado o error por el bug

    def test_verify_invalid_token_raises_exception(self, client):
        from fastapi.security import HTTPAuthorizationCredentials
        from unittest.mock import MagicMock
        from fastapi import HTTPException
        
        creds = MagicMock(spec=HTTPAuthorizationCredentials)
        creds.credentials = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(creds)
        assert exc_info.value.status_code == 401


class TestDatabaseOperations:
    def test_fake_db_structure(self, reset_db):
        assert "users" in fake_db
        assert "products" in fake_db
        assert "product_counter" in fake_db
        assert fake_db["product_counter"] == 0

    def test_user_credentials_exist(self):
        assert "admin" in fake_db["users"]
        assert "user" in fake_db["users"]
        assert fake_db["users"]["admin"]["password"] == "admin123"
        assert fake_db["users"]["user"]["password"] == "user123"
```

### tests/test_api.py

```python
import pytest
from fastapi import status


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        
    def test_health_returns_status_healthy(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAuthEndpoints:
    def test_login_admin_success(self, client):
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_user_success(self, client):
        response = client.post("/auth/login", json={
            "username": "user",
            "password": "user123"
        })
        assert response.status_code == 200

    def test_login_invalid_credentials(self, client):
        response = client.post("/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401


class TestProductEndpoints:
    def test_create_product_as_admin(self, client, admin_token, reset_db):
        response = client.post(
            "/products",
            json={
                "name": "Test Product",
                "price": 99.99,
                "quantity": 100,
                "min_stock": 10
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["price"] == 99.99
        assert data["id"] == 1

    def test_create_product_as_user_forbidden(self, client, user_token, reset_db):
        response = client.post(
            "/products",
            json={
                "name": "Test Product",
                "price": 99.99,
                "quantity": 100
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_create_product_without_token(self, client, reset_db):
        response = client.post(
            "/products",
            json={
                "name": "Test Product",
                "price": 99.99,
                "quantity": 100
            }
        )
        assert response.status_code == 403

    def test_create_product_negative_price_should_fail(self, client, admin_token, reset_db):
        # BUG: Deberia fallar pero no lo hace
        response = client.post(
            "/products",
            json={
                "name": "Negative Price Product",
                "price": -10.00,
                "quantity": 100
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Documenta el bug: permite precios negativos
        assert response.status_code == 201  # Bug: deberia ser 400

    def test_list_products(self, client, admin_token, reset_db):
        # Crear un producto primero
        client.post(
            "/products",
            json={"name": "Product 1", "price": 10, "quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_products_pagination_bug(self, client, admin_token, reset_db):
        # Crear 5 productos
        for i in range(5):
            client.post(
                "/products",
                json={"name": f"Product {i}", "price": 10, "quantity": 5},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        # BUG: skip=2, limit=2 deberia retornar productos 3 y 4
        response = client.get(
            "/products?skip=2&limit=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        # Bug: retorna [0:2] en lugar de [2:4]
        assert len(data) == 2  # Esto pasa pero los productos son incorrectos

    def test_get_product_by_id(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "Test", "price": 10, "quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.get(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Test"

    def test_get_product_not_found(self, client, admin_token, reset_db):
        response = client.get(
            "/products/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404

    def test_update_product(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "Original", "price": 10, "quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.put(
            f"/products/{product_id}",
            json={"name": "Updated"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_update_product_to_zero_price_bug(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "Test", "price": 10, "quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        # BUG: No permite actualizar precio a 0
        response = client.put(
            f"/products/{product_id}",
            json={"price": 0},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # El precio deberia ser 0 pero sigue siendo 10
        assert response.json()["price"] == 10  # Bug documentado

    def test_delete_product(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "ToDelete", "price": 10, "quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

    def test_delete_nonexistent_product_should_return_404(self, client, admin_token, reset_db):
        # BUG: Deberia retornar 404
        response = client.delete(
            "/products/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Bug: retorna 204 en lugar de 404
        assert response.status_code == 204  # Bug documentado


class TestInventoryEndpoints:
    def test_adjust_inventory_add(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "Stock Test", "price": 10, "quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.post(
            "/inventory/adjust",
            json={
                "product_id": product_id,
                "adjustment": 50,
                "reason": "Restock"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["new_quantity"] == 150

    def test_adjust_inventory_subtract(self, client, admin_token, reset_db):
        # Crear producto
        create_resp = client.post(
            "/products",
            json={"name": "Stock Test", "price": 10, "quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.post(
            "/inventory/adjust",
            json={
                "product_id": product_id,
                "adjustment": -30,
                "reason": "Sale"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["new_quantity"] == 70

    def test_low_stock_logic_inverted_bug(self, client, admin_token, reset_db):
        # Crear producto con bajo stock
        client.post(
            "/products",
            json={"name": "Low Stock", "price": 10, "quantity": 5, "min_stock": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Crear producto con alto stock
        client.post(
            "/products",
            json={"name": "High Stock", "price": 10, "quantity": 100, "min_stock": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/inventory/low-stock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        # BUG: Retorna "High Stock" en lugar de "Low Stock"
        # La logica esta invertida
        assert len(data) == 1
        assert data[0]["name"] == "High Stock"  # Bug: deberia ser "Low Stock"


class TestProfitMarginEndpoint:
    def test_calculate_profit_margin(self, client, admin_token, reset_db):
        create_resp = client.post(
            "/products",
            json={"name": "Margin Test", "price": 100, "quantity": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        response = client.get(
            f"/products/{product_id}/profit-margin?cost=80",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["margin_percentage"] == 25.0

    def test_profit_margin_division_by_zero_bug(self, client, admin_token, reset_db):
        create_resp = client.post(
            "/products",
            json={"name": "Margin Test", "price": 100, "quantity": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = create_resp.json()["id"]
        
        # BUG: Division por cero
        response = client.get(
            f"/products/{product_id}/profit-margin?cost=0",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Bug: retorna 500 en lugar de 400 con mensaje apropiado
        assert response.status_code == 500  # Bug documentado


class TestSearchEndpoint:
    def test_search_products(self, client, admin_token, reset_db):
        client.post(
            "/products",
            json={"name": "Apple iPhone", "price": 999, "quantity": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/products",
            json={"name": "Samsung Galaxy", "price": 899, "quantity": 15},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/products/search/Apple",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_case_sensitive_bug(self, client, admin_token, reset_db):
        client.post(
            "/products",
            json={"name": "Apple iPhone", "price": 999, "quantity": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # BUG: Busqueda case-sensitive
        response = client.get(
            "/products/search/apple",  # minuscula
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Bug: no encuentra porque es case-sensitive
        assert len(response.json()) == 0  # Bug documentado


class TestInventoryValueEndpoint:
    def test_inventory_value_single_product(self, client, admin_token, reset_db):
        client.post(
            "/products",
            json={"name": "Product 1", "price": 100, "quantity": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/inventory/value",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["total_value"] == 1000

    def test_inventory_value_accumulation_bug(self, client, admin_token, reset_db):
        # Crear multiples productos
        client.post(
            "/products",
            json={"name": "Product 1", "price": 100, "quantity": 10},  # 1000
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            "/products",
            json={"name": "Product 2", "price": 50, "quantity": 20},  # 1000
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        response = client.get(
            "/inventory/value",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # BUG: Solo retorna el valor del ultimo producto (1000)
        # Deberia ser 2000 (1000 + 1000)
        assert response.json()["total_value"] == 1000  # Bug: deberia ser 2000
```

---

## RUBRICA DE CALIFICACION

### 1. Deteccion de Bugs (30 puntos)

| Bug | Puntos | Criterio |
|-----|--------|----------|
| Token Expirado | 5 | Issue completo con reproduccion |
| Low Stock Invertido | 4 | Issue con evidencia |
| Inventory Value Bug | 4 | Issue con calculo correcto |
| Division por Cero | 3 | Issue con caso de prueba |
| Paginacion Bug | 3 | Issue con ejemplo |
| Update Zero Values | 3 | Issue documentado |
| Delete 404 Missing | 2 | Issue documentado |
| Negative Price | 2 | Issue documentado |
| Search Case Sensitive | 2 | Issue documentado |
| SECRET_KEY Hardcoded | 2 | Issue de seguridad |

**Criterios para Issues:**
- Titulo descriptivo: +0.5
- Pasos para reproducir: +1
- Esperado vs Actual: +0.5
- Severidad correcta: +0.5
- Evidencia adjunta: +0.5

---

### 2. Pruebas Automatizadas (40 puntos)

| Criterio | Puntos |
|----------|--------|
| Pruebas unitarias de funciones core | 10 |
| Pruebas de todos los endpoints | 15 |
| Pruebas que detectan los bugs | 10 |
| Uso correcto de fixtures | 3 |
| Organizacion y legibilidad | 2 |

**Desglose pruebas endpoint:**
- Auth endpoints: 3 pts
- CRUD productos: 5 pts
- Inventario: 4 pts
- Busqueda y calculo: 3 pts

---

### 3. Code Coverage (20 puntos)

| Coverage | Puntos |
|----------|--------|
| 100% | 20 |
| 90-99% | 15 |
| 80-89% | 10 |
| 70-79% | 5 |
| < 70% | 0 |

---

### 4. Documentacion (10 puntos)

| Criterio | Puntos |
|----------|--------|
| Resumen ejecutivo claro | 2 |
| Lista de bugs con referencias | 3 |
| Metricas de coverage | 2 |
| Recomendaciones | 2 |
| Instrucciones de ejecucion | 1 |

---

## TABLA DE CALIFICACION RAPIDA

| Rango | Calificacion | Decision |
|-------|--------------|----------|
| 90-100 | Excelente | Contratar |
| 75-89 | Bueno | Considerar |
| 60-74 | Aceptable | Segunda entrevista |
| < 60 | Insuficiente | No contratar |

---

## COMANDOS PARA VERIFICAR ENTREGA

```bash
# Verificar estructura de archivos
ls -la tests/

# Ejecutar pruebas con coverage
pytest --cov=app --cov-report=html --cov-report=term tests/

# Ver reporte de coverage
open htmlcov/index.html

# Verificar Issues en GitHub
gh issue list
```

---

## RED FLAGS (Descalificacion Automatica)

1. Modificar codigo fuente de `app/`
2. Copiar soluciones de internet
3. No crear Issues en GitHub
4. Coverage menor a 50%
5. Plagiar pruebas existentes
6. No completar en el tiempo asignado

---

## PUNTOS EXTRA (Hasta 10 puntos adicionales)

- Pruebas con Selenium: +5
- Pruebas de carga/stress: +3
- Reporte HTML profesional: +2
- CI/CD pipeline configurado: +5
