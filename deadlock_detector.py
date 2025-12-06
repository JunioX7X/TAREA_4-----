import sys
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple
import time as time_module


class ResourceAllocationGraph:
    """
    Grafo de Asignación de Recursos para detectar deadlocks
    VERSIÓN 2: Con soporte para recursos con cola (marcados con *)
    """

    def __init__(self):
        # Nodos del grafo
        self.processes: Set[str] = set()
        self.resources: Set[str] = set()

        # NUEVO: Recursos que usan cola (marcados con *)
        self.recursos_con_cola: Set[str] = set()

        # Aristas del grafo
        self.solicita: Dict[str, List[str]] = defaultdict(list)
        self.asignado: Dict[str, str] = {}

        # Cola de espera por recurso
        self.cola_espera: Dict[str, List[str]] = defaultdict(list)

        # Métricas
        self.tiempo_llegada: Dict[str, int] = {}
        self.tiempo_inicio_espera: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.tiempo_finalizacion: Dict[str, int] = {}
        self.recursos_por_proceso: Dict[str, List[str]] = defaultdict(list)

    def agregar_recurso(self, recurso: str, usa_cola: bool = False):
        """
        Agrega un recurso al sistema

        Args:
            recurso: Nombre del recurso
            usa_cola: Si True, el recurso usa cola (no genera dependencias cíclicas)
        """
        self.resources.add(recurso)
        self.asignado[recurso] = None

        if usa_cola:
            self.recursos_con_cola.add(recurso)
            print(f"  ✓ Recurso {recurso} agregado (CON COLA - sin ciclos)")
        else:
            print(f"  ✓ Recurso {recurso} agregado (normal)")

    def agregar_proceso(self, proceso: str, tiempo: int):
        """Agrega un nuevo proceso al sistema"""
        if proceso not in self.processes:
            self.processes.add(proceso)
            self.tiempo_llegada[proceso] = tiempo
            print(f"  ✓ Proceso {proceso} llega al sistema")

    def solicitar_recurso(self, proceso: str, recurso: str, tiempo: int):
        """Un proceso solicita un recurso"""
        self.agregar_proceso(proceso, tiempo)

        if recurso not in self.resources:
            print(f"  ✗ ERROR: Recurso {recurso} no existe")
            return

        # Si el recurso está libre, asignarlo
        if self.asignado[recurso] is None:
            self.asignado[recurso] = proceso
            self.recursos_por_proceso[proceso].append(recurso)
            print(f"  ✓ Recurso {recurso} asignado a {proceso}")
        else:
            # El recurso está ocupado
            if recurso in self.recursos_con_cola:
                # NUEVO: Recurso con cola - NO crea dependencia cíclica
                self.cola_espera[recurso].append(proceso)
                self.tiempo_inicio_espera[proceso][recurso] = tiempo
                print(f"   Proceso {proceso} entra a COLA de {recurso} (ocupado por {self.asignado[recurso]})")
                print(f"     → NO se crea dependencia cíclica (recurso con *)")
            else:
                # Recurso normal - crea dependencia
                self.solicita[proceso].append(recurso)
                self.cola_espera[recurso].append(proceso)
                self.tiempo_inicio_espera[proceso][recurso] = tiempo
                print(f"   Proceso {proceso} espera por {recurso} (ocupado por {self.asignado[recurso]})")
                print(f"     → Se crea dependencia: {proceso} → {recurso} → {self.asignado[recurso]}")

    def liberar_proceso(self, proceso: str, tiempo: int):
        """Un proceso termina y libera todos sus recursos"""
        if proceso not in self.processes:
            print(f"  ✗ ERROR: Proceso {proceso} no existe")
            return

        self.tiempo_finalizacion[proceso] = tiempo

        # Liberar todos los recursos asignados a este proceso
        recursos_liberados = []
        for recurso, proc_asignado in self.asignado.items():
            if proc_asignado == proceso:
                recursos_liberados.append(recurso)

        print(f"  ✓ Proceso {proceso} termina y libera recursos: {recursos_liberados}")

        for recurso in recursos_liberados:
            self.asignado[recurso] = None

            # Asignar recurso al siguiente proceso en cola
            if self.cola_espera[recurso]:
                siguiente_proceso = self.cola_espera[recurso].pop(0)
                self.asignado[recurso] = siguiente_proceso

                # Remover de solicita solo si el recurso NO usa cola
                if recurso not in self.recursos_con_cola:
                    if recurso in self.solicita[siguiente_proceso]:
                        self.solicita[siguiente_proceso].remove(recurso)

                self.recursos_por_proceso[siguiente_proceso].append(recurso)
                print(f"    → Recurso {recurso} ahora asignado a {siguiente_proceso}")

        # Eliminar proceso del grafo
        self.processes.discard(proceso)
        if proceso in self.solicita:
            del self.solicita[proceso]

    def detectar_ciclo(self) -> Tuple[bool, List[str]]:
        """
        Detecta si existe un ciclo en el grafo (deadlock)
        MODIFICADO: Solo considera dependencias de recursos SIN cola
        """
        # Construir grafo de dependencias entre procesos
        grafo = defaultdict(list)

        # Para cada proceso que solicita un recurso
        for proceso, recursos_solicitados in self.solicita.items():
            for recurso in recursos_solicitados:
                # IMPORTANTE: Solo crear dependencia si el recurso NO usa cola
                if recurso not in self.recursos_con_cola:
                    # Si el recurso está asignado a otro proceso
                    if self.asignado[recurso] and self.asignado[recurso] != proceso:
                        # Crear arista: proceso → proceso_que_tiene_recurso
                        grafo[proceso].append(self.asignado[recurso])

        # DFS para detectar ciclo
        visitado = set()
        en_pila = set()

        def dfs(nodo, ruta):
            if nodo in en_pila:
                # Encontramos un ciclo
                idx = ruta.index(nodo)
                return True, ruta[idx:]

            if nodo in visitado:
                return False, []

            visitado.add(nodo)
            en_pila.add(nodo)
            ruta.append(nodo)

            for vecino in grafo[nodo]:
                hay_ciclo, ciclo = dfs(vecino, ruta[:])
                if hay_ciclo:
                    return True, ciclo

            en_pila.remove(nodo)
            return False, []

        # Revisar todos los nodos
        for proceso in list(grafo.keys()):
            if proceso not in visitado:
                hay_ciclo, ciclo = dfs(proceso, [])
                if hay_ciclo:
                    return True, ciclo

        return False, []

    def imprimir_estado(self):
        """Imprime el estado actual del sistema"""
        print("\n  📊 Estado actual del sistema:")
        print(f"  Procesos activos: {sorted(self.processes)}")
        print(f"  Recursos asignados:")
        for recurso in sorted(self.resources):
            marca_cola = "(*)" if recurso in self.recursos_con_cola else ""
            if self.asignado[recurso]:
                print(f"    {recurso}{marca_cola} → {self.asignado[recurso]}")
            else:
                print(f"    {recurso}{marca_cola} → (libre)")

        if self.solicita:
            print(f"  Procesos esperando (con dependencia):")
            for proceso, recursos in self.solicita.items():
                print(f"    {proceso} espera: {recursos}")

        # Mostrar colas de espera
        colas_activas = {r: cola for r, cola in self.cola_espera.items() if cola}
        if colas_activas:
            print(f"  Colas de espera:")
            for recurso, cola in colas_activas.items():
                marca_cola = "(*)" if recurso in self.recursos_con_cola else ""
                print(f"    {recurso}{marca_cola}: {cola}")

    def calcular_metricas(self):
        """Calcula métricas de rendimiento"""
        completados = len(self.tiempo_finalizacion)

        tiempos_espera = []
        for proceso, recursos_dict in self.tiempo_inicio_espera.items():
            if proceso in self.tiempo_finalizacion:
                for recurso, tiempo_inicio in recursos_dict.items():
                    tiempo_fin_espera = self.tiempo_finalizacion[proceso]
                    tiempo_espera = tiempo_fin_espera - tiempo_inicio
                    tiempos_espera.append(tiempo_espera)

        tiempo_espera_promedio = sum(tiempos_espera) / len(tiempos_espera) if tiempos_espera else 0

        turnaround_times = []
        for proceso, tiempo_fin in self.tiempo_finalizacion.items():
            if proceso in self.tiempo_llegada:
                turnaround = tiempo_fin - self.tiempo_llegada[proceso]
                turnaround_times.append(turnaround)

        turnaround_promedio = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0

        return {
            'procesos_completados': completados,
            'tiempo_espera_promedio': tiempo_espera_promedio,
            'turnaround_promedio': turnaround_promedio,
            'procesos_bloqueados': len(self.processes)
        }


