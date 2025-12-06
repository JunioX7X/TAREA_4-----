
def generar_escenario_1_controlado():
    """Escenario 1 CONTROLADO: El recurso r1 ahora tiene * (usa cola)"""
    with open('escenario_1_controlado.txt', 'w') as f:
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
    print("✓ Escenario 1 CONTROLADO creado: escenario_1_controlado.txt")
    print("  Descripción: r1 con * rompe el ciclo P1→R2→P2→R3→P3→R1→P1")
    print("  Resultado: SIN deadlock, todos los procesos terminan")


def generar_escenario_1_original():
    """Escenario 1 ORIGINAL: Sin control (para comparación)"""
    with open('escenario_1_original.txt', 'w') as f:
        f.write("""r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
10,p1""")
    print("✓ Escenario 1 ORIGINAL creado: escenario_1_original.txt")
    print("  Descripción: Sin *, genera deadlock en tiempo 5")


def generar_escenario_3_controlado():
    """Escenario 3 CONTROLADO: Ambos recursos con * (sin deadlock)"""
    with open('escenario_3_controlado.txt', 'w') as f:
        f.write("""*r1,*r2
0,p1,r1
1,p2,r2
2,p3,r1
3,p4,r2
4,p5,r1
5,p1,r2
6,p2,r1
7,p3,r2
8,p4,r1
9,p5,r2
15,p1
20,p2
25,p3
30,p4
35,p5""")
    print("✓ Escenario 3 CONTROLADO creado: escenario_3_controlado.txt")
    print("  Descripción: r1 y r2 con * - 5 procesos completan sin deadlock")


def generar_escenario_4_controlado():
    """Escenario 4 CONTROLADO: r1 con * rompe el ciclo completo"""
    with open('escenario_4_controlado.txt', 'w') as f:
        f.write("""*r1,r2,r3,r4
0,p1,r1
1,p2,r2
2,p3,r3
3,p4,r4
4,p1,r2
5,p2,r3
6,p3,r4
7,p4,r1
12,p1
13,p2
14,p3
15,p4""")
    print("✓ Escenario 4 CONTROLADO creado: escenario_4_controlado.txt")
    print("  Descripción: r1 con * rompe ciclo P1→P2→P3→P4→P1")


def generar_escenario_5_controlado():
    """Escenario 5 CONTROLADO: Alta contención pero sin deadlock"""
    with open('escenario_5_controlado.txt', 'w') as f:
        contenido = "*r1,*r2\n"
        # 8 procesos compitiendo por 2 recursos CON cola
        for i in range(1, 9):
            tiempo = i - 1
            recurso = 'r1' if i % 2 == 1 else 'r2'
            contenido += f"{tiempo},p{i},{recurso}\n"

        # Segunda ronda de solicitudes
        for i in range(1, 9):
            tiempo = i + 7
            recurso = 'r2' if i % 2 == 1 else 'r1'
            contenido += f"{tiempo},p{i},{recurso}\n"

        # Todos terminan
        for i in range(1, 9):
            tiempo = 20 + i * 2
            contenido += f"{tiempo},p{i}\n"

        f.write(contenido)
    print("✓ Escenario 5 CONTROLADO creado: escenario_5_controlado.txt")
    print("  Descripción: 8 procesos, recursos con * - todos completan")


def generar_escenario_7_controlado():
    """Escenario 7 CONTROLADO: Deadlock parcial eliminado"""
    with open('escenario_7_controlado.txt', 'w') as f:
        f.write("""*r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p4,r3
4,p1,r2
5,p2,r1
8,p3
10,p4
12,p1
14,p2""")
    print("✓ Escenario 7 CONTROLADO creado: escenario_7_controlado.txt")
    print("  Descripción: r1 con * evita deadlock entre P1 y P2")


def generar_escenario_mixto():
    """Escenario MIXTO: Algunos recursos con *, otros sin *"""
    with open('escenario_mixto.txt', 'w') as f:
        f.write("""*r1,r2,r3,r4
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r4
6,p1,r4
10,p1
11,p2
12,p3""")
    print("✓ Escenario MIXTO creado: escenario_mixto.txt")
    print("  Descripción: Solo r1 con *, otros recursos normales")


def generar_escenario_comparativo():
    """Genera dos versiones del mismo escenario: con y sin control"""

    # Versión CON control (*)
    with open('comparativo_con_control.txt', 'w') as f:
        f.write("""*r1,*r2,*r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
6,p1,r3
7,p2,r1
8,p3,r2
15,p1
16,p2
17,p3""")

    # Versión SIN control
    with open('comparativo_sin_control.txt', 'w') as f:
        f.write("""r1,r2,r3
0,p1,r1
1,p2,r2
2,p3,r3
3,p1,r2
4,p2,r3
5,p3,r1
6,p1,r3
7,p2,r1
8,p3,r2
15,p1""")

    print("✓ Escenarios COMPARATIVOS creados:")
    print("  - comparativo_con_control.txt (CON *)")
    print("  - comparativo_sin_control.txt (SIN *)")


