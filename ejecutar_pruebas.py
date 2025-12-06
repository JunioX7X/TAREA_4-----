"""
VERSIÓN 2
"""

import sys
import os
from typing import List, Dict
import time
from collections import defaultdict


class ResourceAllocationGraph:
    """Versión con soporte para recursos con cola"""

    def __init__(self):
        self.processes = set()
        self.resources = set()
        self.recursos_con_cola = set()
        self.solicita = defaultdict(list)
        self.asignado = {}
        self.cola_espera = defaultdict(list)
        self.tiempo_llegada = {}
        self.tiempo_inicio_espera = defaultdict(dict)
        self.tiempo_finalizacion = {}
        self.recursos_por_proceso = defaultdict(list)

    def agregar_recurso(self, recurso, usa_cola=False):
        self.resources.add(recurso)
        self.asignado[recurso] = None
        if usa_cola:
            self.recursos_con_cola.add(recurso)

    def agregar_proceso(self, proceso, tiempo):
        if proceso not in self.processes:
            self.processes.add(proceso)
            self.tiempo_llegada[proceso] = tiempo

    def solicitar_recurso(self, proceso, recurso, tiempo):
        self.agregar_proceso(proceso, tiempo)

        if recurso not in self.resources:
            return

        if self.asignado[recurso] is None:
            self.asignado[recurso] = proceso
            self.recursos_por_proceso[proceso].append(recurso)
        else:
            if recurso in self.recursos_con_cola:
                # Recurso con cola - NO crea dependencia
                self.cola_espera[recurso].append(proceso)
                self.tiempo_inicio_espera[proceso][recurso] = tiempo
            else:
                # Recurso normal - crea dependencia
                self.solicita[proceso].append(recurso)
                self.cola_espera[recurso].append(proceso)
                self.tiempo_inicio_espera[proceso][recurso] = tiempo

    def liberar_proceso(self, proceso, tiempo):
        if proceso not in self.processes:
            return

        self.tiempo_finalizacion[proceso] = tiempo

        recursos_liberados = []
        for recurso, proc_asignado in self.asignado.items():
            if proc_asignado == proceso:
                recursos_liberados.append(recurso)

        for recurso in recursos_liberados:
            self.asignado[recurso] = None

            if self.cola_espera[recurso]:
                siguiente_proceso = self.cola_espera[recurso].pop(0)

                # Solo remover de solicita si NO es recurso con cola
                if recurso not in self.recursos_con_cola:
                    if recurso in self.solicita[siguiente_proceso]:
                        self.solicita[siguiente_proceso].remove(recurso)

                self.asignado[recurso] = siguiente_proceso
                self.recursos_por_proceso[siguiente_proceso].append(recurso)

        self.processes.discard(proceso)
        if proceso in self.solicita:
            del self.solicita[proceso]

    def detectar_ciclo(self):
        grafo = defaultdict(list)

        # Solo considerar dependencias de recursos SIN cola
        for proceso, recursos_solicitados in self.solicita.items():
            for recurso in recursos_solicitados:
                # CRÍTICO: No crear dependencia si el recurso usa cola
                if recurso not in self.recursos_con_cola:
                    if self.asignado[recurso] and self.asignado[recurso] != proceso:
                        grafo[proceso].append(self.asignado[recurso])

        visitado = set()
        en_pila = set()

        def dfs(nodo, ruta):
            if nodo in en_pila:
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

        for proceso in list(grafo.keys()):
            if proceso not in visitado:
                hay_ciclo, ciclo = dfs(proceso, [])
                if hay_ciclo:
                    return True, ciclo

        return False, []

    def calcular_metricas(self):
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
            'procesos_bloqueados': len(self.processes),
            'recursos_con_cola': len(self.recursos_con_cola)
        }


def leer_archivo_configuracion(nombre_archivo):
    """Lee archivo con soporte para recursos con *"""
    acciones = []
    try:
        with open(nombre_archivo, 'r') as f:
            lineas = f.readlines()

            # Primera línea: recursos (pueden tener *)
            recursos_str = [r.strip() for r in lineas[0].strip().split(',')]
            recursos_parseados = []

            for recurso_str in recursos_str:
                usa_cola = recurso_str.startswith('*')
                nombre_recurso = recurso_str[1:] if usa_cola else recurso_str
                recursos_parseados.append((nombre_recurso, usa_cola))

            acciones.append(('recursos', recursos_parseados))

            for linea in lineas[1:]:
                linea = linea.strip()
                if not linea:
                    continue

                partes = [p.strip() for p in linea.split(',')]
                tiempo = int(partes[0])
                proceso = partes[1]

                if len(partes) == 2:
                    acciones.append(('terminar', tiempo, proceso))
                else:
                    recurso = partes[2]
                    acciones.append(('solicitar', tiempo, proceso, recurso))

        return acciones
    except:
        return []


