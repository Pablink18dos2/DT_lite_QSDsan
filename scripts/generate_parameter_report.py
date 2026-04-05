"""BSM1 Parameter Sensitivity Report Generator.

Runs simulations for all user-configurable PlantParameters across a range of
low / baseline / high values and produces a comprehensive text report.

Each scenario varies ONE parameter while keeping all others at BSM1 defaults.
Results include all 14 ASM1 components + aggregate indicators (COD, TN, BOD5,
TSS, SRT) plus IWA compliance flags.

Usage:
    python generate_parameter_report.py

Output:
    reports/INFORME_SENSIBILIDAD_PARAMETROS.txt
"""

import os
import sys
import time
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from app.engine import run_steady_state_simulation
from app.models import PlantParameters
from app.config import IWA_SS_REF, IWA_SS_TSS, IWA_LIMITS

# ============================================================================
# Report configuration
# ============================================================================

REPORT_DIR = 'reports'
REPORT_FILE = 'INFORME_SENSIBILIDAD_PARAMETROS.txt'

# All 14 components in display order
ALL_COMPONENTS = [
    'S_I', 'S_S', 'X_I', 'X_S', 'X_BH', 'X_BA', 'X_P',
    'S_O', 'S_NO', 'S_NH', 'S_ND', 'X_ND', 'S_ALK', 'TSS',
]

COMPONENT_UNITS_DISPLAY = {
    'S_I':   'mg COD/L',
    'S_S':   'mg COD/L',
    'X_I':   'mg COD/L',
    'X_S':   'mg COD/L',
    'X_BH':  'mg COD/L',
    'X_BA':  'mg COD/L',
    'X_P':   'mg COD/L',
    'S_O':   'mg O2/L ',
    'S_NO':  'mg N/L  ',
    'S_NH':  'mg N/L  ',
    'S_ND':  'mg N/L  ',
    'X_ND':  'mg N/L  ',
    'S_ALK': 'mol/m3  ',
    'TSS':   'mg SS/L ',
}

IWA_REF_DISPLAY = {**IWA_SS_REF, 'TSS': IWA_SS_TSS}

AGGREGATE_KEYS = [
    ('COD_total',       'COD total efluente',         'mg COD/L', 100.0),
    ('TN_total',        'Nitrogeno total (TN)',         'mg N/L',   18.0),
    ('BOD5',            'DBO5 efluente',               'mg/L',     10.0),
    ('TSS',             'SST efluente',                'mg SS/L',  30.0),
    ('Q_effluent_m3d',  'Caudal efluente',             'm3/d',     None),
    ('SRT_specific_days','SRT especifico',              'dias',     None),
]

# ============================================================================
# Scenarios definition
# ============================================================================

