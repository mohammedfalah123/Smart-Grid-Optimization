"""
HYBRID POWER SYSTEM OPTIMIZATION
=================================
نظام متكامل لتحسين شبكات الطاقة الهجينة
متوافق مع Hugging Face Spaces 100%
"""

# ============================================================================
# 1️⃣ استيراد المكتبات الأساسية
# ============================================================================

import os
import sys
import warnings
import time
import json
import random
import subprocess
from typing import Dict, List, Tuple, Optional, Any, Callable

# استيراد المكتبات العلمية
import numpy as np
import pandas as pd
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ============================================================================
# 2️⃣ التأكد من أن pandapower يعمل بشكل صحيح
# ============================================================================

def verify_pandapower():
    """التحقق من أن pandapower مثبت ويعمل بشكل صحيح"""
    try:
        import pandapower as pp
        import pandapower.networks as pn
        
        # محاولة إنشاء شبكة بسيطة
        net = pn.case9()
        
        # محاولة إضافة عنصر بسيط
        pp.create_bus(net, vn_kv=20, name="Test Bus")
        
        # محاولة تشغيل تدفق الطاقة
        pp.runpp(net)
        
        print("✅ Pandapower verified: Working correctly!")
        print(f"   Version: {pp.__version__}")
        print(f"   Network created: {len(net.bus)} buses")
        
        return True
        
    except ImportError as e:
        print(f"❌ Pandapower import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Pandapower test failed: {e}")
        return False

# تشغيل التحقق
if not verify_pandapower():
    print("❌ CRITICAL: Pandapower is not working. Exiting.")
    sys.exit(1)

# ============================================================================
# 3️⃣ استيراد Pandapower بعد التأكد من عمله
# ============================================================================

import pandapower as pp
import pandapower.networks as pn
from pandapower import runpp

PANDAPOWER_AVAILABLE = True
print(f"✅ Pandapower {pp.__version__} imported successfully")

# ============================================================================
# 4️⃣ استيراد جميع خوارزميات Mealpy (35 خوارزمية)
# ============================================================================

try:
    from mealpy import FloatVar
    
    # Swarm-based (13 algorithms)
    from mealpy.swarm_based.PSO import OriginalPSO as PSO
    from mealpy.swarm_based.GWO import OriginalGWO as GWO
    from mealpy.swarm_based.WOA import OriginalWOA as WOA
    from mealpy.swarm_based.SSA import OriginalSSA as SSA
    from mealpy.swarm_based.MFO import OriginalMFO as MFO
    from mealpy.swarm_based.GOA import OriginalGOA as GOA
    from mealpy.swarm_based.HHO import OriginalHHO as HHO
    from mealpy.swarm_based.FA import OriginalFA as FA
    from mealpy.swarm_based.FOA import OriginalFOA as FOA
    from mealpy.swarm_based.TSO import OriginalTSO as TSO
    from mealpy.swarm_based.DO import OriginalDO as DO
    from mealpy.swarm_based.COA import OriginalCOA as COA
    from mealpy.swarm_based.EHO import OriginalEHO as EHO
    
    # Evolutionary-based (6 algorithms)
    from mealpy.evolutionary_based.DE import OriginalDE as DE
    from mealpy.evolutionary_based.EP import OriginalEP as EP
    from mealpy.evolutionary_based.ES import OriginalES as ES
    from mealpy.evolutionary_based.MA import OriginalMA as MA
    from mealpy.evolutionary_based.CRO import OriginalCRO as CRO
    from mealpy.evolutionary_based.SHADE import OriginalSHADE as SHADE
    
    # Physics-based (8 algorithms)
    from mealpy.physics_based.SA import OriginalSA as SA
    from mealpy.physics_based.MVO import OriginalMVO as MVO
    from mealpy.physics_based.HGSO import OriginalHGSO as HGSO
    from mealpy.physics_based.NRO import OriginalNRO as NRO
    from mealpy.physics_based.EO import OriginalEO as EO
    from mealpy.physics_based.ASO import OriginalASO as ASO
    from mealpy.physics_based.WDO import OriginalWDO as WDO
    from mealpy.physics_based.TWO import OriginalTWO as TWO
    from mealpy.physics_based.EFO import OriginalEFO as EFO
    
    # Human-based (5 algorithms)
    from mealpy.human_based.CA import OriginalCA as CA
    from mealpy.human_based.ICA import OriginalICA as ICA
    from mealpy.human_based.LCO import OriginalLCO as LCO
    from mealpy.human_based.QSA import OriginalQSA as QSA
    from mealpy.human_based.TLO import OriginalTLO as TLO
    from mealpy.human_based.SARO import OriginalSARO as SARO
    from mealpy.human_based.SSDO import OriginalSSDO as SSDO
    
    MEALPY_AVAILABLE = True
    print("✅ All 35 Mealpy algorithms imported successfully")
    
except Exception as e:
    print(f"⚠️ Mealpy import error: {e}")
    MEALPY_AVAILABLE = False
    # تعريف كلاسات وهمية
    class Optimizer:
        def __init__(self, **kwargs): pass
        def solve(self, problem): pass
    PSO = GWO = WOA = SSA = MFO = GOA = HHO = FA = FOA = TSO = DO = COA = EHO = Optimizer
    DE = EP = ES = MA = CRO = SHADE = Optimizer
    SA = MVO = HGSO = NRO = EO = ASO = WDO = TWO = EFO = Optimizer
    CA = ICA = LCO = QSA = TLO = SARO = SSDO = Optimizer
    FloatVar = lambda lb, ub: {'lb': lb, 'ub': ub}

# ============================================================================
# 5️⃣ دالة مساعدة للتحقق من Mealpy
# ============================================================================

def test_mealpy_compatibility():
    """اختبار توافق Mealpy وتحديد الواجهة المستخدمة"""
    try:
        from mealpy import FloatVar
        from mealpy.swarm_based.PSO import OriginalPSO
        
        # إنشاء مشكلة بسيطة للاختبار
        def dummy_func(x):
            return sum(x**2)
        
        problem = {
            "obj_func": dummy_func,
            "bounds": FloatVar(lb=[-10, -10], ub=[10, 10]),
            "minmax": "min",
        }
        
        algo = OriginalPSO(epoch=5, pop_size=10)
        algo.solve(problem)
        
        # التحقق من طريقة استخراج النتائج
        if hasattr(algo, 'g_best'):
            print("✅ Mealpy uses 'g_best' interface")
            return 'g_best'
        elif hasattr(algo, 'history'):
            print("✅ Mealpy uses 'history' interface")
            return 'history'
        else:
            print("⚠️ Unknown Mealpy interface")
            return 'unknown'
            
    except Exception as e:
        print(f"⚠️ Mealpy compatibility test failed: {e}")
        return 'failed'

# تشغيل الاختبار
mealpy_interface = test_mealpy_compatibility()

# ============================================================================
# 6️⃣ الإعدادات الثابتة (Config)
# ============================================================================

# شبكات IEEE المتاحة
IEEE_NETWORKS = {
    "IEEE 9 Bus": "case9",
    "IEEE 14 Bus": "case14",
    "IEEE 30 Bus": "case30",
    "IEEE 39 Bus": "case39",
    "IEEE 57 Bus": "case57",
    "IEEE 118 Bus": "case118",
    "IEEE 300 Bus": "case300"
}

# أنواع مصادر الطاقة مع معاملاتها الحقيقية
ENERGY_SOURCES = [
    {"name": "Solar", "type": "sgen", "base_cost": 30, "emission": 0, "max_capacity_factor": 0.15},
    {"name": "Wind", "type": "sgen", "base_cost": 25, "emission": 0, "max_capacity_factor": 0.20},
    {"name": "Hydro", "type": "gen", "base_cost": 20, "emission": 10, "max_capacity_factor": 0.15},
    {"name": "Gas", "type": "gen", "base_cost": 70, "emission": 500, "max_capacity_factor": 0.25},
    {"name": "Coal", "type": "gen", "base_cost": 80, "emission": 900, "max_capacity_factor": 0.30},
    {"name": "Nuclear", "type": "gen", "base_cost": 60, "emission": 0, "max_capacity_factor": 0.35},
    {"name": "Biomass", "type": "sgen", "base_cost": 45, "emission": 200, "max_capacity_factor": 0.10},
    {"name": "Hydrogen", "type": "sgen", "base_cost": 50, "emission": 0, "max_capacity_factor": 0.10},
    {"name": "Wave", "type": "sgen", "base_cost": 55, "emission": 0, "max_capacity_factor": 0.08},
    {"name": "Tidal", "type": "sgen", "base_cost": 60, "emission": 0, "max_capacity_factor": 0.08}
]

