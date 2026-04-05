# UI Design Rules — BSM1 Simulator Dashboard

Estas reglas definen el sistema visual del panel de control. Aplicar de forma
consistente en cualquier modificacion o extension de `app/static/index.html`.

---

## 1. Estructura y Contenedores (Layout)

| Rol | Color | Uso |
|-----|-------|-----|
| Fondo de secciones | `#444e54` | Color base de las "tarjetas" o contenedores principales (bloques de Influent, Performance, Effluent, etc.). Superficie sobre la que se apoya toda la informacion. |
| Fondo de subseccion resaltada | `#3f484d` | Subsecciones dentro de una tarjeta principal para crear profundidad. Diferencia el area de graficas del area de parametros. |
| Cabecera de contenedor | `#373f44` | Franja superior de cada bloque informativo. Enmarca el titulo de la seccion (ej. recuadro con "Influent") y lo separa visualmente del cuerpo de datos. |
| Menu activo / pestana activa | `#5e686c` | Resalta la pestana o seccion activa dentro del menu superior (ej. boton "Dashboard"). Contraste claro frente al resto de opciones. |

### Principios de layout

- Usar margenes y padding consistentes: `8px` interno, `12px` entre secciones.
- Las tarjetas deben tener `border-radius: 4px`.
- El sidebar de parametros tiene ancho fijo de `360px`.
- Las secciones son colapsables; estado por defecto definido en `localStorage`.

---

## 2. Capa de Datos y Tipografia

| Rol | Color | Uso |
|-----|-------|-----|
| Valores de medicion | `#9cc2e4` | **Exclusivo para datos variables y lecturas en tiempo real** (numeros como "9.8 days", "4096 mg/L", "83.9 %"). El operador localiza la cifra de forma inmediata por contraste cromatico. |
| Texto general y etiquetas | `#fafafa` | Todo el texto estatico: nombres de parametros, ejes de graficas, titulos. Blanco roto — lectura limpia sobre grises oscuros sin deslumbrar. |

### Principios tipograficos

- **Fuente obligatoria**: `'Open Sans', sans-serif` para TODO el texto de la interfaz.
  Importar siempre desde Google Fonts: `https://fonts.googleapis.com/css2?family=Open+Sans&display=swap`
- Excepcion: bloques de codigo, valores numericos en monoespacio y el diagrama ASCII
  usan `'Courier New', monospace` como complemento.
- **Nunca** mezclar fuentes decorativas ni `'Segoe UI'`, `system-ui` u otras sans-serif
  del sistema como fuente principal.
- Jerarquia de peso: titulos de seccion `600`, etiquetas `400`, valores de medicion `400` en `#9cc2e4`.
- **Nunca** usar el mismo color para una etiqueta y su valor asociado.

---

## 3. Semantica de Estados (Status Indicators)

Los colores de estado indican si el proceso va bien o requiere intervencion.

### Estado Correcto / Normal

| Elemento | Color |
|----------|-------|
| Fondo del indicador | `#53645e` |
| Texto del indicador | `#92ba7b` |

Ejemplo: pastilla verde con texto "Normal" cuando el parametro esta dentro de rango.

### Estado de Alarma / Alerta

| Elemento | Color |
|----------|-------|
| Fondo de la alarma | `#63555a` |
| Texto de la alarma | `#e37272` |

Ejemplo: recuadro rojizo con el nombre del parametro (ej. NH3) cuando el valor
supera el limite IWA. Debe destacar como prioridad visual inmediata.

### Reglas de aplicacion

- **No usar rojo para texto decorativo** — reservado exclusivamente para alarmas.
- **No usar verde para elementos que no sean estado "OK"** — evitar confusion semiotica.
- Los indicadores de estado siempre incluyen: fondo coloreado + texto coloreado + etiqueta textual (no depender solo del color para accesibilidad).
- Un tercer estado "Warning" puede usar `#6b6040` (fondo) / `#d4a843` (texto amarillo)
  para alertas intermedias (ej. parametro cerca del limite pero sin superarlo).

---

## 4. Inputs y Controles

- Campos de entrada: fondo `#2c3336`, borde `#5e686c`, texto `#fafafa`.
- Campo invalido (fuera de rango): borde `#e37272` (rojo alarma).
- Campo modificado respecto al default BSM1: borde `#9cc2e4` (azul datos).
- Botones primarios (Simular): fondo `#9cc2e4`, texto `#1a2226`.
- Botones secundarios (Reset, Pre-check): fondo `#444e54`, borde `#5e686c`, texto `#fafafa`.
- Toggle activo (ej. modo SRT seleccionado): fondo `#53645e`, texto `#92ba7b`.

---

## 5. Graficas y Visualizacion

- Fondo de area de grafica: `#3f484d` (fondo de subseccion resaltada).
- Lineas de datos: usar `#9cc2e4` como color principal.
- Lineas de referencia IWA / limites: usar `#e37272` (rojo alarma, trazo discontinuo).
- Ejes y grid: `#5e686c` con opacidad al 50%.
- Texto de ejes y leyendas: `#fafafa`.

---

## 6. Paleta Completa (Referencia Rapida)

```
Fondos (oscuro a claro):
  #1a2226  -- Fondo global de la aplicacion
  #2c3336  -- Fondo de inputs y campos
  #373f44  -- Cabeceras de contenedor
  #3f484d  -- Subseccion resaltada / fondo de graficas
  #444e54  -- Tarjeta / contenedor principal
  #5e686c  -- Menu activo / bordes de input

Datos y texto:
  #fafafa  -- Texto general y etiquetas
  #9cc2e4  -- Valores de medicion (azul datos)

Estados:
  #53645e / #92ba7b  -- Normal (fondo / texto)
  #6b6040 / #d4a843  -- Warning (fondo / texto)
  #63555a / #e37272  -- Alarma (fondo / texto)
```
