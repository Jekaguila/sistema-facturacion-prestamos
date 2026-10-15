# Decisiones de diseño

Este documento explica **por qué** el proyecto está organizado así. Cada decisión se relaciona con un tema de la Unidad 4.

## 1. Herencia solo donde hay una relación ES-UN estable

| Jerarquía | Por qué sí es herencia |
|---|---|
| `ErrorDominio → DatoInvalidoError → TasaInvalidaError` | Una tasa inválida **es un** dato inválido, que **es un** error del dominio. Permite capturar por nivel (`except DatoInvalidoError`). |
| `MetodoAmortizacion → FrancesCuotaFija / CapitalConstante` | Ambos **son** métodos de amortización y cumplen el mismo contrato (`desglosar`). |
| `LineaFactura → LineaGravada / LineaExenta` | Ambas **son** líneas de factura; solo cambia `impuesto()`. |

## 2. Composición donde hay TIENE-UN

| Relación | Por qué es composición |
|---|---|
| `Prestamo` tiene un `HistorialTasas` | El historial nace y muere con el préstamo; nadie más lo modifica. |
| `Prestamo` usa un `MetodoAmortizacion` | Se **inyecta**: cambiar de método no obliga a crear subclases de `Prestamo` (evita la explosión de subclases `PrestamoFrancesConMora`, `PrestamoCapitalConstanteSinMora`, …). |
| `Factura` tiene `LineaFactura` | Una factura agrupa líneas; no *es* una línea. |
| `ServicioPrestamos` tiene repositorio, almacén y generador | Colaboran; se reciben por el constructor. |

> Regla práctica: si dudas entre heredar o componer, **compón**. Hereda únicamente cuando puedas sustituir al padre por el hijo sin sorpresas (LSP).

## 3. Cómo se aplican los principios SOLID

- **SRP** — `Prestamo` calcula; `GeneradorRecibos` arma el recibo; `formatos.py` presenta; `almacenes.py` guarda; `ServicioPrestamos` orquesta.
- **OCP** — Un formato nuevo es una clase nueva con `@formato_recibo("html")`; un método nuevo es una subclase de `MetodoAmortizacion`. No se edita código existente.
- **LSP** — `test_contrato_lsp_cualquier_metodo_liquida_el_prestamo` prueba que cualquier método de amortización liquida el préstamo y que la suma del capital es el monto prestado.
- **ISP** — Protocolos de 1–3 miembros: quien solo formatea no depende de cómo se guarda.
- **DIP** — `ServicioPrestamos` depende de `Protocol`, no de clases concretas. La *raíz de composición* (`main.py`) es el único lugar que conoce las piezas concretas.

## 4. Encapsulamiento

- `Prestamo._saldo` no se modifica desde fuera: solo `aplicar_pago()`.
- `Cliente._documento` es privado y de solo lectura (`@property`).
- `HistorialTasas.tramos()` devuelve una **copia inmutable** (tupla); quien la reciba no puede alterar el historial.
- `Recibo`, `Pago`, `TramoTasa` son `@dataclass(frozen=True)`: una vez emitidos no cambian.

## 5. Dinero y fechas

- Todo el dinero usa `Decimal` con `ROUND_HALF_UP` a 2 decimales (`dinero.py`). Nunca `float`.
- La cuota *n* vence en `desembolso + n meses` (`fechas.sumar_meses` ajusta al último día del mes si hace falta).
- **La tasa que se aplica es la vigente en la fecha de vencimiento**, no la de la fecha de pago. Así un pago tardío no cambia el interés pactado; el atraso se cobra aparte como **mora**.

## 6. Reglas didácticas (no son asesoría legal ni contable)

- IVA 13 % solo sobre cargos gravados que se facturan (comisión de apertura 1.5 %, mora). Los intereses y el capital viajan en el **recibo** de cada cuota; en este modelo didáctico no se facturan.
- Mora: 24 % anual, base 360, con 5 días de gracia.
- Si tu país o institución tiene otras reglas, se cambian **en un solo lugar** (`PoliticaMora`, `LineaGravada`) gracias al diseño.

## 7. Qué se dejó fuera a propósito

Base de datos, interfaz gráfica, autenticación y moneda múltiple. Son buenos **retos de extensión** y el diseño está preparado: bastaría con implementar `RepositorioPrestamos` sobre SQLite, por ejemplo.