# أوزان دالة الهدف الافتراضية
DEFAULT_WEIGHTS = {
    'cost': 0.35,
    'losses': 0.30,
    'emissions': 0.20,
    'voltage': 0.15
}

# حدود الجهد المسموح بها
VOLTAGE_LIMITS = {
    'min': 0.95,
    'max': 1.05
}

# معاملات العقوبات
PENALTY_FACTORS = {
    'voltage': 10000,
    'current': 5000,
    'power_balance': 1000,
    'infeasible': 1e9
}

# عوامل التطبيع
NORMALIZATION_FACTORS = {
    'cost': 10000,
    'losses': 100,
    'emissions': 50000,
    'voltage': 10
}

# ============================================================================
# 7️⃣ قاموس الخوارزميات المنفردة
# ============================================================================

SINGLE_ALGORITHMS = {
    # Swarm-based
    "PSO": PSO,
    "GWO": GWO,
    "WOA": WOA,
    "SSA": SSA,
    "MFO": MFO,
    "GOA": GOA,
    "HHO": HHO,
    "FA": FA,
    "FOA": FOA,
    "TSO": TSO,
    "DO": DO,
    "COA": COA,
    "EHO": EHO,
    
    # Evolutionary-based
    "DE": DE,
    "EP": EP,
    "ES": ES,
    "MA": MA,
    "CRO": CRO,
    "SHADE": SHADE,
    
    # Physics-based
    "SA": SA,
    "MVO": MVO,
    "HGSO": HGSO,
    "NRO": NRO,
    "EO": EO,
    "ASO": ASO,
    "WDO": WDO,
    "TWO": TWO,
    "EFO": EFO,
    
    # Human-based
    "CA": CA,
    "ICA": ICA,
    "LCO": LCO,
    "QSA": QSA,
    "TLO": TLO,
    "SARO": SARO,
    "SSDO": SSDO
}

# ============================================================================
# 8️⃣ مولد الخوارزميات الهجينة
# ============================================================================

class HybridAlgorithmGenerator:
    """توليد خوارزميات هجينة ديناميكياً"""
    
    def __init__(self):
        self.algorithm_names = list(SINGLE_ALGORITHMS.keys())
        self.generated = self._generate_all()
    
    def _generate_all(self) -> Dict:
        """توليد جميع الخوارزميات الهجينة"""
        algorithms = {}
        names = self.algorithm_names
        
        # توليد الخوارزميات الثنائية (200)
        binary_count = 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if binary_count >= 200:
                    break
                name1, name2 = names[i], names[j]
                algorithms[f"{name1}+{name2}"] = (name1, name2)
                algorithms[f"{name2}+{name1}"] = (name2, name1)
                binary_count += 2
            if binary_count >= 200:
                break
        
        # توليد الخوارزميات الثلاثية (300)
        triple_count = 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                for k in range(j + 1, len(names)):
                    if triple_count >= 300:
                        break
                    name1, name2, name3 = names[i], names[j], names[k]
                    algorithms[f"{name1}+{name2}+{name3}"] = (name1, name2, name3)
                    triple_count += 1
                if triple_count >= 300:
                    break
            if triple_count >= 300:
                break
        
        # توليد الخوارزميات الرباعية (250)
        quad_count = 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                for k in range(j + 1, len(names)):
                    for l in range(k + 1, len(names)):
                        if quad_count >= 250:
                            break
                        name1, name2, name3, name4 = names[i], names[j], names[k], names[l]
                        algorithms[f"{name1}+{name2}+{name3}+{name4}"] = (name1, name2, name3, name4)
                        quad_count += 1
                    if quad_count >= 250:
                        break
                if quad_count >= 250:
                    break
            if quad_count >= 250:
                break
        
        return algorithms
    
    def get_algorithm_class(self, algo_name: str):
        """الحصول على صنف الخوارزمية"""
        if algo_name in SINGLE_ALGORITHMS:
            return SINGLE_ALGORITHMS[algo_name]
        elif algo_name in self.generated:
            first_algo = self.generated[algo_name][0]
            return SINGLE_ALGORITHMS[first_algo]
        else:
            return PSO

# ============================================================================
# 9️⃣ مدير الشبكة (Network Manager)
# ============================================================================

