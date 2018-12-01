# -*- mode: python -*-

block_cipher = None


a = Analysis(['MyPlot.py'],
             pathex=['C:\\Users\\Administrator\\PycharmProjects\\MyPlot\\plot'],
             binaries=[],
             datas=[
                    ('C:\\Users\\Administrator\\PycharmProjects\\MyPlot\\plot\\testdata\\memory.json', 'testdata\\memory.json'),
                    ('C:\\Users\\Administrator\\PycharmProjects\\MyPlot\\plot\\testdata\\power_123.json', 'testdata\\power_123.json')
                    ],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MyPlot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