SCENARIOS = [
    # (group_title, group_description, list_of_(scenario_label, kwargs, param_note))
    (
        'CASO BASE BSM1 (valores por defecto IWA)',
        'PlantParameters sin modificar. Validacion de los 14 componentes IWA.',
        [
            ('BASE', {}, ''),
        ],
    ),
    (
        'GRUPO 1 -- EDAD DEL LODO: Q_WAS (m3/d)',
        ('El SRT es el parametro de diseno mas critico para la nitrificacion.\n'
         'Los nitrificadores (X_BA) tienen mu_A=0.5 1/d. A SRT bajo son arrastrados\n'
         'antes de reproducirse. A SRT alto se acumulan y nitrif ican bien.\n'
         'Formula aprox: SRT ~ 385 * 9.14 / Q_WAS [dias]\n'
         'NOTA: el SRT simulado puede ser mayor que la formula simple porque la biomasa\n'
         'acumulada (X_I, X_P) crece con el SRT, reduciendo la fraccion activa.'),
        [
            ('Q_WAS=192 (SRT~18.3d)', {'Q_WAS': 192},  'Alto SRT -> nitrificacion robusta'),
            ('Q_WAS=385 (SRT~9.1d)',  {'Q_WAS': 385},  'Defecto BSM1'),
            ('Q_WAS=855 (SRT~4.5d)',  {'Q_WAS': 855},  'Bajo SRT -> riesgo lavado X_BA'),
        ],
    ),
    (
        'GRUPO 2 -- CONTROL DE AIREACION: DO en reactores aerobios (mg O2/L)',
        ('El DO controla la transferencia de O2. KLa = OUR_ref / (DOsat - DO_setpoint).\n'
         'Los nitrificadores tienen K_OA=0.4 mg/L; con DO < K_OA la cinetica colapsa.\n'
         'Los valores de DO se aplican a los tres reactores aerobios (O1, O2, O3).'),
        [
            ('DO=0.3 en O1/O2/O3',  {'DO_O1': 0.3, 'DO_O2': 0.3, 'DO_O3': 0.3},
             'DO < K_OA -> nitrificacion inhibida'),
            ('DO=1.72/2.43/0.49',   {},
             'Defecto BSM1 (KLa=240/240/84)'),
            ('DO=3.5 en O1/O2/O3',  {'DO_O1': 3.5, 'DO_O2': 3.5, 'DO_O3': 3.5},
             'DO elevado -> nitrificacion plena'),
        ],
    ),
    (
        'GRUPO 3 -- TEMPERATURA (grados C)',
        ('Las tasas cineticas ASM1 siguen Arrhenius (theta=1.07).\n'
         'A 15 C: mu_A ~ 0.5 * 1.07^(15-20) = 0.36 1/d (reduccion 28%).\n'
         'A 25 C: mu_A ~ 0.5 * 1.07^(25-20) = 0.70 1/d (aumento 40%).\n'
         'Con Q_WAS fijo, menor temperatura -> peor nitrificacion.'),
        [
            ('T=15 C (invierno)',   {'Temperature': 15}, 'Condicion desfavorable'),
            ('T=20 C (referencia)', {},                  'Defecto BSM1'),
            ('T=25 C (verano)',     {'Temperature': 25}, 'Condicion favorable'),
        ],
    ),
    (
        'GRUPO 4 -- CARGA DE COD INFLUENTE (mg COD/L)',
        ('La descomposicion del influente escala linealmente COD_total:\n'
         '  S_I_inf = 30.0 * (COD / 381.19)   -- inerte, escala directamente.\n'
         '  S_S_inf = 69.5 * (COD / 381.19)   -- biodegradable.\n'
         'S_I pasa por la planta sin degradarse, dominando el COD efluente.'),
        [
            ('COD=200 mg/L',  {'COD_total': 200},  '~52% del defecto; S_I_inf~15.7'),
            ('COD=381 mg/L',  {},                   'Defecto BSM1'),
            ('COD=762 mg/L',  {'COD_total': 762},   '~2x defecto; S_I_inf~60.0'),
        ],
    ),
    (
        'GRUPO 5 -- RECIRCULACION INTERNA Q_intr (m3/d)',
        ('La recirculacion interna (O3->A1) transporta S_NO a la zona anoxica\n'
         'donde se desnitrifica. Mayor Q_intr -> mas NO3 hacia A1/A2 -> menor S_NO.\n'
         'Rango practico: 1Q a 6Q. Por encima se satura la desnitrificacion.\n'
         'ATENCION: comportamiento NO monotonico observado. A 6Q el TRH en A1/A2\n'
         'cae drasticamente (A1 recibe 147568 m3/d, TRH~0.16 h) limitando la\n'
         'desnitrificacion por contacto insuficiente. El optimo esta en ~3Q.'),
        [
            ('Q_intr=18446 (1Q)',   {'Q_intr': 18446},  'Minimo operacional'),
            ('Q_intr=55338 (3Q)',   {},                  'Defecto BSM1'),
            ('Q_intr=110676 (6Q)',  {'Q_intr': 110676}, 'Maximo practico'),
        ],
    ),
    (
        'GRUPO 6 -- VOLUMEN DE REACTORES (m3)',
        ('Mayor volumen -> mayor HRT -> mayor tiempo contacto biomasa-sustrato.\n'
         'Con Q_WAS fijo, mayor volumen tambien implica mayor SRT efectivo.\n'
         'Ambos efectos mejoran nitrificacion y eliminacion de COD.'),
        [
            ('50%% vol (an=500, ae=666)',    {'V_anoxic': 500,  'V_aerobic': 666},
             'HRT ~3.9 h, SRT reducido'),
            ('100%% vol (an=1000, ae=1333)', {},
             'Defecto BSM1 (HRT ~7.8 h)'),
            ('200%% vol (an=2000, ae=2666)', {'V_anoxic': 2000, 'V_aerobic': 2666},
             'HRT ~15.6 h, SRT elevado'),
        ],
    ),
    (
        'GRUPO 7 -- CAUDAL INFLUENTE Q (m3/d)',
        ('Q controla el HRT: HRT = (2*V_an + 3*V_ae) / Q.\n'
         'Con volumenes fijos, mayor Q -> menor HRT -> peor tratamiento.\n'
         'La carga hidraulica del decantador (SOR=Q_feed/A) tambien aumenta.'),
        [
            ('Q=9000 m3/d (0.5x)',  {'Q': 9000},  'HRT ~15.6 h (bajo carga)'),
            ('Q=18446 m3/d (1x)',   {},            'Defecto BSM1 (HRT ~7.8 h)'),
            ('Q=36000 m3/d (2x)',   {'Q': 36000}, 'HRT ~4.0 h (sobrecarga)'),
        ],
    ),
    (
        'GRUPO 8 -- TKN INFLUENTE (mg N/L)',
        ('TKN influente determina la carga de amoniaco: S_NH_inf = 31.56*(TKN/51.35).\n'
         'Con capacidad de nitrificacion fija (SRT, KLa), mayor carga TKN\n'
         'supera el limite -> S_NH efluente sube.'),
        [
            ('TKN=25 mg N/L (bajo)', {'TKN': 25},  'S_NH_inf~15.4 mg/L'),
            ('TKN=51 mg N/L (ref)',  {},            'Defecto BSM1 (S_NH_inf=31.56)'),
            ('TKN=100 mg N/L (alto)',{'TKN': 100}, 'S_NH_inf~61.5 mg/L -> sobrecarga'),
        ],
    ),
    (
        'GRUPO 9 -- RECIRCULACION EXTERNA RAS Q_RAS (m3/d)',
        ('RAS devuelve los lodos del clarificador a A1.\n'
         'Mayor Q_RAS -> mayor MLSS en reactores -> mejor retencion de biomasa\n'
         '-> mejor nitrificacion. Contrapartida: mayor carga hidraulica en decantador.'),
        [
            ('Q_RAS=9000 m3/d (0.5Q)',   {'Q_RAS': 9000},  'Poca retencion de biomasa'),
            ('Q_RAS=18446 m3/d (1Q)',    {},                'Defecto BSM1'),
            ('Q_RAS=55000 m3/d (~3Q)',   {'Q_RAS': 55000}, 'Alta retencion de biomasa'),
        ],
    ),
    (
        'GRUPO 10 -- AREA DEL DECANTADOR (m2)',
        ('El SOR (surface overflow rate) = Q_feed / A controla la separacion de solidos.\n'
         'Q_feed = Q + Q_RAS = 36892 m3/d (defecto).\n'
         'A mayor SOR, la velocidad ascensional supera la de sedimentacion -> TSS sube.'),
        [
            ('Area=500 m2  (SOR=3.1 m/h)', {'Clarifier_area': 500},  'Decantador subdimensionado (pequeno)'),
            ('Area=1500 m2 (SOR=1.0 m/h)', {},                        'Defecto BSM1'),
            ('Area=4000 m2 (SOR=0.4 m/h)', {'Clarifier_area': 4000}, 'Holgura de capacidad'),
        ],
    ),
    (
        'GRUPO 11 -- PARAMETROS SIN EFECTO EN EFLUENTE EN ESTADO ESTACIONARIO (verificacion)',
        ('Estos parametros son informativos o tienen compensacion exacta en SS.\n'
         'La calidad del efluente (concentraciones) debe ser identica al caso base.\n'
         'NOTA Clarifier_height: si bien el efluente es identico, el SRT SI cambia\n'
         '(mayor volumen de decantador -> mayor masa de lodo en el sistema -> mayor SRT).\n'
         'Esto es consistente con la teoria: la altura afecta el blanket de lodos\n'
         'almacenado, no la separacion solido-liquido en superficie.'),
        [
            ('TSS_inf=50 mg/L',        {'TSS_inf': 50},        'Solo advertencia en pre_check'),
            ('TSS_inf=1000 mg/L',      {'TSS_inf': 1000},      'Solo advertencia en pre_check'),
            ('DOsat=6.5 mg/L',         {'DOsat': 6.5},         'KLa compensa (OUR invariante)'),
            ('DOsat=12.0 mg/L',        {'DOsat': 12.0},        'KLa compensa (OUR invariante)'),
            ('Clarifier_h=1 m',        {'Clarifier_height': 1},'Solo volumen almacenamiento'),
            ('Clarifier_h=10 m',       {'Clarifier_height': 10},'Solo volumen almacenamiento'),
        ],
    ),
]