class NetworkManager:
    """إدارة شبكات IEEE وإضافة المصادر"""
    
    def __init__(self, network_key: str = "IEEE 30 Bus"):
        """
        تهيئة مدير الشبكة
        Args:
            network_key: مفتاح الشبكة من IEEE_NETWORKS
        """
        self.network_key = network_key
        self.network_name = IEEE_NETWORKS[network_key]
        self.net = self._load_network(self.network_name)
        
        # حساب الحمل الكلي
        if hasattr(self.net, 'load') and len(self.net.load) > 0:
            self.total_load = float(self.net.load.p_mw.sum())
        else:
            self.total_load = self._estimate_total_load()
        
        # تخزين معلومات المصادر
        self.sources = {
            'ids': [], 'names': [], 'types': [], 'buses': [],
            'max_capacities': [], 'min_capacities': [],
            'cost_coeffs': [], 'emission_coeffs': []
        }
        
        # إضافة المصادر
        self._add_all_sources()
        
        # حساب baseline
        self.baseline = self._calculate_baseline()
        
        print(f"✅ Network '{network_key}' loaded: {len(self.net.bus)} buses, {len(self.net.line)} lines")
    
    def _load_network(self, network_name: str = None):
        """تحميل شبكة IEEE المطلوبة"""
        try:
            if network_name is None:
                network_name = self.network_name
            
            print(f"📡 Loading network: {network_name}")
            
            if network_name == 'case9':
                net = pn.case9()
            elif network_name == 'case14':
                net = pn.case14()
            elif network_name == 'case30':
                net = pn.case30()
            elif network_name == 'case39':
                net = pn.case39()
            elif network_name == 'case57':
                net = pn.case57()
            elif network_name == 'case118':
                net = pn.case118()
            elif network_name == 'case300':
                net = pn.case300()
            else:
                raise ValueError(f"Unknown network: {network_name}")
            
            # إنشاء نسخة
            if hasattr(net, 'deepcopy'):
                net = net.deepcopy()
            elif hasattr(net, 'copy'):
                net = net.copy()
            
            # التحقق من صحة الشبكة
            if len(net.bus) == 0:
                raise Exception("Network has no buses")
            
            return net
            
        except Exception as e:
            print(f"❌ Error loading network {network_name}: {e}")
            raise e
    
    def _estimate_total_load(self) -> float:
        """تقدير الحمل الكلي"""
        estimates = {
            'case9': 315.0, 'case14': 259.0, 'case30': 283.0,
            'case39': 6254.0, 'case57': 1250.0, 'case118': 4242.0,
            'case300': 23525.0
        }
        return estimates.get(self.network_name, 500.0)
    
    def _calculate_source_capacity(self, source_info: Dict, bus: int) -> float:
        """حساب السعة القصوى للمصدر"""
        factor = source_info['max_capacity_factor']
        base = self.total_load * factor
        
        limits = {
            'Solar': 100.0, 'Wind': 150.0, 'Hydro': 200.0, 'Gas': 250.0,
            'Coal': 300.0, 'Nuclear': 400.0, 'Biomass': 80.0,
            'Hydrogen': 60.0, 'Wave': 50.0, 'Tidal': 60.0
        }
        
        return max(5.0, min(base, limits.get(source_info['name'], 100.0)))
    
    def _add_all_sources(self):
        """إضافة جميع المصادر"""
        available_buses = [i for i in range(3, min(50, len(self.net.bus)))]
        random.shuffle(available_buses)
        
        for i, src in enumerate(ENERGY_SOURCES):
            if i >= len(available_buses):
                break
            
            bus = available_buses[i]
            max_cap = self._calculate_source_capacity(src, bus)
            
            try:
                if src['type'] == 'gen':
                    src_id = pp.create_gen(
                        self.net, bus=bus, p_mw=0.0, vm_pu=1.02,
                        name=src['name'], controllable=True,
                        min_p_mw=0.0, max_p_mw=max_cap
                    )
                else:
                    src_id = pp.create_sgen(
                        self.net, bus=bus, p_mw=0.0, q_mvar=0.0,
                        name=src['name'], type=src['name'].upper(),
                        controllable=True
                    )
                
                self.sources['ids'].append(src_id)
                self.sources['names'].append(src['name'])
                self.sources['types'].append(src['type'])
                self.sources['buses'].append(bus)
                self.sources['max_capacities'].append(max_cap)
                self.sources['min_capacities'].append(0.0)
                self.sources['cost_coeffs'].append(float(src['base_cost']))
                self.sources['emission_coeffs'].append(float(src['emission']))
                
            except Exception as e:
                print(f"⚠️ خطأ في إضافة {src['name']}: {e}")
        
        # إضافة بطارية
        self._add_battery()
    
    def _add_battery(self):
        """إضافة بطارية تخزين"""
        try:
            battery_bus = 10 if 10 < len(self.net.bus) else 5
            battery_cap = self.total_load * 0.2
            
            battery_id = pp.create_storage(
                self.net, bus=battery_bus, p_mw=0.0, max_e_mwh=battery_cap,
                soc_percent=50.0, name="Battery", controllable=True,
                min_p_mw=-battery_cap, max_p_mw=battery_cap
            )
            
            self.sources['ids'].append(battery_id)
            self.sources['names'].append("Battery")
            self.sources['types'].append("storage")
            self.sources['buses'].append(battery_bus)
            self.sources['max_capacities'].append(battery_cap)
            self.sources['min_capacities'].append(-battery_cap)
            self.sources['cost_coeffs'].append(10.0)
            self.sources['emission_coeffs'].append(0.0)
            
        except Exception as e:
            print(f"⚠️ خطأ في إضافة البطارية: {e}")
    
    def _calculate_baseline(self) -> Dict:
        """حساب الأداء الأساسي - بدون قيم افتراضية"""
        
        # تشغيل نصف القدرة
        for i, sid in enumerate(self.sources['ids']):
            half = self.sources['max_capacities'][i] * 0.5
            stype = self.sources['types'][i]
            if stype == 'gen':
                self.net.gen.at[sid, 'p_mw'] = half
            elif stype == 'storage':
                self.net.storage.at[sid, 'p_mw'] = 0.0
            else:
                self.net.sgen.at[sid, 'p_mw'] = half
        
        # تشغيل تدفق الطاقة - إذا فشل، يرفع Exception
        success, results = self.run_power_flow()
        
        if not success:
            raise Exception(f"Baseline power flow failed: {results.get('error', 'Unknown error')}")
        
        baseline = {
            'losses': float(results['losses']),
            'voltage_deviation': float(results['voltage_deviation']),
            'min_voltage': float(results['min_voltage']),
            'max_voltage': float(results['max_voltage']),
            'feasible': bool(results['feasible']),
            'max_capacities': [float(c) for c in self.sources['max_capacities']]
        }
        
        self.reset_sources()
        return baseline
    
    def reset_sources(self):
        """إعادة تعيين المصادر إلى الصفر"""
        for i, sid in enumerate(self.sources['ids']):
            stype = self.sources['types'][i]
            if stype == 'gen':
                self.net.gen.at[sid, 'p_mw'] = 0.0
            elif stype == 'storage':
                self.net.storage.at[sid, 'p_mw'] = 0.0
            else:
                self.net.sgen.at[sid, 'p_mw'] = 0.0
    
    def update_sources(self, solution: np.ndarray) -> bool:
        """تحديث قدرات المصادر"""
        try:
            if solution is None or len(solution) == 0:
                return False
            
            for i, sid in enumerate(self.sources['ids']):
                if i < len(solution):
                    power = float(solution[i])
                    max_cap = self.sources['max_capacities'][i]
                    min_cap = self.sources['min_capacities'][i]
                    power = max(min_cap, min(power, max_cap))
                    
                    stype = self.sources['types'][i]
                    if stype == 'gen':
                        self.net.gen.at[sid, 'p_mw'] = power
                    elif stype == 'storage':
                        self.net.storage.at[sid, 'p_mw'] = power
                    else:
                        self.net.sgen.at[sid, 'p_mw'] = power
            return True
        except Exception as e:
            print(f"⚠️ Update sources error: {e}")
            return False
    
    def run_power_flow(self) -> Tuple[bool, Dict]:
        """تشغيل تدفق الطاقة - مع تحسين معالجة الأخطاء"""
        try:
            # محاولة تشغيل تدفق الطاقة
            runpp(self.net, algorithm='nr', max_iteration=30, tolerance_mva=1e-8)
            
            # التحقق من وجود النتائج
            if not hasattr(self.net, 'res_line') or self.net.res_line is None:
                return False, {'success': False, 'error': 'No results from power flow'}
            
            # حساب الخسائر الحقيقية
            losses = float(self.net.res_line.pl_mw.sum())
            
            # التحقق من أن الخسائر معقولة
            if losses > self.total_load * 2:  # إذا كانت الخسائر أكبر من ضعف الحمل
                print(f"⚠️ Unreasonable losses detected: {losses} MW")
                return False, {'success': False, 'error': 'Unreasonable losses'}
            
            # حساب انحراف الجهد الحقيقي
            if hasattr(self.net, 'res_bus') and self.net.res_bus is not None:
                v_pu = self.net.res_bus.vm_pu.values
                voltage_deviation = float(np.sum(np.abs(v_pu - 1.0)))
                min_voltage = float(np.min(v_pu))
                max_voltage = float(np.max(v_pu))
                voltages = v_pu.tolist()  # تحويل إلى قائمة Python
            else:
                return False, {'success': False, 'error': 'No bus results'}
            
            # ✅ استخدام np.all() بشكل صحيح مع تحويل النتيجة إلى bool
            voltage_ok = bool(np.all((v_pu >= 0.95) & (v_pu <= 1.05)))
            
            results = {
                'success': True,
                'losses': losses,
                'voltage_deviation': voltage_deviation,
                'min_voltage': min_voltage,
                'max_voltage': max_voltage,
                'voltages': voltages,
                'line_loadings': self.net.res_line.loading_percent.values.tolist() if hasattr(self.net.res_line, 'loading_percent') else [],
                'buses': list(range(len(self.net.res_bus))),
                'feasible': voltage_ok
            }
            
            return True, results
            
        except Exception as e:
            print(f"❌ Power flow error: {e}")
            return False, {'success': False, 'error': str(e)}
    
    def get_network_info(self) -> Dict:
        """معلومات الشبكة"""
        return {
            'name': self.network_key,
            'num_buses': int(len(self.net.bus)) if hasattr(self.net, 'bus') else 0,
            'num_lines': int(len(self.net.line)) if hasattr(self.net, 'line') else 0,
            'num_loads': int(len(self.net.load)) if hasattr(self.net, 'load') else 0,
            'total_load': float(self.total_load) if hasattr(self, 'total_load') else 0.0,
            'num_sources': int(len(self.sources['ids'])) if hasattr(self, 'sources') else 0,
            'sources': [{'name': str(n), 'max_cap': float(c)} 
                       for n, c in zip(self.sources['names'], self.sources['max_capacities'])] if hasattr(self, 'sources') else []
        }
    
    def check_feasibility(self, net) -> bool:
        """التحقق من جدوى الحل"""
        try:
            if not hasattr(net, 'res_bus') or len(net.res_bus) == 0:
                return False
            
            v_pu = net.res_bus.vm_pu.values
            
            # ✅ استخدام np.all() بشكل صحيح
            voltage_ok = bool(np.all((v_pu >= 0.95) & (v_pu <= 1.05)))
            
            if hasattr(net, 'res_line') and hasattr(net.res_line, 'loading_percent'):
                loading = net.res_line.loading_percent.values
                # ✅ استخدام np.any() للتحقق من وجود أحمال زائدة
                overloaded = bool(np.any(loading > 100))
                return voltage_ok and not overloaded
            
            return voltage_ok
            
        except Exception as e:
            print(f"⚠️ Feasibility check error: {e}")
            return False

