# -*- mode: python ; coding: utf-8 -*-


# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/modules', 'modules'),
        ('src/assets', 'assets'),
        ('src/database', 'database'),
        ('docs', 'docs'),
        ('config.py', '.')
    ],
    hiddenimports=[
        'modules',
        'modules.dashboard.dashboard_main',
        'modules.ajustes.ajustes_main',
        'modules.ventas.ventas_main',
        'modules.utils.logger',
        'modules.utils.login_ui',
        'modules.utils.app_paths',
        'modules.utils.usuario_manager',
        'modules.utils.license_manager',
        'modules.utils.tour_state_manager',
        'database',
        'database.connection',
        'database.database'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FincaFacil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src/assets/Logo.ico'],
)