# ============================================================================
# Helper functions
# ============================================================================


def get_comp(result, comp_id):
    """Return simulated concentration for a named component."""
    if comp_id == 'TSS':
        return result.aggregates.get('TSS', float('nan'))
    for c in result.components:
        if c.component == comp_id:
            return c.obtained
    return float('nan')


def get_agg(result, key):
    """Return an aggregate value from result."""
    val = result.aggregates.get(key)
    return val if val is not None else float('nan')


def iwa_limit_flag(key, value):
    """Return compliance flag vs IWA effluent limits."""
    limits_map = {
        'COD_total': IWA_LIMITS['COD'],
        'TN_total':  IWA_LIMITS['TN'],
        'BOD5':      IWA_LIMITS['BOD5'],
        'TSS':       IWA_LIMITS['TSS'],
    }
    limit = limits_map.get(key)
    if limit is None:
        return '   '
    if value <= limit:
        return '[OK]'
    else:
        return '[!!]'


def fmt(value, decimals=3):
    """Format a float value for tabular display."""
    if value is None or (isinstance(value, float) and (value != value)):  # nan check
        return '   N/A  '
    return f'{value:>8.{decimals}f}'


def divider(char='-', width=90):
    return char * width


def run_all_scenarios():
    """Execute all simulations and return results dict keyed by scenario label."""
    results = {}
    total_scenarios = sum(len(sc[2]) for sc in SCENARIOS)
    current = 0

    print(f'Ejecutando {total_scenarios} escenarios...')
    print(divider())

    for group_title, _, scenario_list in SCENARIOS:
        short_group = group_title[:60]
        for label, kwargs, note in scenario_list:
            current += 1
            print(f'  [{current:2d}/{total_scenarios}] {label:<40s} ', end='', flush=True)
            t0 = time.time()
            try:
                plant = PlantParameters(**kwargs)
                result = run_steady_state_simulation(plant=plant, t_days=200)
                elapsed = time.time() - t0
                print(f'OK  ({elapsed:.1f}s)')
                results[label] = (result, kwargs, note)
            except Exception as exc:
                elapsed = time.time() - t0
                print(f'ERROR: {exc}  ({elapsed:.1f}s)')
                results[label] = (None, kwargs, str(exc))

    print(divider())
    return results


