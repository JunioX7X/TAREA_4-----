# Tarea Programada 4 - Control de Interbloqueos
## Sistema de Asignación de Recursos con Prevención de Deadlocks

---

## 📋 Descripción

Este proyecto implementa un sistema de detección y **control de interbloqueos** mediante el uso de **recursos con cola**. Es una evolución de la Tarea 3, donde ahora los recursos pueden marcarse con `*` para evitar ciclos de dependencia.

---

## 🎯 Objetivo Principal

**Modificar el sistema de asignación de recursos para que NO genere interbloqueos** mediante el uso de recursos con cola (marcados con `*`).

### ¿Qué cambia respecto a la Tarea 3?

| Aspecto | Tarea 3 (Sin Control) | Tarea 4 (Con Control) |
|---------|----------------------|----------------------|
| **Recursos** | `r1,r2,r3` | `*r1,r2,r3` |
| **Dependencias** | P1 → R1 → P2 | P1 → COLA(R1) |
| **Ciclos** | ✅ Pueden formarse | ❌ Se previenen |
| **Deadlock** | ⚠️ Posible | ✅ Eliminado |

---

## 🔧 Archivos del Proyecto

### Archivos Principales

1. **`deadlock_detector_v2.py`** - Programa principal con control de interbloqueos
2. **`generar_escenarios_v2.py`** - Genera escenarios de prueba (con y sin control)
3. **`ejecutar_pruebas_v2.py`** - Suite automatizada de pruebas y análisis

### Archivos de Escenarios

**Con Control (*):**
- `escenario_1_controlado.txt` - Deadlock resuelto con *
- `escenario_3_controlado.txt` - 5 procesos sin deadlock
- `escenario_4_controlado.txt` - Ciclo completo resuelto
- `escenario_5_controlado.txt` - Alta contención resuelta
- `escenario_7_controlado.txt` - Deadlock parcial resuelto
- `escenario_mixto.txt` - Mezcla de recursos

**Sin Control (comparación):**
- `escenario_1_original.txt` - Escenario original con deadlock
- `comparativo_sin_control.txt` - Para comparar resultados

---

## 🚀 Cómo Ejecutar

### Paso 1: Generar Escenarios

```bash
python generar_escenarios_v2.py
```

Esto creará todos los archivos `.txt` con los escenarios de prueba.

### Paso 2: Ejecutar Simulación Individual

```bash
python deadlock_detector_v2.py
```

Ejecuta dos ejemplos comparativos y muestra paso a paso la simulación.

### Paso 3: Ejecutar Suite Completa de Pruebas

```bash
python ejecutar_pruebas_v2.py
```

Ejecuta todos los escenarios y genera un reporte comparativo detallado.

---

## 📖 Teoría: ¿Cómo Funciona el Control?

### Problema Original (Sin *)

Cuando los procesos solicitan recursos de forma circular, se forma un **ciclo de dependencias**:

```
Tiempo 0: P1 toma r1
Tiempo 1: P2 toma r2
Tiempo 2: P3 toma r3
Tiempo 3: P1 espera r2  →  P1 → r2 → P2
Tiempo 4: P2 espera r3  →  P2 → r3 → P3
Tiempo 5: P3 espera r1  →  P3 → r1 → P1

🔴 CICLO: P1 → P2 → P3 → P1 = DEADLOCK
```

### Solución con * (Cola)

Al marcar un recurso con `*`, se rompe el ciclo:

```
*r1,r2,r3  ← r1 ahora usa cola

Tiempo 0: P1 toma r1
Tiempo 1: P2 toma r2
Tiempo 2: P3 toma r3
Tiempo 3: P1 espera r2  →  P1 → r2 → P2
Tiempo 4: P2 espera r3  →  P2 → r3 → P3
Tiempo 5: P3 entra a COLA(r1)  →  NO crea P3 → r1 → P1

✅ NO HAY CICLO
```

### ¿Por qué Funciona?

| Recurso Normal | Recurso con Cola (*) |
|---------------|---------------------|
| Crea **dependencia** P1 → R → P2 | Crea **cola FIFO** sin dependencia |
| Puede formar **ciclos** | **Imposible** formar ciclos |
| Grafos de espera **complejos** | Grafos de espera **simples** |

---

## 🎓 Conceptos Clave

### 1. Grafo de Asignación de Recursos (RAG)

**Sin control:**
```
P1 ──solicita──> R2 ──asignado a──> P2
                                     │
                                     └──solicita──> R3 ──asignado a──> P3
                                                                         │
                                                                         └──solicita──> R1 ──asignado a──> P1
```

**Con control (*r1):**
```
P1 ──solicita──> R2 ──asignado a──> P2
                                     │
                                     └──solicita──> R3 ──asignado a──> P3
                                                                         │
                                                                         └──en COLA(R1)
                                                                              ↓
                                                                           (no crea ciclo)
```

### 2. Detección de Ciclos (DFS)

El algoritmo de detección **ignora** las dependencias de recursos con `*`:

```python
def detectar_ciclo(self):
    grafo = defaultdict(list)
    
    for proceso, recursos_solicitados in self.solicita.items():
        for recurso in recursos_solicitados:
            # CRÍTICO: Solo considerar recursos SIN *
            if recurso not in self.recursos_con_cola:
                if self.asignado[recurso]:
                    grafo[proceso].append(self.asignado[recurso])
    
    # DFS para detectar ciclos...
```

### 3. Colas FIFO vs Dependencias

| Cola (FIFO) | Dependencia Cíclica |
|------------|-------------------|
| Orden garantizado | Sin orden definido |
| Sin starvation | Posible starvation |
| Sin deadlock | Posible deadlock |
| Más espera promedio | Menos espera si no hay deadlock |