def simular_silencioso(acciones):
    """Simula sin imprimir (para análisis rápido)"""
    grafo = ResourceAllocationGraph()

    if acciones[0][0] == 'recursos':
        recursos = acciones[0][1]
        for nombre_recurso, usa_cola in recursos:
            grafo.agregar_recurso(nombre_recurso, usa_cola)
        acciones = acciones[1:]

    deadlock_detectado = False
    ciclo_detectado = []

    for accion in acciones:
        tipo = accion[0]

        if tipo == 'solicitar':
            _, tiempo, proceso, recurso = accion
            grafo.solicitar_recurso(proceso, recurso, tiempo)

        elif tipo == 'terminar':
            _, tiempo, proceso = accion
            grafo.liberar_proceso(proceso, tiempo)

        hay_ciclo, ciclo = grafo.detectar_ciclo()
        if hay_ciclo and not deadlock_detectado:
            deadlock_detectado = True
            ciclo_detectado = ciclo

    metricas = grafo.calcular_metricas()
    metricas['deadlock'] = deadlock_detectado
    metricas['ciclo'] = ciclo_detectado

    return grafo, metricas


def ejecutar_suite_pruebas():
    """Ejecuta todos los escenarios y genera reporte comparativo"""

    escenarios = [
        ('escenario_1_original.txt', 'Original - Con Deadlock'),
        ('escenario_1_controlado.txt', 'Controlado - Sin Deadlock'),
        ('escenario_3_controlado.txt', '5 Procesos Controlado'),
        ('escenario_4_controlado.txt', 'Ciclo Completo Controlado'),
        ('escenario_5_controlado.txt', 'Alta Contención Controlada'),
        ('escenario_7_controlado.txt', 'Deadlock Parcial Controlado'),
        ('escenario_mixto.txt', 'Recursos Mixtos (* y normal)'),
        ('comparativo_con_control.txt', 'Comparativo CON *'),
        ('comparativo_sin_control.txt', 'Comparativo SIN *'),
    ]

    print("=" * 80)
    print(" " * 20 + "SUITE DE PRUEBAS - TAREA 4")
    print(" " * 18 + "Control de Interbloqueos")
    print("=" * 80)
    print()

    resultados = []

    for archivo, descripcion in escenarios:
        if not os.path.exists(archivo):
            print(f"⚠  Archivo {archivo} no encontrado. Saltando...")
            continue

        print(f" Ejecutando: {descripcion}")
        print(f"   Archivo: {archivo}")

        acciones = leer_archivo_configuracion(archivo)
        if not acciones:
            print(f"  ❌ Error al leer archivo\n")
            continue

        # Detectar si tiene recursos con cola
        if acciones[0][0] == 'recursos':
            recursos_info = acciones[0][1]
            tiene_cola = any(usa_cola for _, usa_cola in recursos_info)
            recursos_con_cola = [nombre for nombre, usa_cola in recursos_info if usa_cola]
        else:
            tiene_cola = False
            recursos_con_cola = []

        inicio = time.time()
        grafo, metricas = simular_silencioso(acciones)
        tiempo_ejecucion = (time.time() - inicio) * 1000  # en ms

        metricas['tiempo_ejecucion'] = tiempo_ejecucion
        metricas['descripcion'] = descripcion
        metricas['archivo'] = archivo
        metricas['tiene_control'] = tiene_cola
        metricas['recursos_cola_lista'] = recursos_con_cola

        resultados.append(metricas)

        # Resultado breve
        control_info = f"  CON CONTROL (*)" if tiene_cola else "⚠️  SIN CONTROL"
        estado = " DEADLOCK" if metricas['deadlock'] else "✅ SIN DEADLOCK"

        print(f"   {control_info}")
        if recursos_con_cola:
            print(f"   Recursos con cola: {recursos_con_cola}")
        print(f"   {estado}")
        print(f"   Completados: {metricas['procesos_completados']} | "
              f"Bloqueados: {metricas['procesos_bloqueados']} | "
              f"Tiempo: {tiempo_ejecucion:.2f}ms")
        print()

    # Generar reporte comparativo
    generar_reporte(resultados)


