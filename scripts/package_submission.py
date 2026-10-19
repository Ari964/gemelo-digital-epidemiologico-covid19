import os
import subprocess
import shutil
import hashlib
from pathlib import Path

def create_packages():
    project_dir = Path(r"d:\X CICLO\TRABAJO DE INVESTIGACIÓN\SEMANA 2\GD_TI").resolve()
    parent_dir = project_dir.parent
    rar_exe = Path(r"C:\Program Files\WinRAR\Rar.exe")
    
    # Nombre canónico único del entregable
    final_rar_name = "GD_TI_Final_Verificado.rar"
    rar_path_local = project_dir / final_rar_name
    rar_path_parent = parent_dir / final_rar_name
    exclude_file = project_dir / "rar_exclude.txt"
    
    # Limpieza de paquetes antiguos redundantes en el directorio local y padre
    old_patterns = [
        "GD_TI_Actualizado*.rar",
        "GD_TI_Final_Verificado*.rar",
        "test*.rar",
        "*.bak"
    ]
    for p in [project_dir, parent_dir]:
        for pat in old_patterns:
            for old_f in p.glob(pat):
                try:
                    old_f.unlink()
                    print(f"[CLEANUP] Archivo anterior removido: {old_f.name}")
                except Exception as e:
                    print(f"[WARN] No se pudo eliminar {old_f}: {e}")

    print(f"\nEmpaquetando entrega final canónica desde {project_dir}...")
    
    # Exclusiones estándar para distribución académica limpia y reproducible
    excl_content = """node_modules
node_modules/*
*/node_modules/*
.venv
.venv/*
*/.venv/*
.git
.git/*
*/.git/*
dist
dist/*
*/dist/*
__pycache__
*__pycache__*
.pytest_cache
*.pytest_cache*
.tempmediaStorage
*clean_extraction_test*
*.log
*.rar
*.zip
*.bak
test_out.rar
rar_exclude.txt
"""
    exclude_file.write_text(excl_content, encoding="utf-8")
    
    cmd = [
        str(rar_exe),
        "a",
        "-r",
        "-m5",  # Compresión máxima
        f"-x@{exclude_file.name}",
        str(rar_path_local),
        "*"
    ]
    
    print("Ejecutando compresión WinRAR (Rar.exe a -r -m5)...")
    res = subprocess.run(cmd, cwd=str(project_dir), capture_output=True, text=True)
    
    # Eliminar archivo temporal de exclusiones
    if exclude_file.exists():
        exclude_file.unlink()
        
    if res.returncode in (0, 1) and rar_path_local.exists():
        print(f"\n[OK] Archivo RAR único generado con éxito: {rar_path_local}")
        
        # Test de integridad del archivo RAR
        test_res = subprocess.run([str(rar_exe), "t", str(rar_path_local)], capture_output=True, text=True)
        if test_res.returncode == 0:
            print("[INTEGRIDAD VERIFICADA] WinRAR test archive (rar t): 100% OK sin errores de CRC.")
        else:
            print(f"[ALERTA] Fallo en test de archivo RAR: {test_res.stderr}")

        # Copia al directorio padre para conveniencia del evaluador
        shutil.copy2(rar_path_local, rar_path_parent)
        print(f"[OK] Copia sincronizada en directorio superior: {rar_path_parent}")

        size_mb = rar_path_local.stat().st_size / (1024 * 1024)
        
        # Calcular SHA-256
        with open(rar_path_local, "rb") as rf:
            rar_sha = hashlib.sha256(rf.read()).hexdigest()

        print(f"\n" + "=" * 80)
        print("FICHA DEL ENTREGABLE ÚNICO FINAL (GD_TI)")
        print("=" * 80)
        print(f"Archivo Local:    {rar_path_local}")
        print(f"Archivo Superior: {rar_path_parent}")
        print(f"Tamaño:           {size_mb:.2f} MB ({rar_path_local.stat().st_size:,} bytes)")
        print(f"SHA-256 Checksum: {rar_sha}")
        print("=" * 80)
    else:
        print(f"[ERROR] Fallo al crear RAR: {res.stderr}")
        print("Salida:", res.stdout)

if __name__ == "__main__":
    create_packages()