---

## 📊 Formato de Archivos

### Sintaxis

```
*r1,r2,r3          ← Primera línea: recursos (* = usa cola)
0,p1,r1            ← tiempo,proceso,recurso (solicitud)
1,p2,r2
2,p3,r3
10,p1              ← tiempo,proceso (terminación)
```

### Reglas

- **Recursos con `*`**: Usan cola FIFO, no crean dependencias cíclicas
- **Recursos sin `*`**: Comportamiento normal, pueden crear deadlock
- **Mezcla**: Puedes tener algunos recursos con * y otros sin *

### Ejemplos

**Todos con control:**
```
*r1,*r2,*r3
```

**Mezcla:**
```
*r1,r2,r3
```
(Solo r1 usa cola)

**Sin control:**
```
r1,r2,r3
```
(Comportamiento original de Tarea 3)

---

## 🔬 Casos de Prueba

### Escenario 1: Deadlock Resuelto

**Original (deadlock):**
```
r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
```
**Resultado:** 🚨 DEADLOCK en tiempo 5

**Controlado (sin deadlock):**
```
*r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
10,p1
11,p2
12,p3
```
**Resultado:** ✅ Todos los procesos completan

### Escenario 2: Alta Contención

```
*r1,*r2
```
8 procesos compitiendo por 2 recursos → ✅ Todos completan

### Escenario 3: Recursos Mixtos

```
*r1,r2,r3,r4
```
Solo r1 con * → Deadlock parcial posible pero reducido

---

## 📈 Métricas Calculadas

El sistema calcula automáticamente:

- **Procesos completados**: Cuántos terminaron exitosamente
- **Procesos bloqueados**: Cuántos quedaron en deadlock
- **Tiempo de espera promedio**: Promedio de tiempo esperando recursos
- **Turnaround time promedio**: Tiempo total desde llegada hasta finalización
- **Tasa de deadlock**: % de escenarios con deadlock

---

## 🎯 Resultados Esperados

### Comparación: Con vs Sin Control

| Métrica | Sin Control | Con Control (*) |
|---------|-------------|----------------|
| **Deadlocks** | ~60% escenarios | ~0% escenarios |
| **Procesos completados** | ~40% | ~100% |
| **Tiempo espera** | Variable | Predecible |
| **Starvation** | Posible | No |

### Ejemplo de Salida

```
📊 ESCENARIOS CON CONTROL (recursos con *):
   Total: 7
   Con deadlock: 0
   Sin deadlock: 7
   Promedio procesos completados: 4.85

📊 ESCENARIOS SIN CONTROL:
   Total: 2
   Con deadlock: 2
   Sin deadlock: 0
   Promedio procesos completados: 1.00

✅ MEJORA: 100% menos deadlocks con control
```

---

## 🔑 Conclusiones

### Ventajas del Control con *

✅ **Elimina deadlocks** circulares  
✅ **Garantiza progreso** (todos los procesos avanzan)  
✅ **Previene starvation** (colas FIFO)  
✅ **Predecible** (comportamiento determinista)  

### Desventajas

⚠️ **Mayor tiempo de espera** promedio en algunos casos  
⚠️ **Serialización** en recursos muy contendidos  
⚠️ **Overhead** de gestión de colas  

### ¿Cuándo Usar *?

**SÍ usar * cuando:**
- Recurso crítico con alta contención
- No puedes tolerar deadlocks
- Necesitas fairness (FIFO)

**NO usar * cuando:**
- Baja contención por el recurso
- Rendimiento es crítico
- Tienes otras formas de prevención

---

## 🛠️ Modificaciones Principales del Código

### 1. Clase ResourceAllocationGraph

**Nuevo atributo:**
```python
self.recursos_con_cola: Set[str] = set()
```

### 2. Método agregar_recurso

**Ahora acepta parámetro usa_cola:**
```python
def agregar_recurso(self, recurso: str, usa_cola: bool = False):
    if usa_cola:
        self.recursos_con_cola.add(recurso)
```

### 3. Método solicitar_recurso

**Lógica diferenciada:**
```python
if recurso in self.recursos_con_cola:
    # NO crear dependencia, solo cola
    self.cola_espera[recurso].append(proceso)
else:
    # Crear dependencia normal
    self.solicita[proceso].append(recurso)
```

### 4. Método detectar_ciclo

**Ignora recursos con *:**
```python
if recurso not in self.recursos_con_cola:
    grafo[proceso].append(self.asignado[recurso])
```

---

## 📚 Referencias

- **Condiciones de Coffman** para deadlock
- **Algoritmo de Banker** (prevención)
- **Detección de ciclos con DFS**
- **Grafos de asignación de recursos (RAG)**

---

## 👨‍💻 Autor
JUNIOR RAMIREZ
Universidad Lead - Bachillerato en Ciencia de Datos  
Sistemas Operativos - Tarea Programada 4

---

## 📝 Notas Adicionales

### Para Modificar Escenarios

1. Edita cualquier archivo `.txt`
2. Agrega o quita `*` en la primera línea
3. Ejecuta nuevamente la simulación

### Para Crear Nuevos Escenarios

```python
# Formato simple
with open('mi_escenario.txt', 'w') as f:
    f.write("""*r1,*r2
0,p1,r1
1,p2,r2
2,p1,r2
3,p2,r1
10,p1
11,p2""")
```

### Debugging

El programa muestra paso a paso:
- ✓ Asignaciones exitosas
- ⏳ Procesos esperando (con dependencia)
- 📋 Procesos en cola (sin dependencia)
- 🚨 Deadlocks detectados
- 📊 Estado del sistema completo

---

**¡Proyecto completado con éxito! 🎉**