def generar_reporte(resultados):
    """Genera un reporte detallado de todos los resultados"""

    print("\n" + "=" * 80)
    print(" " * 25 + "REPORTE COMPARATIVO")
    print("=" * 80)
    print()

    # Tabla de resultados
    print(f"{'Escenario':<35} {'Control':<10} {'Deadlock':<10} {'Completados':<12} {'Bloqueados':<10}")
    print("-" * 80)

    for resultado in resultados:
        desc = resultado['descripcion'][:33]
        tiene_control = "✅ SÍ" if resultado['tiene_control'] else "❌ NO"
        deadlock = " SÍ" if resultado['deadlock'] else "✅ NO"
        completados = resultado['procesos_completados']
        bloqueados = resultado['procesos_bloqueados']

        print(f"{desc:<35} {tiene_control:<10} {deadlock:<10} {completados:<12} {bloqueados:<10}")

    print()
    print("=" * 80)
    print("ANÁLISIS ESTADÍSTICO")
    print("=" * 80)

    # Dividir resultados por control
    con_control = [r for r in resultados if r['tiene_control']]
    sin_control = [r for r in resultados if not r['tiene_control']]

    print(f"\n ESCENARIOS CON CONTROL (recursos con *):")
    print(f"   Total: {len(con_control)}")
    if con_control:
        deadlocks_con_control = sum(1 for r in con_control if r['deadlock'])
        print(f"   Con deadlock: {deadlocks_con_control}")
        print(f"   Sin deadlock: {len(con_control) - deadlocks_con_control}")
        avg_completados = sum(r['procesos_completados'] for r in con_control) / len(con_control)
        print(f"   Promedio procesos completados: {avg_completados:.2f}")

    print(f"\n ESCENARIOS SIN CONTROL:")
    print(f"   Total: {len(sin_control)}")
    if sin_control:
        deadlocks_sin_control = sum(1 for r in sin_control if r['deadlock'])
        print(f"   Con deadlock: {deadlocks_sin_control}")
        print(f"   Sin deadlock: {len(sin_control) - deadlocks_sin_control}")
        avg_completados = sum(r['procesos_completados'] for r in sin_control) / len(sin_control)
        print(f"   Promedio procesos completados: {avg_completados:.2f}")

    # Análisis de efectividad del control
    print("\n" + "=" * 80)
    print("EFECTIVIDAD DEL CONTROL DE INTERBLOQUEOS")
    print("=" * 80)

    if con_control and sin_control:
        tasa_deadlock_sin = sum(1 for r in sin_control if r['deadlock']) / len(sin_control) * 100
        tasa_deadlock_con = sum(1 for r in con_control if r['deadlock']) / len(con_control) * 100

        print(f"\n Tasa de deadlock SIN control: {tasa_deadlock_sin:.1f}%")
        print(f" Tasa de deadlock CON control: {tasa_deadlock_con:.1f}%")

        if tasa_deadlock_con < tasa_deadlock_sin:
            mejora = tasa_deadlock_sin - tasa_deadlock_con
            print(f"\n✅ MEJORA: {mejora:.1f}% menos deadlocks con control")

        # Comparar procesos completados
        avg_comp_sin = sum(r['procesos_completados'] for r in sin_control) / len(sin_control)
        avg_comp_con = sum(r['procesos_completados'] for r in con_control) / len(con_control)

        print(f"\n Procesos completados promedio:")
        print(f"   Sin control: {avg_comp_sin:.2f}")
        print(f"   Con control: {avg_comp_con:.2f}")

        if avg_comp_con > avg_comp_sin:
            mejora_proc = ((avg_comp_con - avg_comp_sin) / avg_comp_sin) * 100
            print(f"   ✅ Mejora: {mejora_proc:.1f}% más procesos completados")

    # Detalles de deadlocks
    print("\n" + "-" * 80)
    print("DETALLES DE DEADLOCKS DETECTADOS")
    print("-" * 80)

    deadlocks_encontrados = [r for r in resultados if r['deadlock']]
    if deadlocks_encontrados:
        for resultado in deadlocks_encontrados:
            control_str = "CON control (*)" if resultado['tiene_control'] else "SIN control"
            print(f"\n🔴 {resultado['descripcion']} - {control_str}")
            if resultado['ciclo']:
                ciclo_str = ' → '.join(resultado['ciclo'] + [resultado['ciclo'][0]])
                print(f"   Ciclo: {ciclo_str}")
            print(f"   Procesos bloqueados: {resultado['procesos_bloqueados']}")
    else:
        print("\n✅ ¡No se detectaron deadlocks en ningún escenario!")

    print("\n" + "=" * 80)
    print("✅ Suite de pruebas completada")
    print("=" * 80)


if __name__ == "__main__":
    print("\n INICIANDO SUITE DE PRUEBAS AUTOMATIZADA - TAREA 4\n")

    # Verificar archivos
    print("Verificando archivos de escenarios...")

    archivos_necesarios = [
        'escenario_1_original.txt',
        'escenario_1_controlado.txt',
        'escenario_3_controlado.txt',
        'escenario_4_controlado.txt',
        'escenario_5_controlado.txt',
        'escenario_7_controlado.txt',
        'escenario_mixto.txt',
        'comparativo_con_control.txt',
        'comparativo_sin_control.txt',
    ]

    archivos_faltantes = [f for f in archivos_necesarios if not os.path.exists(f)]

    if archivos_faltantes:
        print("\n⚠️  Faltan los siguientes archivos:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print("\nEjecuta primero el generador de escenarios:")
        print("   python generar_escenarios_v2.py")
        sys.exit(1)

    print("✅ Todos los archivos encontrados\n")

    # Ejecutar suite
    ejecutar_suite_pruebas()