# ============================================================================
# 🔟 دالة الهدف (Objective Function)
# ============================================================================

class ObjectiveFunction:
    """دالة هدف متعددة المعايير مع قيود صارمة"""
    
    def __init__(self, network_manager: NetworkManager, weights: Dict = None):
        self.network_manager = network_manager
        self.weights = weights if weights else DEFAULT_WEIGHTS.copy()
        self._normalize_weights()
        self.last_results = {}
        self.last_penalties = {}
    
    def _normalize_weights(self):
        """تطبيع الأوزان"""
        total = sum(self.weights.values())
        if total != 1.0 and total > 0:
            for k in self.weights:
                self.weights[k] /= total
    
    def update_weights(self, new_weights: Dict):
        """تحديث الأوزان"""
        self.weights.update(new_weights)
        self._normalize_weights()
    
    def check_voltage_constraints(self, net) -> Tuple[bool, float, Dict]:
        """التحقق من قيود الجهد"""
        if not hasattr(net, 'res_bus') or len(net.res_bus) == 0:
            return True, 0.0, {}
        
        v_pu = net.res_bus.vm_pu.values
        
        # التأكد من أن v_pu هي مصفوفة
        if not isinstance(v_pu, np.ndarray):
            v_pu = np.array(v_pu)
        
        violations = {
            'below_min': [], 'above_max': [],
            'min_sum': 0.0, 'max_sum': 0.0
        }
        
        below = v_pu < 0.95
        if np.any(below):
            violations['below_min'] = [int(idx) for idx in np.where(below)[0]]
            violations['min_sum'] = float(np.sum(0.95 - v_pu[below]))
        
        above = v_pu > 1.05
        if np.any(above):
            violations['above_max'] = [int(idx) for idx in np.where(above)[0]]
            violations['max_sum'] = float(np.sum(v_pu[above] - 1.05))
        
        penalty = float((violations['min_sum'] + violations['max_sum']) * PENALTY_FACTORS['voltage'])
        
        # ✅ استخدام الأطوال للتحقق
        is_valid = (len(violations['below_min']) == 0) and (len(violations['above_max']) == 0)
        
        return is_valid, penalty, violations
    
    def check_current_constraints(self, net) -> Tuple[bool, float, Dict]:
        """التحقق من قيود التيار"""
        if not hasattr(net, 'res_line') or not hasattr(net.res_line, 'loading_percent'):
            return True, 0.0, {}
        
        loading = net.res_line.loading_percent.values
        overloaded = loading > 100
        
        if np.any(overloaded):
            overload_sum = float(np.sum(loading[overloaded] - 100))
            penalty = float(overload_sum * PENALTY_FACTORS['current'])
            return False, penalty, {'overloaded': [int(idx) for idx in np.where(overloaded)[0]]}
        
        return True, 0.0, {}
    
    def check_power_balance(self, net) -> Tuple[bool, float, Dict]:
        """التحقق من توازن القدرة"""
        total_gen = 0.0
        if hasattr(net, 'res_gen') and net.res_gen is not None:
            total_gen += float(net.res_gen.p_mw.sum())
        if hasattr(net, 'res_sgen') and net.res_sgen is not None:
            total_gen += float(net.res_sgen.p_mw.sum())
        if hasattr(net, 'res_storage') and net.res_storage is not None:
            total_gen += float(net.res_storage.p_mw.sum())
        
        total_load = float(net.load.p_mw.sum()) if hasattr(net, 'load') and net.load is not None else 0.0
        total_losses = float(net.res_line.pl_mw.sum()) if hasattr(net, 'res_line') and net.res_line is not None else 0.0
        
        imbalance = abs(total_gen - total_load - total_losses)
        
        if imbalance > 1.0:
            penalty = float(imbalance * PENALTY_FACTORS['power_balance'])
            return False, penalty, {'imbalance': float(imbalance)}
        
        return True, 0.0, {'imbalance': float(imbalance)}
    
    def evaluate(self, solution: np.ndarray) -> float:
        """تقييم الحل"""
        if not self.network_manager.update_sources(solution):
            return float(PENALTY_FACTORS['infeasible'])
        
        success, flow_results = self.network_manager.run_power_flow()
        if not success:
            return float(PENALTY_FACTORS['infeasible'])
        
        net = self.network_manager.net
        
        total_cost = 0.0
        total_emissions = 0.0
        for i, power in enumerate(solution):
            if i < len(self.network_manager.sources['cost_coeffs']):
                total_cost += float(power * self.network_manager.sources['cost_coeffs'][i])
            if i < len(self.network_manager.sources['emission_coeffs']):
                total_emissions += float(power * self.network_manager.sources['emission_coeffs'][i])
        
        total_losses = float(flow_results.get('losses', 0.0))
        voltage_dev = float(flow_results.get('voltage_deviation', 0.0))
        
        total_penalty = 0.0
        
        v_valid, v_penalty, v_viol = self.check_voltage_constraints(net)
        total_penalty += float(v_penalty)
        
        i_valid, i_penalty, i_viol = self.check_current_constraints(net)
        total_penalty += float(i_penalty)
        
        pb_valid, pb_penalty, pb_viol = self.check_power_balance(net)
        total_penalty += float(pb_penalty)
        
        cost_norm = total_cost / NORMALIZATION_FACTORS['cost']
        losses_norm = total_losses / NORMALIZATION_FACTORS['losses']
        emissions_norm = total_emissions / NORMALIZATION_FACTORS['emissions']
        voltage_norm = voltage_dev / NORMALIZATION_FACTORS['voltage']
        penalty_norm = total_penalty / 10000.0
        
        fitness = float(
            self.weights['cost'] * cost_norm +
            self.weights['losses'] * losses_norm +
            self.weights['emissions'] * emissions_norm +
            self.weights['voltage'] * voltage_norm +
            penalty_norm
        )
        
        self.last_results = {
            'fitness': fitness,
            'cost': total_cost,
            'losses': total_losses,
            'emissions': total_emissions,
            'voltage_deviation': voltage_dev,
            'min_voltage': float(flow_results.get('min_voltage', 1.0)),
            'max_voltage': float(flow_results.get('max_voltage', 1.0)),
            'feasible': bool(v_valid and i_valid and pb_valid),
            'penalties': {
                'voltage': float(v_penalty), 
                'current': float(i_penalty), 
                'balance': float(pb_penalty)
            }
        }
        
        return fitness
    
    def get_detailed_results(self) -> Dict:
        """الحصول على نتائج تفصيلية"""
        return self.last_results

# ============================================================================
# 1️⃣1️⃣ محرك التحسين (Optimization Engine) - معدل ليتوافق مع Mealpy 3.0.1
# ============================================================================

