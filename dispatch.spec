# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis([
	r'bin\dispatch.py',
	r'scripts\windows\windows.py',
    r'scripts\windows\journalist.py',
    r'scripts\windows\contact.py',
    r'scripts\svn\SVNCheck.py',
    r'scripts\prettyCode\prettyPrint.py',
    r'scripts\game\update.py',
    r'scripts\game\gameControl.py',
    r'scripts\dataAnalysis\abacus.py',
    r'scripts\dataMining\miner.py'
],
             pathex=['C:\\Users\\Administrator\\Documents\\组内测试开发\\脚本\\李典凯\\AutoCheckSubmitOrder'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='QQ游戏',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='data\\ico\\ico64.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='bin')
