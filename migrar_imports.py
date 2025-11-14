import os
import re
from pathlib import Path

class ImportMigrator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.files_updated = []
        self.errors = []
    
    def migrate_file(self, file_path):
        """Migra los imports de un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrones a buscar y reemplazar
            patterns = [
                # from database import db
                (r'from\s+database\.conexion\s+import\s+([^\n]+)', r'from database import \1'),
                
                # from database import db as db
                (r'import\s+database\.conexion\s+as\s+(\w+)', r'from database import db as \1'),
                
                # import database
                (r'from\s+database\s+import\s+conexion', r'import database'),
                
                # database.db
                (r'database\.conexion\.(\w+)', r'database.\1')
            ]
            
            original_content = content
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_updated.append(str(file_path))
                return True
            
            return False
            
        except Exception as e:
            self.errors.append(f"❌ Error en {file_path}: {e}")
            return False
    
    def find_python_files(self):
        """Encuentra todos los archivos Python en el proyecto"""
        python_files = []
        for root, dirs, files in os.walk(self.base_dir):
            # Excluir carpetas específicas
            if '__pycache__' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def run_migration(self):
        """Ejecuta la migración completa"""
        print("🔄 INICIANDO MIGRACIÓN DE IMPORTS...")
        print("=" * 50)
        
        python_files = self.find_python_files()
        print(f"📁 Encontrados {len(python_files)} archivos Python")
        
        migrated_count = 0
        for file_path in python_files:
            if self.migrate_file(file_path):
                migrated_count += 1
                print(f"✅ Actualizado: {file_path.relative_to(self.base_dir)}")
        
        print("=" * 50)
        print(f"🎉 MIGRACIÓN COMPLETADA")
        print(f"📄 Archivos actualizados: {migrated_count}")
        print(f"❌ Errores: {len(self.errors)}")
        
        if self.errors:
            print("\n--- ERRORES ---")
            for error in self.errors:
                print(error)
        
        # Mostrar resumen de cambios
        print("\n--- RESUMEN DE CAMBIOS ---")
        print("Los imports se cambiaron de:")
        print("  from database import db")
        print("  from database import db as db")
        print("A:")
        print("  from database import db")
        print("  from database import get_db_connection")

if __name__ == "__main__":
    migrator = ImportMigrator()
    migrator.run_migration()