def generar_todos_escenarios():
    """Genera todos los escenarios de prueba para Tarea 4"""
    print("=" * 70)
    print("GENERANDO ESCENARIOS PARA TAREA 4 (CON CONTROL)")
    print("=" * 70)
    print()

    print("📝 Generando escenarios controlados...")
    print()
    generar_escenario_1_controlado()
    print()
    generar_escenario_1_original()
    print()
    generar_escenario_3_controlado()
    print()
    generar_escenario_4_controlado()
    print()
    generar_escenario_5_controlado()
    print()
    generar_escenario_7_controlado()
    print()
    generar_escenario_mixto()
    print()
    generar_escenario_comparativo()

    print()
    print("=" * 70)
    print("✅ Todos los escenarios han sido generados")
    print("=" * 70)
    print("\nArchivos creados:")
    print("\n ESCENARIOS CONTROLADOS (con *):")
    print("  1. escenario_1_controlado.txt - Deadlock original RESUELTO con *")
    print("  2. escenario_3_controlado.txt - 5 procesos sin deadlock")
    print("  3. escenario_4_controlado.txt - Ciclo completo RESUELTO")
    print("  4. escenario_5_controlado.txt - Alta contención RESUELTA")
    print("  5. escenario_7_controlado.txt - Deadlock parcial RESUELTO")
    print("  6. escenario_mixto.txt - Mezcla de recursos con/sin *")

    print("\n🔴 ESCENARIOS ORIGINALES (sin control):")
    print("  7. escenario_1_original.txt - Para comparar con controlado")

    print("\n ESCENARIOS COMPARATIVOS:")
    print("  8. comparativo_con_control.txt - Versión con *")
    print("  9. comparativo_sin_control.txt - Versión sin *")


if __name__ == "__main__":
    generar_todos_escenarios()

    print("\n" + "=" * 70)
    print("EXPLICACIÓN DEL MECANISMO DE CONTROL")
    print("=" * 70)
    print()
    print("¿Qué hace el * (asterisco)?")
    print("─" * 70)
    print()
    print("RECURSO NORMAL (sin *):")
    print("  • Crea dependencias: P1 → R1 → P2")
    print("  • Puede formar ciclos: P1→R2→P2→R3→P3→R1→P1 ❌ DEADLOCK")
    print()
    print("RECURSO CON * (con cola):")
    print("  • NO crea dependencias entre procesos")
    print("  • Los procesos entran a una COLA ordenada")
    print("  • Ejemplo: P1 → COLA(R1) [no crea P1→R1→P3]")
    print("  • Resultado: ✅ SIN DEADLOCK")
    print()
    print("─" * 70)
    print("EJEMPLO PRÁCTICO:")
    print("─" * 70)
    print()
    print("SIN CONTROL (r1,r2,r3):")
    print("  Tiempo 0: P1 toma r1")
    print("  Tiempo 1: P2 toma r2")
    print("  Tiempo 2: P3 toma r3")
    print("  Tiempo 3: P1 espera r2 (P1→r2→P2)")
    print("  Tiempo 4: P2 espera r3 (P2→r3→P3)")
    print("  Tiempo 5: P3 espera r1 (P3→r1→P1)")
    print("    CICLO: P1→P2→P3→P1 = DEADLOCK")
    print()
    print("CON CONTROL (*r1,r2,r3):")
    print("  Tiempo 0: P1 toma r1")
    print("  Tiempo 1: P2 toma r2")
    print("  Tiempo 2: P3 toma r3")
    print("  Tiempo 3: P1 espera r2 (P1→r2→P2)")
    print("  Tiempo 4: P2 espera r3 (P2→r3→P3)")
    print("  Tiempo 5: P3 entra a COLA(r1) - NO crea P3→r1→P1")
    print("  ✅ NO HAY CICLO - P1 eventualmente termina y libera r1 para P3")
    print()
    print("─" * 70)
    print()
    print(" CONCLUSIÓN:")
    print("El * rompe los ciclos al convertir dependencias en colas FIFO,")
    print("garantizando que eventualmente todos los procesos obtendrán")
    print("sus recursos y completarán su ejecución.")
    print()
    print("=" * 70)
    print()
    print("  SIGUIENTE PASO:")
    print("Ejecuta: python deadlock_detector_v2.py")
    print("Para ver la simulación con control de interbloqueos")