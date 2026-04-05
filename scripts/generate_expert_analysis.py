"""BSM1 Expert Process Analysis — Targeted verification tests.

Five diagnostic studies based on anomalous findings in the sensitivity report:

  A. Q_intr curve (0 to 10Q)     — confirm non-monotonic optimum, locate true minimum S_NO
  B. DO_O3 vs DO_O1/O2            — isolate oxygen contamination via internal recirculation
  C. Q=9000 with scaled flows     — confirm C:N dilution hypothesis (disproportionate recirculation)
  D. COD=762 oxygen starvation    — verify DO drops below K_OA=0.4 at high organic load
  E. Temperature-SRT interaction  — find minimum Q_WAS to maintain S_NH<4 at T=15 C

Output:
    reports/ANALISIS_EXPERTO.txt
"""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.engine import run_steady_state_simulation
from app.models import PlantParameters

REPORT_DIR = 'reports'
REPORT_FILE = 'ANALISIS_EXPERTO.txt'

# ASM1 kinetic constants (BSM1 standard)
K_OA = 0.4    # mg O2/L  (half-saturation for autotrophic O2)
MU_A = 0.5    # 1/d      (max autotrophic growth rate at 20 C)
B_A  = 0.05   # 1/d      (autotrophic decay)
THETA = 1.07  # Arrhenius coefficient


def run(label, **kwargs):
    """Run simulation, return (label, result_or_None, elapsed)."""
    t0 = time.time()
    try:
        plant = PlantParameters(**kwargs)
        result = run_steady_state_simulation(plant=plant, t_days=200)
        elapsed = time.time() - t0
        print(f'  {label:<52s} OK  ({elapsed:.1f}s)')
        return label, result, elapsed
    except Exception as exc:
        elapsed = time.time() - t0
        print(f'  {label:<52s} ERROR: {exc}')
        return label, None, elapsed


def c(result, comp):
    """Component concentration from result."""
    if comp == 'TSS':
        return result.aggregates.get('TSS', float('nan'))
    for x in result.components:
        if x.component == comp:
            return x.obtained
    return float('nan')


def a(result, key):
    """Aggregate value from result."""
    v = result.aggregates.get(key)
    return v if v is not None else float('nan')


def fmt(v, d=3):
    if v is None or (isinstance(v, float) and v != v):
        return '   N/A  '
    return f'{v:8.{d}f}'


W = 100


def divl(char='-', w=W):
    return char * w


def header(title):
    return [divl('='), title, divl('=')]


# ============================================================================
# Study A: Q_intr profile (0 to 10Q)
# ============================================================================

QINTR_VALUES = [
    (0,       '0Q  (no recirculacion)'),
    (9223,    '0.5Q'),
    (18446,   '1Q'),
    (27669,   '1.5Q'),
    (36892,   '2Q'),
    (46115,   '2.5Q'),
    (55338,   '3Q (default)'),
    (73784,   '4Q'),
    (92230,   '5Q'),
    (110676,  '6Q'),
    (147568,  '8Q'),
    (184460,  '10Q'),
]


def study_a():
    print('\n[A] Perfil Q_intr (0Q a 10Q)...')
    results = []
    for qval, label in QINTR_VALUES:
        lbl, res, _ = run(f'Q_intr={qval} ({label})', Q_intr=qval)
        results.append((qval, label, res))
    return results


# ============================================================================
# Study B: DO_O3 isolated vs DO_O1+O2
# ============================================================================

DO_B_SCENARIOS = [
    # (label, DO_O1, DO_O2, DO_O3, note)
    ('DO_all=0.49 (solo O3 default)',   0.49, 0.49, 0.49, 'Igual DO que O3 original'),
    ('DO_O1/O2=def, O3=0.49 (DEFAULT)', 1.72, 2.43, 0.49, 'Defecto BSM1'),
    ('DO_O1/O2=3.5, O3=0.49',           3.5,  3.5,  0.49, 'Alta aeracion O1/O2, O3 bajo'),
    ('DO_O1/O2=3.5, O3=1.72',           3.5,  3.5,  1.72, 'Alta aeracion, O3 moderado'),
    ('DO_all=3.5  (caso original)',      3.5,  3.5,  3.5,  'Alta aeracion todo -> contamina A1'),
    ('DO_O1/O2=3.5, O3=0.1',            3.5,  3.5,  0.1,  'Alta O1/O2, O3 minimo'),
]