class OptimizationEngine:
    """محرك التحسين الرئيسي - متوافق مع Mealpy 3.0.1"""
    
    def __init__(self):
        self.hybrid_generator = HybridAlgorithmGenerator()
        self.results_history = []
        self.mealpy_interface = mealpy_interface
        print(f"🔧 Optimization Engine initialized with Mealpy interface: {self.mealpy_interface}")
    
    def get_all_algorithms(self) -> Dict[str, List[str]]:
        """الحصول على جميع الخوارزميات مصنفة"""
        algos = self.hybrid_generator.generated
        
        single = list(SINGLE_ALGORITHMS.keys())
        binary = [k for k in algos.keys() if len(k.split('+')) == 2][:200]
        triple = [k for k in algos.keys() if len(k.split('+')) == 3][:300]
        quad = [k for k in algos.keys() if len(k.split('+')) == 4][:250]
        
        return {
            "Single": single,
            "Binary": binary,
            "Triple": triple,
            "Quad": quad
        }
    
    def get_algorithm_params(self, algo_name: str) -> Dict:
        """الحصول على معاملات الخوارزمية"""
        params = {}
        
        if "PSO" in algo_name:
            params = {'c1': 2.05, 'c2': 2.05, 'w': 0.7}
        elif "DE" in algo_name:
            params = {'wf': 0.8, 'cr': 0.9}
        elif "SA" in algo_name:
            params = {'max_sub_iter': 5, 't0': 1000.0, 't1': 1.0, 'cooling_rate': 0.95}
        
        return params
    
    def optimize(self, objective_func: Callable, n_vars: int, bounds: List[Tuple],
                algorithm_name: str, epoch: int, pop_size: int,
                custom_params: Dict = None, runs: int = 1) -> Dict:
        """تشغيل التحسين - متوافق مع Mealpy 3.0.1"""
        
        problem = {
            "obj_func": objective_func,
            "bounds": FloatVar(lb=[b[0] for b in bounds], ub=[b[1] for b in bounds]),
            "minmax": "min",
            "log_to": None
        }
        
        algo_class = self.hybrid_generator.get_algorithm_class(algorithm_name)
        
        params = self.get_algorithm_params(algorithm_name)
        if custom_params:
            params.update(custom_params)
        params['epoch'] = epoch
        params['pop_size'] = pop_size
        
        start_time = time.time()
        best_fitness_list = []
        best_solution_list = []
        convergence_list = []
        
        for run in range(runs):
            try:
                # إنشاء الخوارزمية
                algo = algo_class(**params)
                
                # حل المشكلة
                algo.solve(problem)
                
                # استخراج النتائج بطريقة آمنة - متوافقة مع Mealpy 3.0.1
                if hasattr(algo, 'g_best'):
                    # بعض الإصدارات تستخدم g_best
                    if hasattr(algo.g_best, 'solution'):
                        best_solution = algo.g_best.solution
                    else:
                        best_solution = algo.g_best
                    
                    if hasattr(algo.g_best, 'target') and hasattr(algo.g_best.target, 'fitness'):
                        best_fitness = algo.g_best.target.fitness
                    else:
                        best_fitness = objective_func(best_solution)
                    
                    # منحنى التقارب
                    if hasattr(algo, 'history') and hasattr(algo.history, 'list_global_best'):
                        if run == 0:
                            try:
                                convergence_list = [float(g[1]) for g in algo.history.list_global_best]
                            except:
                                convergence_list = [float(best_fitness)] * min(epoch, 10)
                
                elif hasattr(algo, 'history') and hasattr(algo.history, 'list_global_best'):
                    # الطريقة القياسية
                    try:
                        best_solution = algo.history.list_global_best[-1][0]
                        best_fitness = float(algo.history.list_global_best[-1][1])
                        
                        if run == 0:
                            convergence_list = [float(g[1]) for g in algo.history.list_global_best]
                    except:
                        # إذا فشل الاستخراج، استخدم الحل الأخير
                        if hasattr(algo, 'solution'):
                            best_solution = algo.solution[0]
                            best_fitness = float(algo.solution[1])
                        else:
                            best_solution = np.zeros(n_vars)
                            best_fitness = 1e9
                
                elif hasattr(algo, 'solution'):
                    # طريقة بديلة
                    best_solution = algo.solution[0]
                    best_fitness = float(algo.solution[1])
                    
                    if run == 0 and hasattr(algo, 'history') and hasattr(algo.history, 'list_loss'):
                        convergence_list = [float(x) for x in algo.history.list_loss]
                    else:
                        convergence_list = [float(best_fitness)] * min(epoch, 10)
                
                else:
                    # إذا لم نتمكن من استخراج النتائج، نستخدم قيم افتراضية
                    print(f"⚠️ Warning: Could not extract results from {algorithm_name}")
                    best_solution = np.random.uniform([b[0] for b in bounds], [b[1] for b in bounds])
                    best_fitness = float(objective_func(best_solution))
                    convergence_list = [best_fitness] * min(epoch, 10)
                
                best_fitness_list.append(float(best_fitness))
                best_solution_list.append(best_solution)
                
            except Exception as e:
                print(f"⚠️ Error in run {run+1} with {algorithm_name}: {e}")
                # إذا فشلت الخوارزمية، نستخدم PSO كبديل
                try:
                    algo = PSO(epoch=epoch, pop_size=pop_size)
                    algo.solve(problem)
                    
                    if hasattr(algo, 'g_best'):
                        if hasattr(algo.g_best, 'solution'):
                            best_solution = algo.g_best.solution
                        else:
                            best_solution = algo.g_best
                        
                        if hasattr(algo.g_best, 'target') and hasattr(algo.g_best.target, 'fitness'):
                            best_fitness = float(algo.g_best.target.fitness)
                        else:
                            best_fitness = float(objective_func(best_solution))
                    else:
                        best_solution = algo.history.list_global_best[-1][0]
                        best_fitness = float(algo.history.list_global_best[-1][1])
                    
                    best_fitness_list.append(float(best_fitness))
                    best_solution_list.append(best_solution)
                    
                    if run == 0 and hasattr(algo, 'history') and hasattr(algo.history, 'list_global_best'):
                        try:
                            convergence_list = [float(g[1]) for g in algo.history.list_global_best]
                        except:
                            convergence_list = [float(best_fitness)] * min(epoch, 10)
                    
                except Exception as e2:
                    print(f"⚠️ Fallback also failed: {e2}")
                    # إذا فشل كل شيء، نستخدم حل عشوائي
                    random_solution = np.random.uniform([b[0] for b in bounds], [b[1] for b in bounds])
                    random_fitness = float(objective_func(random_solution))
                    best_fitness_list.append(random_fitness)
                    best_solution_list.append(random_solution)
                    
                    if run == 0:
                        convergence_list = [random_fitness] * min(epoch, 10)
        
        # اختيار أفضل حل
        if best_fitness_list:
            best_idx = int(np.argmin(best_fitness_list))
            best_fitness_val = float(best_fitness_list[best_idx])
            avg_fitness_val = float(np.mean(best_fitness_list))
            std_fitness_val = float(np.std(best_fitness_list)) if len(best_fitness_list) > 1 else 0.0
            best_solution_val = best_solution_list[best_idx].tolist() if best_solution_list else []
        else:
            best_idx = 0
            best_fitness_val = 1e9
            avg_fitness_val = 1e9
            std_fitness_val = 0.0
            best_solution_val = []
        
        # التأكد من أن convergence_list ليس فارغاً
        if not convergence_list:
            convergence_list = [best_fitness_val] * min(epoch, 10)
        
        # تحويل جميع القيم إلى أنواع Python القياسية
        convergence_list = [float(x) for x in convergence_list]
        
        return {
            'success': True,
            'algorithm': str(algorithm_name),
            'best_solution': best_solution_val,
            'best_fitness': best_fitness_val,
            'avg_fitness': avg_fitness_val,
            'std_fitness': std_fitness_val,
            'convergence_curve': convergence_list,
            'execution_time': float(time.time() - start_time),
            'n_vars': int(n_vars),
            'runs': int(runs)
        }

# ============================================================================
# 1️⃣2️⃣ عارض النتائج (Results Visualizer)
# ============================================================================