def leer_archivo_configuracion(nombre_archivo: str) -> List[Tuple]:
    """
    Lee el archivo de configuración y retorna las acciones
    MODIFICADO: Detecta recursos con * (usa cola)
    """
    acciones = []

    try:
        with open(nombre_archivo, 'r') as f:
            lineas = f.readlines()

            # Primera línea: recursos (pueden tener * al inicio)
            recursos_str = [r.strip() for r in lineas[0].strip().split(',')]
            recursos_parseados = []

            for recurso_str in recursos_str:
                usa_cola = recurso_str.startswith('*')
                nombre_recurso = recurso_str[1:] if usa_cola else recurso_str
                recursos_parseados.append((nombre_recurso, usa_cola))

            acciones.append(('recursos', recursos_parseados))

            # Resto de líneas: acciones
            for linea in lineas[1:]:
                linea = linea.strip()
                if not linea:
                    continue

                partes = [p.strip() for p in linea.split(',')]
                tiempo = int(partes[0])
                proceso = partes[1]

                if len(partes) == 2:
                    # Proceso termina
                    acciones.append(('terminar', tiempo, proceso))
                else:
                    # Proceso solicita recurso
                    recurso = partes[2]
                    acciones.append(('solicitar', tiempo, proceso, recurso))

        return acciones

    except FileNotFoundError:
        print(f"ERROR: Archivo '{nombre_archivo}' no encontrado")
        return []
    except Exception as e:
        print(f"ERROR al leer archivo: {e}")
        return []


