# Pipeline de Procesamiento de Transacciones BTC
## Documento de Arquitectura — Patrón Pipe-and-Filter

---

## Descripción General

El sistema implementa el **patrón arquitectónico Pipe-and-Filter** para procesar transacciones de compra de Bitcoin (BTC) en tres monedas base: USD, EUR y GBP. El pipeline está compuesto por **5 filtros independientes** que se ejecutan de forma secuencial. Cada filtro recibe un diccionario de contexto (`transaction`), lo enriquece con nueva información y lo pasa al siguiente filtro a través de una interfaz común definida por la clase abstracta `BaseFilter`.

---

## Responsabilidades de Cada Filtro

### Filtro 1 — `ValidationFilter`
Verifica que la transacción de entrada contenga todos los campos obligatorios con valores válidos: `user_id` (cadena no vacía), `btc_amount` (número positivo) y `currency` (USD, EUR o GBP). Normaliza la moneda a mayúsculas y rechaza la transacción con un `ValueError` o `TypeError` si algún campo es inválido. Es la primera línea de defensa del pipeline.

### Filtro 2 — `AuthenticationFilter`
Confirma la identidad del usuario consultando la base de datos simulada `data/users.json` (que representa un servicio RDS o DynamoDB). Verifica que el `user_id` exista en el registro y que la cuenta esté activa. Si el usuario no existe o está suspendido, lanza un `PermissionError` y detiene el pipeline. En caso de éxito, enriquece el contexto con el nombre, correo y rol del usuario.

### Filtro 3 — `TransformationFilter`
Convierte el monto de BTC a la moneda base mediante una llamada simulada a una API REST (`MockBTCPriceAPI v1.0`). Utiliza tasas fijas realistas: 1 BTC = 65,000 USD / 60,500 EUR / 51,800 GBP. Calcula el valor total de la transacción (`btc_amount × btc_price`) y registra la fuente del precio y el timestamp de la consulta en el contexto.

### Filtro 4 — `FeeFilter`
Aplica la comisión fija de **5.00 USD** convertida a la moneda base de la transacción (USD: 5.00 / EUR: 4.62 / GBP: 3.96). Suma la comisión al subtotal para producir el monto final a pagar (`total_with_fee`). Registra el desglose completo (subtotal, comisión, total) en el contexto de la transacción.

### Filtro 5 — `StorageFilter`
Persiste la transacción completamente procesada en una base de datos **SQLite** (`data/transactions.db`). Genera un identificador único UUID4, registra el timestamp ISO de la operación y almacena los 13 campos del registro. Inicializa la tabla automáticamente si no existe. Marca la transacción con `status = "completed"` como confirmación final.

---

## Comunicación entre Filtros

Todos los filtros comparten la misma interfaz definida por `BaseFilter.process(transaction: dict) -> dict`. El objeto `transaction` actúa como el **pipe** del patrón: es un diccionario mutable que cada filtro recibe, enriquece con nuevos campos y retorna para el siguiente. El orquestador `Pipeline.execute()` itera sobre la lista de filtros en orden, pasando el resultado de cada uno como entrada del siguiente. Si cualquier filtro lanza una excepción, el pipeline se detiene inmediatamente y propaga el error con información diagnóstica clara.

---

## Flujo de Datos

```
{ user_id, btc_amount, currency }
        ↓ ValidationFilter
{ + validation_status }
        ↓ AuthenticationFilter
{ + authenticated, user_name, user_email, user_role }
        ↓ TransformationFilter
{ + btc_price, total_value, api_source, price_timestamp }
        ↓ FeeFilter
{ + fee, subtotal, total_with_fee }
        ↓ StorageFilter
{ + transaction_id, timestamp, status: "completed" }
```

---

*Arquitectura de Software · Python 3 · SQLite · Patrón Pipe-and-Filter*