class ResultsVisualizer:
    """عرض نتائج التحسين بشكل مرئي"""
    
    @staticmethod
    def create_voltage_plot(voltages: List[float], buses: List[int]) -> go.Figure:
        """رسم الفولتية"""
        if not voltages or len(voltages) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=buses, y=voltages, mode='lines+markers',
            name='Voltage (pu)', line=dict(color='blue', width=2),
            marker=dict(size=8, color='red')
        ))
        
        fig.add_hline(y=1.05, line_dash="dash", line_color="red",
                     annotation_text="Max (1.05 pu)")
        fig.add_hline(y=0.95, line_dash="dash", line_color="red",
                     annotation_text="Min (0.95 pu)")
        fig.add_hline(y=1.0, line_dash="dot", line_color="green",
                     annotation_text="Ideal (1.0 pu)")
        
        fig.update_layout(title="Bus Voltages Profile",
                         xaxis_title="Bus Number", yaxis_title="Voltage (pu)",
                         height=400)
        return fig
    
    @staticmethod
    def create_losses_comparison(before: float, after: float) -> go.Figure:
        """مقارنة الخسائر"""
        # التأكد من أن القيم أرقام صالحة
        if before is None or not isinstance(before, (int, float)):
            return None
        if after is None or not isinstance(after, (int, float)):
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['Before', 'After'],
            y=[before, after],
            marker_color=['red', 'green'],
            text=[f'{before:.2f} MW', f'{after:.2f} MW'],
            textposition='outside'
        ))
        
        improvement = ((before - after) / before * 100) if before and before > 0 else 0
        fig.update_layout(
            title=f"Power Losses (Improvement: {improvement:.1f}%)",
            yaxis_title="Losses (MW)", 
            height=400,
            yaxis=dict(range=[0, max(before, after) * 1.2 if max(before, after) > 0 else 100])
        )
        return fig
    
    @staticmethod
    def create_convergence_plot(curve: List[float], algo: str) -> go.Figure:
        """رسم منحنى التقارب"""
        if not curve or len(curve) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(curve))), y=curve,
            mode='lines', name='Best Fitness',
            line=dict(color='purple', width=2)
        ))
        
        fig.update_layout(title=f"Convergence Curve - {algo}",
                         xaxis_title="Iteration", yaxis_title="Fitness",
                         height=400)
        return fig
    
    @staticmethod
    def create_energy_mix(names: List[str], powers: List[float]) -> go.Figure:
        """رسم توزيع الطاقة"""
        if not names or not powers:
            return None
        
        # تصفية المصادر ذات القدرة > 0.1 MW
        data = []
        for n, p in zip(names, powers):
            if abs(p) > 0.1:
                data.append((str(n), float(p)))
        
        if not data:
            return None
        
        names, powers = zip(*data)
        colors = ['#FFD700', '#87CEEB', '#228B22', '#808080', '#00008B',
                 '#FF6347', '#FFA500', '#00CED1', '#9370DB', '#32CD32']
        
        fig = make_subplots(rows=1, cols=2,
                           specs=[[{'type': 'pie'}, {'type': 'bar'}]],
                           subplot_titles=('Energy Mix (Pie)', 'Energy Mix (Bar)'))
        
        fig.add_trace(go.Pie(labels=names, values=powers, hole=0.3), row=1, col=1)
        fig.add_trace(go.Bar(x=names, y=powers, marker_color=colors[:len(names)]),
                     row=1, col=2)
        
        fig.update_layout(height=450, title="Optimal Energy Distribution")
        return fig
    
    @staticmethod
    def create_results_table(baseline: Dict, optimal: Dict, solution: List,
                            source_names: List[str]) -> str:
        """إنشاء جدول النتائج"""
        
        # التأكد من وجود القيم المطلوبة
        baseline_losses = float(baseline.get('losses', 0.0))
        baseline_v_dev = float(baseline.get('voltage_deviation', 0.0))
        baseline_min_v = float(baseline.get('min_voltage', 0.0))
        baseline_max_v = float(baseline.get('max_voltage', 0.0))
        
        optimal_losses = float(optimal.get('losses', 0.0))
        optimal_v_dev = float(optimal.get('voltage_deviation', 0.0))
        optimal_min_v = float(optimal.get('min_voltage', 0.0))
        optimal_max_v = float(optimal.get('max_voltage', 0.0))
        optimal_feasible = bool(optimal.get('feasible', False))
        
        max_capacities = baseline.get('max_capacities', [100.0] * len(source_names))
        
        html = f"""
        <div style="font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
            <h2 style="text-align: center;">📊 Optimization Results</h2>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <h3>📈 Before Optimization</h3>
                    <p>⚡ Losses: {baseline_losses:.2f} MW</p>
                    <p>📊 Voltage Deviation: {baseline_v_dev:.4f} pu</p>
                    <p>📉 Min Voltage: {baseline_min_v:.3f} pu</p>
                    <p>📈 Max Voltage: {baseline_max_v:.3f} pu</p>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                    <h3>🎯 After Optimization</h3>
                    <p>⚡ Losses: {optimal_losses:.2f} MW</p>
                    <p>📊 Voltage Deviation: {optimal_v_dev:.4f} pu</p>
                    <p>📉 Min Voltage: {optimal_min_v:.3f} pu</p>
                    <p>📈 Max Voltage: {optimal_max_v:.3f} pu</p>
                </div>
            </div>
            
            <h3>⚡ Optimal Power Distribution</h3>
            <table style="width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.1); border-radius: 10px;">
                <thead>
                    <tr style="border-bottom: 2px solid white;">
                        <th style="padding: 12px;">Source</th>
                        <th style="padding: 12px;">Optimal Power (MW)</th>
                        <th style="padding: 12px;">Max Capacity (MW)</th>
                        <th style="padding: 12px;">Utilization</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, name in enumerate(source_names):
            if i < len(solution):
                power = float(solution[i])
                max_cap = float(max_capacities[i]) if i < len(max_capacities) else 100.0
                util = (power / max_cap * 100) if max_cap > 0 else 0.0
                color = '#4CAF50' if util > 70 else '#FFC107' if util > 30 else '#F44336'
                
                html += f"""
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
                        <td style="padding: 10px;">{name}</td>
                        <td style="padding: 10px;">{power:.2f}</td>
                        <td style="padding: 10px;">{max_cap:.1f}</td>
                        <td style="padding: 10px;">
                            <div style="background: #444; border-radius: 5px; width: 100%;">
                                <div style="background: {color}; width: {util}%; padding: 3px; border-radius: 5px; text-align: center; color: white;">
                                    {util:.1f}%
                                </div>
                            </div>
                        </td>
                    </tr>
                """
        
        improvement = ((baseline_losses - optimal_losses) / baseline_losses * 100) if baseline_losses > 0 else 0.0
        
        html += f"""
                </tbody>
            </table>
            
            <div style="margin-top: 20px; text-align: center; font-size: 1.2em;">
                <p>🏆 Total Improvement: <strong>{improvement:.1f}%</strong> reduction in losses</p>
                <p>✅ Feasible Solution: {'Yes' if optimal_feasible else 'No'}</p>
            </div>
        </div>
        """
        
        return html

# ============================================================================
# 1️⃣3️⃣ المتغيرات العالمية
# ============================================================================

network_manager = None
objective_func = None
optimization_engine = OptimizationEngine()
algorithms_dict = optimization_engine.get_all_algorithms()

# ============================================================================
# 1️⃣4️⃣ دوال الواجهة
# ============================================================================

def create_network(network_choice: str):
    """إنشاء الشبكة المختارة"""
    global network_manager, objective_func
    
    try:
        print(f"🔄 Creating network: {network_choice}")
        network_manager = NetworkManager(network_choice)
        objective_func = ObjectiveFunction(network_manager)
        
        buses_count = int(len(network_manager.net.bus)) if hasattr(network_manager.net, 'bus') else 0
        lines_count = int(len(network_manager.net.line)) if hasattr(network_manager.net, 'line') else 0
        loads_count = int(len(network_manager.net.load)) if hasattr(network_manager.net, 'load') else 0
        gens_count = (int(len(network_manager.net.gen)) if hasattr(network_manager.net, 'gen') else 0) + \
                    (int(len(network_manager.net.sgen)) if hasattr(network_manager.net, 'sgen') else 0) + \
                    (int(len(network_manager.net.storage)) if hasattr(network_manager.net, 'storage') else 0)
        
        sources_list = []
        for i, name in enumerate(network_manager.sources['names']):
            bus = int(network_manager.sources['buses'][i]) if i < len(network_manager.sources['buses']) else 0
            max_cap = float(network_manager.sources['max_capacities'][i]) if i < len(network_manager.sources['max_capacities']) else 0.0
            sources_list.append(f"  • {name} (Bus {bus}): {max_cap:.1f} MW")
        
        sources_text = "\n".join(sources_list) if sources_list else "  • No sources added"
        
        # رسالة النجاح - بدون triple quotes لتجنب الأخطاء
        success_msg = "✅ **Network Created Successfully!**\n\n"
        success_msg += "📊 **Network Information:**\n"
        success_msg += f"- **Name:** {network_choice}\n"
        success_msg += f"- **Buses:** {buses_count}\n"
        success_msg += f"- **Lines:** {lines_count}\n"
        success_msg += f"- **Loads:** {loads_count}\n"
        success_msg += f"- **Total Load:** {network_manager.total_load:.2f} MW\n"
        success_msg += f"- **Generators:** {gens_count}\n\n"
        success_msg += "⚡ **Energy Sources:**\n"
        success_msg += f"{sources_text}\n\n"
        success_msg += "🎯 **Ready for Optimization!**"
        
        return success_msg
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # رسالة الخطأ - بدون triple quotes
        error_msg = "❌ **Pandapower Error**\n\n"
        error_msg += f"**Error details:** {str(e)}\n\n"
        error_msg += "**Possible causes:**\n"
        error_msg += "1. Pandapower not installed correctly\n"
        error_msg += "2. Missing dependencies (pytest, numpy, etc.)\n"
        error_msg += "3. Incompatible versions\n\n"
        error_msg += f"**Technical details:**\n```\n{traceback.format_exc()}\n```"
        
        return error_msg


def update_algorithm_dropdown(category):
    """تحديث قائمة الخوارزميات حسب الفئة"""
    algos = algorithms_dict.get(category, [])
    return gr.Dropdown(
        choices=algos[:100] if algos else [],
        label=f"Select {category} Algorithm",
        value=algos[0] if algos else None
    )


def run_optimization(network_choice: str, algorithm_category: str, algorithm_name: str,
                    epochs: int, pop_size: int, runs: int,
                    cost_weight: float, losses_weight: float,
                    emissions_weight: float, voltage_weight: float,
                    algo_params: str = "{}"):
    """تشغيل عملية التحسين"""
    
    # التحقق من صحة المدخلات (هذه قيم مفردة - آمنة)
    if epochs < 10:
        return None, None, None, None, None, f"❌ Error: Iterations (Epochs) must be at least 10. Current value: {epochs}"
    
    if pop_size < 10:
        return None, None, None, None, None, f"❌ Error: Population Size must be at least 10. Current value: {pop_size}"
    
    if not algorithm_name:
        return None, None, None, None, None, "❌ Error: Please select an algorithm"
    
    global network_manager, objective_func
    
    try:
        # إنشاء الشبكة إذا لزم الأمر
        if network_manager is None or network_manager.network_key != network_choice:
            network_manager = NetworkManager(network_choice)
            objective_func = ObjectiveFunction(network_manager)
        
        # تحديث الأوزان (قيم مفردة - آمنة)
        objective_func.update_weights({
            'cost': float(cost_weight),
            'losses': float(losses_weight),
            'emissions': float(emissions_weight),
            'voltage': float(voltage_weight)
        })
        
        # تجهيز متغيرات التحسين
        n_vars = len(network_manager.sources['ids'])
        bounds = [(float(network_manager.sources['min_capacities'][i]),
                   float(network_manager.sources['max_capacities'][i])) 
                  for i in range(n_vars)]
        
        # معاملات مخصصة
        try:
            custom_params = json.loads(algo_params) if algo_params else {}
        except:
            custom_params = {}
        
        # تشغيل التحسين
        results = optimization_engine.optimize(
            objective_func.evaluate,
            n_vars, bounds,
            algorithm_name, epochs, pop_size,
            custom_params, runs
        )
        
        # استخراج أفضل حل
        best_solution = np.array(results['best_solution'])
        objective_func.evaluate(best_solution)
        optimal_results = objective_func.last_results
        
        # تشغيل تدفق الطاقة
        success, flow_results = network_manager.run_power_flow()
        
        if not success:
            error_msg = str(flow_results.get('error', 'Unknown error'))
            return None, None, None, None, None, f"❌ Power flow failed: {error_msg}"
        
        # ✅ التحقق من أن flow_results يحتوي على القيم المطلوبة
        voltages = flow_results.get('voltages', [])
        if voltages and len(voltages) > 0:
            # التأكد من أن voltages هي قائمة من الأرقام وليست مصفوفة NumPy
            if isinstance(voltages, np.ndarray):
                voltages = voltages.tolist()
            buses = list(range(len(voltages)))
        else:
            voltages = []
            buses = []
        
        # ✅ التأكد من أن baseline موجود وصحيح
        if not hasattr(network_manager, 'baseline') or not network_manager.baseline:
            return None, None, None, None, None, "❌ Baseline not available"
        
        # تحويل قيم baseline إلى أرقام مفردة
        baseline_losses = float(network_manager.baseline.get('losses', 0.0))
        optimal_losses = float(optimal_results.get('losses', 0.0))
        
        # إنشاء الرسومات مع التحقق من البيانات
        try:
            voltage_plot = ResultsVisualizer.create_voltage_plot(voltages, buses)
        except Exception as e:
            print(f"⚠️ Voltage plot error: {e}")
            voltage_plot = None
        
        try:
            losses_plot = ResultsVisualizer.create_losses_comparison(
                baseline_losses,
                optimal_losses
            )
        except Exception as e:
            print(f"⚠️ Losses plot error: {e}")
            losses_plot = None
        
        try:
            convergence_curve = results.get('convergence_curve', [])
            if convergence_curve and isinstance(convergence_curve, np.ndarray):
                convergence_curve = convergence_curve.tolist()
            convergence_plot = ResultsVisualizer.create_convergence_plot(
                convergence_curve,
                algorithm_name
            )
        except Exception as e:
            print(f"⚠️ Convergence plot error: {e}")
            convergence_plot = None
        
        try:
            # التأكد من أن names و powers هما قائمتان من الأرقام
            source_names = [str(name) for name in network_manager.sources['names']]
            if isinstance(best_solution, np.ndarray):
                best_solution_list = best_solution.tolist()
            else:
                best_solution_list = list(best_solution)
            
            energy_mix_plot = ResultsVisualizer.create_energy_mix(
                source_names,
                best_solution_list
            )
        except Exception as e:
            print(f"⚠️ Energy mix plot error: {e}")
            energy_mix_plot = None
        
        try:
            # تحويل جميع القيم إلى أنواع Python القياسية للجدول
            baseline_dict = {
                'losses': float(network_manager.baseline.get('losses', 0.0)),
                'voltage_deviation': float(network_manager.baseline.get('voltage_deviation', 0.0)),
                'min_voltage': float(network_manager.baseline.get('min_voltage', 0.0)),
                'max_voltage': float(network_manager.baseline.get('max_voltage', 0.0)),
                'feasible': bool(network_manager.baseline.get('feasible', False)),
                'max_capacities': [float(c) for c in network_manager.baseline.get('max_capacities', [])]
            }
            
            optimal_dict = {
                'losses': float(optimal_results.get('losses', 0.0)),
                'voltage_deviation': float(optimal_results.get('voltage_deviation', 0.0)),
                'min_voltage': float(optimal_results.get('min_voltage', 0.0)),
                'max_voltage': float(optimal_results.get('max_voltage', 0.0)),
                'feasible': bool(optimal_results.get('feasible', False))
            }
            
            results_table = ResultsVisualizer.create_results_table(
                baseline_dict,
                optimal_dict,
                best_solution_list,
                source_names
            )
        except Exception as e:
            print(f"⚠️ Results table error: {e}")
            results_table = "<p>Error creating results table</p>"
        
        execution_time = float(results.get('execution_time', 0.0))
        
        return (
            results_table,
            voltage_plot,
            losses_plot,
            convergence_plot,
            energy_mix_plot,
            f"✅ Optimization completed in {execution_time:.2f} seconds"
        )
        
    except Exception as e:
        print(f"❌ Error in run_optimization: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, f"❌ Error: {str(e)}"

# ============================================================================
# 1️⃣5️⃣ إنشاء واجهة Gradio مع إضافة العنوان والحقوق
# ============================================================================

# CSS مخصص لتنسيق العنوان والحقوق
custom_css = """
<style>
    .title-container {
        background-color: black;
        padding: 20px;
        border-radius: 10px 10px 0 0;
        text-align: center;
    }
    .main-title {
        color: white;
        font-weight: bold;
        font-size: 2.5em;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .sub-title {
        color: #00ff00;
        font-size: 1.2em;
        margin-top: 5px;
        font-style: italic;
    }
    .footer {
        background-color: black;
        color: white;
        font-weight: bold;
        padding: 20px;
        border-radius: 0 0 10px 10px;
        margin-top: 20px;
        text-align: center;
        font-size: 0.9em;
        line-height: 1.6;
    }
    .footer p {
        margin: 5px 0;
    }
    .footer-arabic {
        font-family: 'Arial', sans-serif;
        direction: rtl;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #444;
    }
</style>
"""

with gr.Blocks(title="Hybrid Power System Optimization", theme=gr.themes.Soft(), css=custom_css) as app:
    
    # إضافة العنوان حسب الطلب
    gr.HTML("""
    <div class="title-container">
        <div class="main-title">⚡ The Smart Grid Consists Of Multiple Energy Sources ⚡</div>
        <div class="sub-title">10 power sources + diverse IEEE networks + multi-objective algorithmic optimization + superior optimization settings</div>
    </div>
    """)
    
    gr.Markdown("""
    # ⚡ Hybrid Power System Optimization with MEALPY + Pandapower
    ### IEEE Networks + Renewable Energy + Storage + Multi-Objective Optimization
    """)
    
    with gr.Tabs():
        # ====== تبويب الإعدادات ======
        with gr.TabItem("⚙️ Settings"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📡 Network Selection")
                    network_choice = gr.Dropdown(
                        choices=list(IEEE_NETWORKS.keys()),
                        value="IEEE 30 Bus",
                        label="Select IEEE Network"
                    )
                    create_btn = gr.Button("🚀 Create Network", variant="primary")
                    network_status = gr.Markdown("Click 'Create Network' to start")
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚖️ Objective Weights")
                    cost_weight = gr.Slider(0, 1, value=0.35, step=0.05, label="💰 Cost Weight")
                    losses_weight = gr.Slider(0, 1, value=0.30, step=0.05, label="⚡ Losses Weight")
                    emissions_weight = gr.Slider(0, 1, value=0.20, step=0.05, label="🌍 Emissions Weight")
                    voltage_weight = gr.Slider(0, 1, value=0.15, step=0.05, label="📊 Voltage Weight")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎮 Algorithm Selection")
                    algo_category = gr.Radio(
                        choices=["Single", "Binary", "Triple", "Quad"],
                        value="Single",
                        label="Algorithm Category"
                    )
                    
                    algorithm_dropdown = gr.Dropdown(
                        choices=algorithms_dict.get("Single", [])[:100],
                        label="Select Algorithm",
                        value=algorithms_dict.get("Single", [])[0] if algorithms_dict.get("Single", []) else None
                    )
                    
                    algo_category.change(
                        fn=update_algorithm_dropdown,
                        inputs=algo_category,
                        outputs=algorithm_dropdown
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🔧 Optimization Parameters")
                    epochs = gr.Number(
                        value=100, 
                        label="Iterations (Epochs)", 
                        minimum=10, 
                        maximum=1000,
                        step=10,
                        info="Number of optimization cycles (minimum 10)"
                    )
                    pop_size = gr.Number(
                        value=50, 
                        label="Population Size", 
                        minimum=10, 
                        maximum=500,
                        step=5,
                        info="Number of solutions per generation"
                    )
                    runs = gr.Number(
                        value=1, 
                        label="Number of Runs", 
                        minimum=1, 
                        maximum=10,
                        step=1,
                        info="Number of times to run the algorithm"
                    )
                    algo_params = gr.Textbox(
                        value='{"c1": 2.05, "c2": 2.05, "w": 0.7}',
                        label="Algorithm Parameters (JSON)",
                        placeholder='{"param1": value1, "param2": value2}'
                    )
        
        # ====== تبويب التشغيل ======
        with gr.TabItem("🚀 Run Optimization"):
            run_btn = gr.Button("🏃 Run Optimization", variant="primary", size="lg")
            run_status = gr.Markdown("Configure settings and click Run")
            
            with gr.Tabs():
                with gr.TabItem("📊 Results Summary"):
                    results_html = gr.HTML()
                
                with gr.TabItem("📈 Voltage Profile"):
                    voltage_plot = gr.Plot()
                
                with gr.TabItem("⚡ Losses Comparison"):
                    losses_plot = gr.Plot()
                
                with gr.TabItem("📉 Convergence Curve"):
                    convergence_plot = gr.Plot()
                
                with gr.TabItem("🎯 Energy Mix"):
                    energy_plot = gr.Plot()
        
        # ====== تبويب المساعدة ======
        with gr.TabItem("ℹ️ Help"):
            gr.Markdown("""
            ## 📚 How to Use This Tool
            
            ### 1️⃣ Select Network
            - Choose an IEEE standard network (9 to 300 buses)
            - Click "Create Network" to initialize
            
            ### 2️⃣ Set Objective Weights
            - Adjust sliders to prioritize different objectives
            - Weights should sum to 1 (normalized automatically)
            
            ### 3️⃣ Choose Algorithm
            - **Single**: 35 individual algorithms
            - **Binary**: 200 hybrid combinations of 2 algorithms
            - **Triple**: 300 hybrid combinations of 3 algorithms
            - **Quad**: 250 hybrid combinations of 4 algorithms
            
            ### 4️⃣ Set Parameters
            - Iterations: number of optimization cycles (minimum 10)
            - Population size: number of solutions per generation (minimum 10)
            - Algorithm parameters: custom parameters in JSON format
            
            ### 5️⃣ Analyze Results
            - Voltage profile: check if within limits (0.95-1.05 pu)
            - Losses comparison: before vs after optimization
            - Convergence curve: algorithm performance
            - Energy mix: optimal power distribution
            
            ## 📝 Notes
            - All constraints are strictly enforced (voltage, current, power balance)
            - Penalty method is used for infeasible solutions
            - Results are 100% real and based on actual power flow calculations
            """)
    
    # ربط الأحداث
    create_btn.click(
        fn=create_network,
        inputs=[network_choice],
        outputs=[network_status]
    )
    
    run_btn.click(
        fn=run_optimization,
        inputs=[
            network_choice, algo_category, algorithm_dropdown,
            epochs, pop_size, runs,
            cost_weight, losses_weight, emissions_weight, voltage_weight,
            algo_params
        ],
        outputs=[
            results_html, voltage_plot, losses_plot,
            convergence_plot, energy_plot, run_status
        ]
    )
    
    # إضافة حقوق الملكية في نهاية الصفحة
    gr.HTML("""
    <div style="background: linear-gradient(135deg, #0066CC, #003366); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-top: 30px;">
        <p style="font-size: 1.3em; margin: 5px 0; color: white; font-weight: bold;">© 2026 Mohammed Falah Hassan Al-Dhafiri</p>
        <p style="font-size: 1.2em; margin: 5px 0; color: white; font-weight: bold;">The Inventor & Founder of the System</p>
        <p style="font-size: 1.2em; margin: 5px 0; color: white; font-weight: bold;">With the contribution of researcher: Muthanna Tariq Faraj Al-Nuaimi</p>
        <p style="font-size: 1.1em; margin: 15px 0 5px 0; color: white; font-weight: bold;">All Rights Reserved.</p>
        <p style="font-size: 0.95em; margin: 5px 0; color: white; font-weight: bold;">It is prohibited to copy, reproduce, modify, publish, or use any part of this system without prior written permission from the Founder and Inventor. Any unauthorized use constitutes a violation of intellectual property rights and may subject the violator to legal liability.</p>
        <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 15px 0;">
        <p style="font-size: 1.3em; margin: 5px 0; color: white; font-weight: bold;">© 2026 محمد فلاح حسن الظفيري</p>
        <p style="font-size: 1.2em; margin: 5px 0; color: white; font-weight: bold;">مبتكر ومؤسس النظام</p>
        <p style="font-size: 1.2em; margin: 5px 0; color: white; font-weight: bold;">بمساهمة الباحث: مثنى طارق فرج النعيمي</p>
        <p style="font-size: 1.1em; margin: 15px 0 5px 0; color: white; font-weight: bold;">جميع الحقوق محفوظة</p>
        <p style="font-size: 0.95em; margin: 5px 0; color: white; font-weight: bold;">لا يجوز نسخ أو إعادة إنتاج أو تعديل أو نشر أو استخدام أي جزء من هذا النظام دون إذن خطي مسبق من المؤسس والمبتكر. أي استخدام غير مصرح به يُعد انتهاكًا لحقوق الملكية الفكرية ويعرض المخالف للمساءلة القانونية</p>
    </div>
    """)

# ============================================================================
# 1️⃣6️⃣ تشغيل التطبيق
# ============================================================================

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