def simular_sistema(acciones: List[Tuple]):
    """Simula el sistema de asignación de recursos"""
    print("=" * 70)
    print("SIMULACIÓN DE SISTEMA CON CONTROL DE INTERBLOQUEOS")
    print("=" * 70)

    grafo = ResourceAllocationGraph()

    # Procesar primera acción (recursos)
    if acciones[0][0] == 'recursos':
        recursos = acciones[0][1]
        print(f"\n🔧 Configurando recursos del sistema:")
        for nombre_recurso, usa_cola in recursos:
            grafo.agregar_recurso(nombre_recurso, usa_cola)
        acciones = acciones[1:]

    # Simular acciones paso a paso
    for accion in acciones:
        tipo = accion[0]

        if tipo == 'solicitar':
            _, tiempo, proceso, recurso = accion
            print(f"\n⏰ Tiempo {tiempo}: Proceso {proceso} solicita {recurso}")
            grafo.solicitar_recurso(proceso, recurso, tiempo)

        elif tipo == 'terminar':
            _, tiempo, proceso = accion
            print(f"\n⏰ Tiempo {tiempo}: Proceso {proceso} termina")
            grafo.liberar_proceso(proceso, tiempo)

        # Detectar deadlock después de cada acción
        hay_ciclo, ciclo = grafo.detectar_ciclo()
        if hay_ciclo:
            print(f"\n   ¡DEADLOCK DETECTADO! ")
            print(f"  Ciclo encontrado: {' → '.join(ciclo + [ciclo[0]])}")
        else:
            print(f"\n  ✅ No hay deadlock")

        # Mostrar estado
        grafo.imprimir_estado()

    # Métricas finales
    print("\n" + "=" * 70)
    print("MÉTRICAS FINALES")
    print("=" * 70)
    metricas = grafo.calcular_metricas()
    print(f"Procesos completados: {metricas['procesos_completados']}")
    print(f"Procesos bloqueados: {metricas['procesos_bloqueados']}")
    print(f"Tiempo de espera promedio: {metricas['tiempo_espera_promedio']:.2f}")
    print(f"Turnaround time promedio: {metricas['turnaround_promedio']:.2f}")

    return grafo, metricas


# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    print("TAREA PROGRAMADA 4 - SISTEMAS OPERATIVOS")
    print("Control de Interbloqueos con Recursos de Cola\n")

    # Ejemplo con recurso que usa cola (*)
    print("Creando ejemplo con recurso de cola (*)...")
    with open('ejemplo_con_cola.txt', 'w') as f:
        f.write("""*r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
10,p1
11,p2
12,p3""")

    acciones = leer_archivo_configuracion('ejemplo_con_cola.txt')
    if acciones:
        grafo1, metricas1 = simular_sistema(acciones)

    print("\n\n" + "=" * 70)
    print("COMPARACIÓN: Mismo escenario SIN recurso de cola")
    print("=" * 70)

    with open('ejemplo_sin_cola.txt', 'w') as f:
        f.write("""r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
10,p1""")

    acciones2 = leer_archivo_configuracion('ejemplo_sin_cola.txt')
    if acciones2:
        grafo2, metricas2 = simular_sistema(acciones2)

    print("\n\n✅ Simulación completada")
    print("\nArchivos generados:")
    print("  - ejemplo_con_cola.txt (CON *)")
    print("  - ejemplo_sin_cola.txt (SIN *)")