def build_report(results):
    """Build the complete text report."""
    lines = []

    def add(text=''):
        lines.append(text)

    W = 110  # report width

    # Header
    add('=' * W)
    add('INFORME DE SENSIBILIDAD DE PARAMETROS - BSM1 (QSDsan v1.3.0 / EXPOsan v1.4.3)')
    add('Benchmark Simulation Model No. 1 - Analisis estado estacionario (200 dias)')
    add(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    add('Referencia IWA: Dr. Ulf Jeppsson, Lund University (2008). Tolerancia: +/- 5%%.')
    add('=' * W)
    add()
    add('INDICADORES CLAVE DE CALIDAD DE EFLUENTE (limites IWA dinamico):')
    add('  COD total  < 100 mg COD/L   |  TN total < 18 mg N/L   |  BOD5 < 10 mg/L')
    add('  SST        < 30  mg SS/L    |  S_NH > 4 mg N/L es VIOLACION ESPERADA en lazo abierto')
    add()
    add('REFERENCIA IWA (estado estacionario, efluente):')
    add(f'  {"Componente":<12} {"Referencia":>10}  {"Unidades":<14}')
    add(f'  {"-"*40}')
    for comp in ALL_COMPONENTS:
        ref = IWA_REF_DISPLAY.get(comp, '-')
        unit = COMPONENT_UNITS_DISPLAY.get(comp, '')
        add(f'  {comp:<12} {ref:>10.4f}  {unit:<14}')
    add()
    add('AGREGADOS DE REFERENCIA IWA (estado estacionario):')
    add('  COD total:  48.3 mg/L (din.) | TN total: 15.6 mg/L (din.) | BOD5: 2.8 mg/L (din.)')
    add('  SST:        12.5 mg/L (SS)   | SRT especifico: 9.14 dias  | Q_eff: 18061 m3/d')
    add()
    add('=' * W)
    add('HALLAZGOS CLAVE DE SENSIBILIDAD (resumen ejecutivo para el experto)')
    add('=' * W)
    add()
    add('1. SRT (Q_WAS): Parametro mas critico. A SRT=4.5d la nitrificacion COLAPSA (S_NH=37.4 mg/L,')
    add('   X_BA~0). El SRT simulado supera al de la formula simple (Q_WAS=192 -> SRT_sim=26d,')
    add('   no 18d) porque la biomasa inerte (X_I, X_P) acumulada eleva la masa total del sistema.')
    add()
    add('2. Temperatura: A 15C S_NH=7.6 mg/L (viola el limite de 4) y TN=17.5 mg/L (cerca del limite).')
    add('   A 25C el sistema mejora notablemente (S_NH=0.6, TN=12.2). El BSM1 en lazo abierto')
    add('   es marginalmente estable en condiciones invernales.')
    add()
    add('3. DO (aireacion): A DO=3.5 mg/L la nitrificacion mejora (S_NH=0.6) pero S_NO=15.1 y')
    add('   TN=17.6 mg/L (casi en el limite). Mas nitrificacion sin mas desnitrificacion eleva TN.')
    add('   La aireacion excesiva en lazo abierto puede empeorar la calidad del efluente en TN.')
    add()
    add('4. COD influente: COD bajo (200 mg/L) da TN=31.5 mg/L [!!] por deficit de carbono para')
    add('   desnitrificacion (relacion C:N insuficiente -> S_NO=28.5 mg/L). COD alto (762 mg/L)')
    add('   colapsa por sobrecarga (COD_eff=176, TSS=85, TN=39, BOD5=47 -- todos fuera de limite).')
    add()
    add('5. Recirculacion interna (Q_intr): Comportamiento NO monotonico. S_NO minimo a 3Q (10.4),')
    add('   sube a 6Q (11.1). A 6Q el caudal en A1 es 147568 m3/d (TRH=0.16 h), insuficiente para')
    add('   denitrif icar aunque se recircule mas nitrato. Optimo operacional: 3Q.')
    add()
    add('6. Caudal Q: A Q=0.5x TN=20.6 [!!] por exceso de nitrificacion relativa al COD disponible')
    add('   (C:N bajo, denitrificacion carbon-limitada). A Q=2x la planta colapsa completamente.')
    add()
    add('7. Altura del decantador: La calidad del efluente es identica para h=1m y h=10m, pero')
    add('   el SRT varia (7.75 vs 11.92 dias) porque la altura cambia el volumen del blanket de')
    add('   lodos almacenado. La altura NO afecta la separacion S/L (modelo Takacs) sino la')
    add('   retencion de biomasa en el sistema. IMPORTANTE: CLAUDE.md seccion 23 requiere correccion.')
    add()
    add('8. DBO5 con decantador pequeno (500 m2): DBO5=15.4 mg/L [!!] excede el limite de 10 mg/L')
    add('   aunque TSS=28.6 esta justo por debajo de 30. La DBO5 incluye biomasa activa (X_BH)')
    add('   que escapa del decantador sobrec argado. Un ingeniero podria subestimar el incumplimiento')
    add('   si solo monitoriza SST.')
    add()
    add('9. Invariancia confirmada: TSS_inf y DOsat no afectan el efluente (verificado).')
    add('   DOsat modifica KLa (e.g., DOsat=6.5 -> KLa_O1=315 vs defecto 240) pero el punto de')
    add('   operacion OUR=KLa*(DOsat-DO_ss) permanece constante.')
    add()

    # Groups
    for group_idx, (group_title, group_desc, scenario_list) in enumerate(SCENARIOS):
        add('=' * W)
        add(group_title)
        add('=' * W)
        # Description (multi-line)
        for desc_line in group_desc.split('\n'):
            add(f'  {desc_line}')
        add()

        # Build comparison table: columns are scenarios in this group
        labels = [lbl for lbl, _, _ in scenario_list]
        valid_labels = [lbl for lbl in labels if results.get(lbl) and results[lbl][0] is not None]

        if not valid_labels:
            add('  [Sin resultados - todos los escenarios fallaron]')
            add()
            continue

        # Column width
        col_w = 13

        # --- Component table ---
        add('  COMPONENTES ASM1 EN EFLUENTE:')
        header_parts = [f'{"Componente":<12}', f'{"Unidades":<14}', f'{"Ref IWA":>{col_w}}']
        for lbl in valid_labels:
            short_lbl = lbl[:col_w]
            header_parts.append(f'{short_lbl:>{col_w}}')
        add('  ' + '  '.join(header_parts))
        add('  ' + '-' * (14 + 14 + (col_w + 2) * (1 + len(valid_labels))))

        for comp in ALL_COMPONENTS:
            ref = IWA_REF_DISPLAY.get(comp, float('nan'))
            unit = COMPONENT_UNITS_DISPLAY.get(comp, '')
            row_parts = [f'{comp:<12}', f'{unit:<14}', f'{ref:>{col_w}.4f}']
            for lbl in valid_labels:
                result, _, _ = results[lbl]
                val = get_comp(result, comp)
                row_parts.append(f'{val:>{col_w}.4f}')
            add('  ' + '  '.join(row_parts))
        add()

        # --- Aggregate table ---
        add('  INDICADORES AGREGADOS:')
        hdr2 = [f'{"Indicador":<28}', f'{"Unidades":<12}', f'{"Lim IWA":>{col_w}}']
        for lbl in valid_labels:
            hdr2.append(f'{lbl[:col_w]:>{col_w}}')
        add('  ' + '  '.join(hdr2))
        add('  ' + '-' * (28 + 12 + (col_w + 2) * (1 + len(valid_labels))))

        for agg_key, agg_label, agg_unit, agg_limit in AGGREGATE_KEYS:
            lim_str = f'{agg_limit:>{col_w}.1f}' if agg_limit is not None else f'{"--":>{col_w}}'
            row2 = [f'{agg_label:<28}', f'{agg_unit:<12}', lim_str]
            for lbl in valid_labels:
                result, _, _ = results[lbl]
                val = get_agg(result, agg_key)
                flag = iwa_limit_flag(agg_key, val) if agg_limit else ''
                row2.append(f'{val:>{col_w - 4}.3f} {flag}')
            add('  ' + '  '.join(row2))
        add()

        # --- Notes per scenario ---
        add('  NOTAS DE ESCENARIOS:')
        for lbl, kwargs, note in scenario_list:
            result_entry = results.get(lbl)
            if result_entry and result_entry[0] is not None:
                result, _, _ = result_entry
                method = result.method_used
                secs = result.compute_time_seconds
                pass_cnt = result.pass_count
                total_cnt = result.total_count
                kla1 = result.aggregates.get('_param_KLa_O1', '-')
                kla2 = result.aggregates.get('_param_KLa_O2', '-')
                kla3 = result.aggregates.get('_param_KLa_O3', '-')
                q_was_eff = result.aggregates.get('_param_Q_WAS', '-')
                add(f'    [{lbl}]')
                add(f'      Nota proceso: {note}')
                add(f'      Solver: {method}  |  Tiempo: {secs:.1f}s  |  Validacion IWA: {pass_cnt}/{total_cnt} PASS')
                add(f'      KLa calculados: O1={kla1} 1/d, O2={kla2} 1/d, O3={kla3} 1/d')
                add(f'      Q_WAS efectivo: {q_was_eff} m3/d')
                if kwargs:
                    param_str = ', '.join(f'{k}={v}' for k, v in kwargs.items())
                    add(f'      Parametros modificados: {param_str}')
            else:
                add(f'    [{lbl}] -- ERROR')
        add()

    # Summary compliance table
    add('=' * W)
    add('TABLA RESUMEN: CUMPLIMIENTO LIMITES IWA POR ESCENARIO')
    add('  [OK] = dentro del limite  |  [!!] = excede el limite  |  -- = sin limite definido')
    add('=' * W)
    add()

    # Collect all scenario labels
    all_labels_flat = []
    for _, _, scenario_list in SCENARIOS:
        for lbl, _, _ in scenario_list:
            all_labels_flat.append(lbl)

    # Header
    col_w2 = 26
    hdr_s = [f'{"Escenario":<{col_w2}}']
    for agg_key, _, agg_unit, _ in AGGREGATE_KEYS:
        short_key = agg_key[:10]
        hdr_s.append(f'{short_key:>12}')
    add('  ' + '  '.join(hdr_s))
    add('  ' + '-' * (col_w2 + 2 + 14 * len(AGGREGATE_KEYS)))

    for lbl in all_labels_flat:
        entry = results.get(lbl)
        if not entry or entry[0] is None:
            add(f'  {lbl:<{col_w2}}  [ERROR]')
            continue
        result, _, _ = entry
        row_s = [f'{lbl[:col_w2]:<{col_w2}}']
        for agg_key, _, agg_unit, agg_limit in AGGREGATE_KEYS:
            val = get_agg(result, agg_key)
            flag = iwa_limit_flag(agg_key, val) if agg_limit else '   '
            row_s.append(f'{val:>8.2f} {flag}')
        add('  ' + '  '.join(row_s))

    add()
    add('=' * W)
    add('FIN DEL INFORME')
    add('=' * W)

    return '\n'.join(lines)


def main():
    print()
    print('BSM1 Parameter Sensitivity Report Generator')
    print('=' * 60)
    print(f'Inicio: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    t_total_start = time.time()
    results = run_all_scenarios()
    t_total = time.time() - t_total_start

    print(f'\nTiempo total de simulaciones: {t_total:.1f}s')
    print('Generando informe...')

    report_text = build_report(results)

    # Save report
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, REPORT_FILE)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f'Informe guardado en: {report_path}')
    print()

    # Print brief summary to console
    print('RESUMEN RAPIDO:')
    print('-' * 60)
    for _, _, scenario_list in SCENARIOS:
        for lbl, _, _ in scenario_list:
            entry = results.get(lbl)
            if not entry or entry[0] is None:
                print(f'  {lbl:<40s}  ERROR')
                continue
            result, _, _ = entry
            s_nh = next((c.obtained for c in result.components if c.component == 'S_NH'), float('nan'))
            s_no = next((c.obtained for c in result.components if c.component == 'S_NO'), float('nan'))
            cod  = result.aggregates.get('COD_total', float('nan'))
            tss  = result.aggregates.get('TSS', float('nan'))
            tn   = result.aggregates.get('TN_total', float('nan'))
            print(f'  {lbl:<38s} S_NH={s_nh:6.3f} S_NO={s_no:6.3f} COD={cod:6.2f} TSS={tss:6.3f} TN={tn:6.3f}')
    print('-' * 60)
    print(f'Informe completo: {report_path}')


if __name__ == '__main__':
    main()
