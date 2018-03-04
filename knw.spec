# -*- mode: python -*-

block_cipher = None


a = Analysis(['knw.py'],
<<<<<<< HEAD
             pathex=['V:\\tim\\Documents\\code\\dev\\KN'],
=======
             pathex=['V:\\Users\\tim\\Documents\\code\\dev\\KN'],
>>>>>>> c4a1de0608a0c26a7c11d9e9b74f187df3b6f89a
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='knw',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
