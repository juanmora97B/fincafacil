#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validación Post-Seed
Verifica integridad de BD, registros huérfanos, y genera reporte completo

Uso:
    python scripts/validate_seed.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import sqlite3
import logging
from database import get_db_connection
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/validate_seed.log")
    ]
)
logger = logging.getLogger(__name__)


class SeedValidator:
    """Validador completo de datos post-seed."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def validate_all(self) -> bool:
        """Ejecuta validación completa."""
        logger.info("=" * 70)
        logger.info("🔍 INICIANDO VALIDACIÓN POST-SEED")
        logger.info("=" * 70)
        
        try:
            self.count_records()
            self.check_foreign_keys()
            self.check_animal_consistency()
            self.check_production_data()
            self.check_reproduction_data()
            self.check_health_data()
            
            self.print_report()
            
            success = len(self.errors) == 0
            logger.info("=" * 70)
            if success:
                logger.info("✅ VALIDACIÓN COMPLETADA SIN ERRORES")
            else:
                logger.warning(f"❌ VALIDACIÓN ENCONTRÓ {len(self.errors)} ERRORES")
            logger.info("=" * 70)
            
            return success
            
        except Exception as e:
            logger.error(f"Error crítico en validación: {e}", exc_info=True)
            return False
    
    def count_records(self):
        """Cuenta registros por tabla."""
        logger.info("📊 Contando registros...")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                tables = [
                    'animal', 'finca', 'potrero', 'lote', 'raza', 'vendedor',
                    'servicio', 'reproduccion', 'tratamiento', 'peso',
                    'produccion_leche', 'muerte', 'insumo', 'movimiento_insumo',
                    'herramienta', 'mantenimiento_herramienta'
                ]
                
                total = 0
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    self.stats[table] = count
                    total += count
                    if count > 0:
                        logger.info(f"  ✓ {table:.<30} {count:>5} registros")
                
                logger.info(f"\n  TOTAL: {total} registros")
                
                # Validar conteos esperados
                expected = {
                    'animal': (30, 50),  # 30-50 animales
                    'finca': (1, 5),      # Al menos 1 finca
                    'potrero': (3, 15),   # Al menos 3 potreros
                    'servicio': (5, 20),  # Servicios reproductivos
                    'produccion_leche': (100, 1000),  # Registros de leche
                }
                
                for table, (min_val, max_val) in expected.items():
                    count = self.stats.get(table, 0)
                    if count < min_val:
                        self.warnings.append(
                            f"⚠️ {table}: {count} registros (esperados: mín {min_val})"
                        )
                    elif count > max_val:
                        self.warnings.append(
                            f"⚠️ {table}: {count} registros (esperados: máx {max_val})"
                        )
        
        except Exception as e:
            self.errors.append(f"Error contando registros: {e}")
    
    def check_foreign_keys(self):
        """Valida integridad de claves foráneas."""
        logger.info("\n🔗 Validando claves foráneas...")
        
        fk_checks = [
            ("animal", "id_finca", "finca", "id"),
            ("animal", "raza_id", "raza", "id"),
            ("animal", "id_potrero", "potrero", "id"),
            ("animal", "lote_id", "lote", "id"),
            ("animal", "id_madre", "animal", "id"),
            ("animal", "id_padre", "animal", "id"),
            ("servicio", "id_hembra", "animal", "id"),
            ("servicio", "id_macho", "animal", "id"),
            ("tratamiento", "id_animal", "animal", "id"),
            ("peso", "animal_id", "animal", "id"),
            ("produccion_leche", "animal_id", "animal", "id"),
            ("muerte", "animal_id", "animal", "id"),
            ("potrero", "id_finca", "finca", "id"),
            ("insumo", "id_finca", "finca", "id"),
            ("herramienta", "id_finca", "finca", "id"),
        ]
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                for table, fk_col, ref_table, ref_col in fk_checks:
                    cur.execute(f"""
                        SELECT COUNT(*) FROM {table}
                        WHERE {fk_col} IS NOT NULL 
                        AND {fk_col} NOT IN (SELECT {ref_col} FROM {ref_table})
                    """)
                    count = cur.fetchone()[0]
                    if count > 0:
                        error_msg = f"❌ {table}.{fk_col} → {ref_table}.{ref_col}: {count} registros huérfanos"
                        self.errors.append(error_msg)
                        logger.error(f"  {error_msg}")
                    else:
                        logger.info(f"  ✓ {table}.{fk_col} → {ref_table}.{ref_col}")
        
        except Exception as e:
            self.errors.append(f"Error validando FKs: {e}")
    
    def check_animal_consistency(self):
        """Valida consistencia de animales."""
        logger.info("\n🐄 Validando animales...")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Animales sin finca
                cur.execute("SELECT COUNT(*) FROM animal WHERE id_finca IS NULL")
                count = cur.fetchone()[0]
                if count > 0:
                    self.warnings.append(f"⚠️ {count} animales sin finca asignada")
                
                # Distribución por sexo
                cur.execute("SELECT sexo, COUNT(*) FROM animal GROUP BY sexo")
                for sexo, count in cur.fetchall():
                    logger.info(f"  ✓ Animales {sexo}: {count}")
                
                # Distribución por estado
                cur.execute("SELECT estado, COUNT(*) FROM animal GROUP BY estado")
                for estado, count in cur.fetchall():
                    logger.info(f"  ✓ Animales {estado}: {count}")
        
        except Exception as e:
            self.errors.append(f"Error validando animales: {e}")
    
    def check_production_data(self):
        """Valida datos de producción de leche."""
        logger.info("\n🥛 Validando producción de leche...")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Total litros
                cur.execute("""
                    SELECT SUM(litros_manana + litros_tarde + litros_noche) as total_litros
                    FROM produccion_leche
                """)
                total = cur.fetchone()[0] or 0
                logger.info(f"  ✓ Total litros registrados: {total:.2f}L")
                
                # Registros sin animal
                cur.execute("""
                    SELECT COUNT(*) FROM produccion_leche
                    WHERE animal_id NOT IN (SELECT id FROM animal)
                """)
                count = cur.fetchone()[0]
                if count > 0:
                    self.errors.append(f"❌ {count} registros de leche sin animal válido")
                
                # Promedio por animal
                cur.execute("""
                    SELECT COUNT(DISTINCT animal_id) as hembras
                    FROM produccion_leche
                """)
                hembras = cur.fetchone()[0]
                logger.info(f"  ✓ Hembras con registro de leche: {hembras}")
        
        except Exception as e:
            self.errors.append(f"Error validando producción: {e}")
    
    def check_reproduction_data(self):
        """Valida datos de reproducción."""
        logger.info("\n🤰 Validando reproducción...")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Servicios por estado
                cur.execute("""
                    SELECT estado, COUNT(*) FROM servicio GROUP BY estado
                """)
                for estado, count in cur.fetchall():
                    logger.info(f"  ✓ Servicios {estado}: {count}")
                
                # Servicios sin hembra o macho
                cur.execute("""
                    SELECT COUNT(*) FROM servicio
                    WHERE id_hembra NOT IN (SELECT id FROM animal)
                """)
                count = cur.fetchone()[0]
                if count > 0:
                    self.errors.append(f"❌ {count} servicios con hembra inválida")
                
                # Gestantes
                cur.execute("""
                    SELECT COUNT(*) FROM servicio WHERE estado='Gestante'
                """)
                gestantes = cur.fetchone()[0]
                logger.info(f"  ✓ Gestantes activas: {gestantes}")
        
        except Exception as e:
            self.errors.append(f"Error validando reproducción: {e}")
    
    def check_health_data(self):
        """Valida datos de salud."""
        logger.info("\n🏥 Validando salud...")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Tratamientos activos
                cur.execute("""
                    SELECT COUNT(*) FROM tratamiento WHERE estado='Activo'
                """)
                activos = cur.fetchone()[0]
                logger.info(f"  ✓ Tratamientos activos: {activos}")
                
                # Tratamientos completados
                cur.execute("""
                    SELECT COUNT(*) FROM tratamiento WHERE estado='Completado'
                """)
                completados = cur.fetchone()[0]
                logger.info(f"  ✓ Tratamientos completados: {completados}")
                
                # Tratamientos sin animal
                cur.execute("""
                    SELECT COUNT(*) FROM tratamiento
                    WHERE id_animal NOT IN (SELECT id FROM animal)
                """)
                count = cur.fetchone()[0]
                if count > 0:
                    self.errors.append(f"❌ {count} tratamientos sin animal válido")
        
        except Exception as e:
            self.errors.append(f"Error validando salud: {e}")
    
    def print_report(self):
        """Genera reporte final."""
        logger.info("\n" + "=" * 70)
        logger.info("📋 REPORTE DE VALIDACIÓN")
        logger.info("=" * 70)
        
        # Errores
        if self.errors:
            logger.error(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"   {error}")
        else:
            logger.info("\n✅ NO HAY ERRORES")
        
        # Advertencias
        if self.warnings:
            logger.warning(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"   {warning}")
        else:
            logger.info("\n✅ NO HAY ADVERTENCIAS")
        
        # Resumen de registros
        logger.info("\n📊 RESUMEN DE REGISTROS:")
        for table, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                logger.info(f"   {table:.<35} {count:>5}")
        
        logger.info("\n" + "=" * 70)


def main():
    """Ejecuta validación."""
    validator = SeedValidator()
    success = validator.validate_all()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