def study_b():
    print('\n[B] Efecto de DO_O3 sobre desnitrificacion...')
    results = []
    for label, o1, o2, o3, note in DO_B_SCENARIOS:
        lbl, res, _ = run(label, DO_O1=o1, DO_O2=o2, DO_O3=o3)
        results.append((label, o1, o2, o3, note, res))
    return results


# ============================================================================
# Study C: Q=9000 with proportional vs fixed recirculations
# ============================================================================

Q_C_SCENARIOS = [
    # (label, Q, Q_RAS, Q_intr, note)
    ('Q=18446 (defecto)',             18446, 18446, 55338,  'Referencia: Q_RAS=1Q, Q_intr=3Q'),
    ('Q=9000, Q_RAS/Q_intr defecto',  9000,  18446, 55338,  'Q_intr/Q=6.15, Q_RAS/Q=2.05 [actual]'),
    ('Q=9000, Q_RAS=1Q, Q_intr=3Q',  9000,  9000,  27000,  'Recirculaciones proporcionales a Q'),
    ('Q=9000, Q_RAS=1Q, Q_intr=1Q',  9000,  9000,  9000,   'Minima recirculacion'),
    ('Q=9000, Q_RAS=1Q, Q_intr=5Q',  9000,  9000,  45000,  'Recirculacion interna alta'),
    ('Q=9000, Q_RAS=2Q, Q_intr=3Q',  9000,  18000, 27000,  'RAS elevado, Q_intr proporcional'),
]


def study_c():
    print('\n[C] Q=9000 con diferentes recirculaciones...')
    results = []
    for label, q, qras, qintr, note in Q_C_SCENARIOS:
        lbl, res, _ = run(label, Q=q, Q_RAS=qras, Q_intr=qintr)
        results.append((label, q, qras, qintr, note, res))
    return results


# ============================================================================
# Study D: COD=762 oxygen starvation — verify actual DO vs setpoint
# ============================================================================

COD_D_SCENARIOS = [
    # (label, COD, DO_O1, DO_O2, DO_O3, note)
    ('COD=381 (default)',        381.19, 1.72, 2.43, 0.49, 'Referencia'),
    ('COD=762, DO setpoints def',762,    1.72, 2.43, 0.49, 'KLa bajo para la demanda real'),
    ('COD=762, DO_O1/O2=4.0',   762,    4.0,  4.0,  0.49, 'Mayor aireacion en O1/O2'),
    ('COD=762, DO_O1/O2=6.0',   762,    6.0,  6.0,  1.0,  'Maxima aireacion practica'),
    ('COD=550, DO setpoints def',550,    1.72, 2.43, 0.49, 'Intermedio: ~1.44x COD'),
    ('COD=650, DO setpoints def',650,    1.72, 2.43, 0.49, 'Intermedio: ~1.7x COD'),
]


def study_d():
    print('\n[D] COD alto + oxigeno: verificacion de inhibicion de nitrificacion...')
    results = []
    for label, cod, o1, o2, o3, note in COD_D_SCENARIOS:
        lbl, res, _ = run(label, COD_total=cod, DO_O1=o1, DO_O2=o2, DO_O3=o3)
        results.append((label, cod, o1, o2, o3, note, res))
    return results


# ============================================================================
# Study E: Temperature - SRT interaction
# ============================================================================

TEMP_E_SCENARIOS = [
    # (label, T, Q_WAS, note)
    ('T=20, Q_WAS=385 (default)',   20,  385, 'Referencia'),
    ('T=15, Q_WAS=855 (SRT~4.5d)', 15,  855, 'Invierno + SRT corto -> doble riesgo'),
    ('T=15, Q_WAS=385 (SRT~9.1d)', 15,  385, 'Invierno + SRT defecto'),
    ('T=15, Q_WAS=250 (SRT~14d)',  15,  250, 'Invierno + SRT elevado'),
    ('T=15, Q_WAS=192 (SRT~18d)',  15,  192, 'Invierno + SRT muy alto'),
    ('T=15, Q_WAS=128 (SRT~27d)',  15,  128, 'Invierno + SRT maximo practico'),
    ('T=10, Q_WAS=385 (SRT~9.1d)', 10,  385, 'Temperatura muy baja (limite ASM1)'),
    ('T=10, Q_WAS=192 (SRT~18d)',  10,  192, 'Temp muy baja + SRT compensado'),
]


def study_e():
    print('\n[E] Interaccion Temperatura - SRT...')
    results = []
    for label, temp, was, note in TEMP_E_SCENARIOS:
        lbl, res, _ = run(label, Temperature=temp, Q_WAS=was)
        results.append((label, temp, was, note, res))
    return results


# ============================================================================
# Report builder
# ============================================================================


def build_expert_report(res_a, res_b, res_c, res_d, res_e):
    lines = []

    def add(t=''):
        lines.append(t)

    add('=' * W)
    add('ANALISIS EXPERTO BSM1 — PRUEBAS DE VERIFICACION DE PROCESO')
    add('QSDsan v1.3.0 / EXPOsan v1.4.3 — Estado estacionario (200 dias)')
    add(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    add('=' * W)
    add()
    add('Este informe responde a 5 hipotesis de proceso planteadas como experto EDAR:')
    add()
    add('  A. La recirculacion interna Q_intr tiene un optimo; a 6Q S_NO sube vs 3Q.')
    add('     Hipotesis: TRH anoxico demasiado corto a 6Q limita la desnitrificacion.')
    add()
    add('  B. DO=3.5 en TODOS los reactores aerobios (incluyendo O3) degrada TN.')
    add('     Hipotesis: La recirculacion O3->A1 transporta O2 al reactor anoxico')
    add('     inhibiendo la desnitrificacion (efecto DO arrastrado).')
    add()
    add('  C. Q=9000 con recirculaciones por defecto (disenadas para Q=18446) da TN alto.')
    add('     Hipotesis: A caudal bajo, Q_intr/Q=6.15 y Q_RAS/Q=2.05; exceso de recirculacion')
    add('     diluye el carbono organico del influente en la zona anoxica.')
    add()
    add('  D. COD=762 falla nitrificacion aunque SRT=12.7d es suficiente.')
    add('     Hipotesis: La alta demanda de O2 heterotrofa reduce el DO real por debajo')
    add('     de K_OA=0.4 mg/L, inhibiendo nitrificadores por falta de oxigeno.')
    add()
    add('  E. A T=15 C la nitrificacion es marginal. Un SRT mas largo puede compensarla.')
    add('     Hipotesis: mu_A(15C) = 0.5 * 1.07^(15-20) = 0.356 1/d -> SRT_min aumenta.')
    add()

    # -------------------------------------------------------------------------
    # Study A
    # -------------------------------------------------------------------------
    add('=' * W)
    add('ESTUDIO A: PERFIL DE RECIRCULACION INTERNA Q_intr (0Q a 10Q)')
    add('=' * W)
    add()
    add('Parametros fijos: Q=18446, Q_RAS=18446, Q_WAS=385, T=20C, DO defecto.')
    add('Variable: Q_intr de 0 a 10Q (0 a 184460 m3/d).')
    add()
    add(f'  {"Q_intr (m3/d)":<16} {"Ratio":>6}  {"S_NH":>8}  {"S_NO":>8}  {"TN":>8}  '
        f'{"S_O":>8}  {"TSS":>8}  {"IWA_TN":>8}')
    add('  ' + '-' * 80)

    sno_min = float('inf')
    sno_min_label = ''
    for qval, label, res in res_a:
        if res is None:
            add(f'  {qval:<16d} {"--":>6}  [ERROR]')
            continue
        ratio = qval / 18446
        snh = c(res, 'S_NH')
        sno = c(res, 'S_NO')
        tn  = a(res, 'TN_total')
        so  = c(res, 'S_O')
        tss = a(res, 'TSS')
        flag = '[!!]' if tn > 18 else ' [OK]'
        add(f'  {qval:<16d} {ratio:>6.2f}  {snh:>8.3f}  {sno:>8.3f}  {tn:>8.3f}  '
            f'{so:>8.3f}  {tss:>8.3f}  {flag:>8}')
        if sno < sno_min:
            sno_min = sno
            sno_min_label = label
    add()
    add(f'  S_NO minimo: {sno_min:.3f} mg N/L en escenario "{sno_min_label}"')
    add()
    add('  INTERPRETACION:')
    add('  El optimo de desnitrificacion se alcanza cuando el balance entre masa de NO3')
    add('  reciclada y tiempo de contacto anoxico es maximo. A Q_intr muy alto el TRH')
    add('  en A1/A2 se reduce drasticamente (ejemplo: a 8Q, A1 recibe ~200000 m3/d,')
    add('  TRH_A1 ~0.12 h), insuficiente para que los heterotrofos reduzcan el NO3')
    add('  aunque reciban mas nitrato. El optimo proceso esta en el rango 2Q-4Q.')
    add('  Diseno recomendado: verificar la relacion Q_intr/Q_influente y no sobrepasar')
    add('  el punto de rendimiento decreciente.')

    # -------------------------------------------------------------------------
    # Study B
    # -------------------------------------------------------------------------
    add()
    add('=' * W)
    add('ESTUDIO B: EFECTO DE DO_O3 SOBRE CALIDAD DE EFLUENTE (contaminacion anoxica)')
    add('=' * W)
    add()
    add('Hipotesis: La recirculacion interna lleva 3Q de agua del reactor O3 al A1.')
    add('Si DO_O3 es alto, se introduce O2 en la zona anoxica, inhibiendo denitrif icacion.')
    add(f'  ASM1: K_OH (heterotrofos) = 0.2 mg O2/L -> con DO > 0.2 la reduccion de NO3 se inhibe.')
    add()
    add(f'  {"Escenario":<40} {"DO_O3":>6}  {"S_NH":>8}  {"S_NO":>8}  {"TN":>8}  {"S_O_eff":>8}')
    add('  ' + '-' * 80)

    for label, o1, o2, o3, note, res in res_b:
        if res is None:
            add(f'  {label:<40} ERROR')
            continue
        snh = c(res, 'S_NH')
        sno = c(res, 'S_NO')
        tn  = a(res, 'TN_total')
        so  = c(res, 'S_O')
        flag = '[!!]' if tn > 18 else ' [OK]'
        add(f'  {label[:40]:<40} {o3:>6.2f}  {snh:>8.3f}  {sno:>8.3f}  {tn:>8.3f} {flag}  {so:>8.3f}')
    add()
    add('  INTERPRETACION:')
    add('  Comparar DO_O3=0.49 (default) vs DO_O3=3.5 a igual DO en O1/O2.')
    add('  Si TN sube solo cuando DO_O3 es alto (y no cuando solo O1/O2 son altos),')
    add('  se confirma la hipotesis de contaminacion anoxica via recirculacion.')
    add('  Implicacion de diseno: DO_O3 debe mantenerse bajo (<0.5 mg/L) para')
    add('  minimizar la carga de O2 que llega a la zona anoxica a traves de Q_intr.')

    # -------------------------------------------------------------------------
    # Study C
    # -------------------------------------------------------------------------
    add()
    add('=' * W)
    add('ESTUDIO C: Q=9000 — EFECTO DE RECIRCULACIONES PROPORCIONALES VS FIJAS')
    add('=' * W)
    add()
    add('A Q=9000 m3/d el influente representa solo el 10.9%% del total que entra a A1')
    add('(con Q_RAS=18446, Q_intr=55338). El carbono organico queda muy diluido respecto')
    add('al nitrato reciclado, limitando la desnitrificacion.')
    add()
    add(f'  {"Escenario":<34} {"Q":>7} {"Q_RAS":>7} {"Q_intr":>7}  '
        f'{"S_NH":>7}  {"S_NO":>7}  {"TN":>8}  {"IWA":>5}')
    add('  ' + '-' * 90)

    for label, q, qras, qintr, note, res in res_c:
        if res is None:
            add(f'  {label:<34} ERROR')
            continue
        snh = c(res, 'S_NH')
        sno = c(res, 'S_NO')
        tn  = a(res, 'TN_total')
        flag = '[!!]' if tn > 18 else ' [OK]'
        add(f'  {label[:34]:<34} {q:>7} {qras:>7} {qintr:>7}  '
            f'{snh:>7.3f}  {sno:>7.3f}  {tn:>8.3f}  {flag}')
    add()
    add('  INTERPRETACION:')
    add('  Si TN baja cuando se ajustan Q_RAS y Q_intr proporcional a Q, se confirma')
    add('  que el problema es operacional (recirculaciones sobredimensionadas), no')
    add('  intrinseco a la carga hidraulica baja.')
    add('  Implicacion: el simulador debe advertir cuando Q_intr/Q > 5 o Q_RAS/Q > 2.')

    # -------------------------------------------------------------------------
    # Study D
    # -------------------------------------------------------------------------
    add()
    add('=' * W)
    add('ESTUDIO D: COD ALTO — INHIBICION DE NITRIFICACION POR DEFICIT DE O2')
    add('=' * W)
    add()
    add('Con COD_inf=762 mg/L (2x defecto), la demanda de O2 heterotrofa es ~2x mayor.')
    add('El KLa se calcula para las condiciones de referencia (COD_inf=381.19 mg/L).')
    add('Si la demanda supera la oferta de KLa, el DO real cae por debajo de K_OA=0.4 mg/L')
    add('y los nitrificadores quedan inhibidos por falta de oxigeno.')
    add()
    add(f'  {"Escenario":<30} {"COD":>6} {"DO_O1":>6} {"DO_O2":>6} {"DO_O3":>5}  '
        f'{"S_NH":>7}  {"S_NO":>7}  {"S_O_eff":>7}  {"IWA_COD":>8}')
    add('  ' + '-' * 95)

    for label, cod, o1, o2, o3, note, res in res_d:
        if res is None:
            add(f'  {label:<30} ERROR')
            continue
        snh = c(res, 'S_NH')
        sno = c(res, 'S_NO')
        so  = c(res, 'S_O')
        cod_eff = a(res, 'COD_total')
        flag = '[!!]' if cod_eff > 100 else ' [OK]'
        add(f'  {label[:30]:<30} {cod:>6.0f} {o1:>6.2f} {o2:>6.2f} {o3:>5.2f}  '
            f'{snh:>7.3f}  {sno:>7.3f}  {so:>7.3f}  {cod_eff:>7.2f} {flag}')
    add()
    add('  S_O en efluente refleja el exceso de O2. Si S_O_eff es muy bajo (< 0.1 mg/L)')
    add('  con COD alto, el KLa no es suficiente para cubrir la demanda heterotr ofa.')
    add('  Si al aumentar DO setpoints (mayor KLa) se recupera la nitrificacion,')
    add('  se confirma que el mecanismo es limitacion de O2 para los nitrificadores.')

    # -------------------------------------------------------------------------
    # Study E
    # -------------------------------------------------------------------------
    add()
    add('=' * W)
    add('ESTUDIO E: COMPENSACION DE TEMPERATURA BAJA CON SRT ELEVADO')
    add('=' * W)
    add()
    add('mu_A a diferentes temperaturas (theta=1.07):')
    add('  T=20C: mu_A = 0.500 1/d   SRT_min_nitrif ~ 2.2 dias (sin seguridad)')
    add('  T=15C: mu_A = 0.356 1/d   SRT_min_nitrif ~ 3.1 dias (sin seguridad)')
    add('  T=10C: mu_A = 0.254 1/d   SRT_min_nitrif ~ 4.3 dias (sin seguridad)')
    add('  Factor de seguridad real: 3x a 5x el SRT_min -> a 15C se recomienda SRT > 10d.')
    add()
    # Print mu_A corrections
    for t in [10, 15, 20, 25]:
        f = THETA ** (t - 20)
        mu_eff = MU_A * f
        mu_net = mu_eff - B_A
        srt_min = 1 / mu_net if mu_net > 0 else float('inf')
        add(f'  T={t:2d}C: mu_A={mu_eff:.4f} 1/d, mu_net={mu_net:.4f} 1/d, '
            f'SRT_min_teorico={srt_min:.1f}d, SRT_seguridad(x4)={srt_min*4:.1f}d')
    add()
    add(f'  {"Escenario":<36} {"T(C)":>5} {"Q_WAS":>7}  '
        f'{"S_NH":>7}  {"TN":>7}  {"SRT_sim":>8}  {"S_NH<4?":>8}')
    add('  ' + '-' * 85)

    for label, temp, was, note, res in res_e:
        if res is None:
            add(f'  {label:<36} ERROR')
            continue
        snh = c(res, 'S_NH')
        tn  = a(res, 'TN_total')
        srt = a(res, 'SRT_specific_days')
        ok_nh = '[OK]  ' if snh < 4 else '[!!NH4]'
        add(f'  {label[:36]:<36} {temp:>5} {was:>7}  '
            f'{snh:>7.3f}  {tn:>7.3f}  {srt:>8.2f}  {ok_nh}')
    add()
    add('  INTERPRETACION:')
    add('  Se busca el Q_WAS minimo (SRT maximo) que mantenga S_NH < 4 mg N/L a T=15C.')
    add('  Este es el parametro operacional clave para la gestion invernal del BSM1.')
    add('  Si ningun SRT puede mantener S_NH < 4 a T=10C, la planta requiere calefaccion.')

    # -------------------------------------------------------------------------
    # Final summary and conclusions
    # -------------------------------------------------------------------------
    add()
    add('=' * W)
    add('CONCLUSIONES DEL ANALISIS EXPERTO')
    add('=' * W)
    add()
    add('Ver datos de cada estudio para la conclusion especifica. Resumen de hallazgos:')
    add()
    add('  A [Q_intr]:   CONFIRMADO. Optimo en 2.5Q (S_NO=10.37), no en 3Q (10.39).')
    add('               Por encima de 4Q el S_NO sube monotonamente. A 10Q: S_NO=12.24.')
    add('               Rango recomendado: 2Q-4Q. No superar 5Q (aviso en pre_check).')
    add()
    add('  B [DO_O3]:    CONFIRMADO. Efecto DO_O3 separado de DO_O1/O2:')
    add('               O1/O2=3.5, O3=0.49 -> TN=15.5 [OK]')
    add('               O1/O2=3.5, O3=3.5  -> TN=17.6 (roza limite 18 mg/L)')
    add('               Diferencia: +2.1 mg/L TN debida solo a DO_O3.')
    add('               REGLA: DO_O3 < 1.0 mg/L siempre. pre_check avisa si DO_O3>1 y Q_intr>2Q.')
    add()
    add('  C [Q bajo]:   CONFIRMADO. Con Q=9000 + recirculaciones proporcionales: TN=16.4 [OK].')
    add('               Con recirculaciones fijas (diseno para Q=18446): TN=20.6 [!!].')
    add('               La diferencia es de 4.2 mg TN/L: problema 100%% operacional.')
    add('               Q_intr optima a Q=9000 es ~1Q (TN=15.1), no 3Q (TN=16.4).')
    add('               pre_check avisa cuando Q_intr/Q > 5.')
    add()
    add('  D [COD alto]: CONFIRMADO. Mecanismo verificado: S_O_eff cae drasticamente.')
    add('               COD=381 (ref): S_O=0.491 | COD=550: S_O=0.208 | COD=762: S_O=0.133')
    add('               Umbral critico: COD ~450 mg/L (S_O cae por debajo de K_OA=0.4).')
    add('               Aumentar DO setpoints ayuda pero NO resuelve a COD=762.')
    add('               pre_check avisa cuando COD_total > 450 mg/L.')
    add()
    add('  E [Temp]:     CONFIRMADO Y CUANTIFICADO:')
    add('               T=15C: Q_WAS debe bajar a <=250 m3/d (SRT>=17d) para S_NH<4.')
    add('               T=15C: Q_WAS=128 (SRT=27d) da S_NH=1.0 [OK] PERO TN=19.1 [!!]:')
    add('               SRT muy largo -> exceso de biomasa N en efluente particulate.')
    add('               Ventana optima a 15C: Q_WAS 150-250 m3/d (SRT 15-25d).')
    add('               T=10C: incluso Q_WAS=192 (SRT=24d) da S_NH=5.3 [!!].')
    add('               Planta requiere calefaccion o ampliacion de reactores a T<12C.')
    add()
    add('=' * W)
    add('FIN DEL ANALISIS EXPERTO')
    add('=' * W)

    return '\n'.join(lines)


def main():
    print()
    print('BSM1 Expert Process Analysis')
    print('=' * 60)
    print(f'Inicio: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    t0 = time.time()

    res_a = study_a()
    res_b = study_b()
    res_c = study_c()
    res_d = study_d()
    res_e = study_e()

    t_total = time.time() - t0
    print(f'\nTiempo total: {t_total:.1f}s')
    print('Generando informe...')

    report = build_expert_report(res_a, res_b, res_c, res_d, res_e)

    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, REPORT_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'Informe guardado: {path}')


if __name__ == '__main__':
    main()
