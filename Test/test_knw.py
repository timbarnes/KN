# Tests for knm
import sys
import os
import glob
import shutil
import filecmp
import wx
import pytest
sys.path.insert(0, '..')
import knm
import knw


def setup():
    shutil.copyfile('testfile2 keynotes_original.xlsx',
                    'testfile2 keynotes.xlsx')
    shutil.copyfile('singlecat keynotes_original.xlsx',
                    'singlecat keynotes.xlsx')


def test_application():
    a = wx.App()
    app = knw.Application()
    assert f'{type(app)}' == "<class 'knw.Application'>"
    assert app.categoryNotebook is None
    assert app.keynoteFile is None
    assert app.inactiveHidden is False
    assert app.fileEdited is False
    assert f'{type(app.panel)}' == "<class 'wx._core.Panel'>"
    assert f'{type(app.commands)}' == "<class 'wx._core.BoxSizer'>"
    app.keynoteFile = knm.keynoteFile()
    assert os.path.isfile('testfile2 keynotes.xlsx')
    app.keynoteFile.load('testfile2 keynotes.xlsx', 'Excel')
    print(app.__dict__)
    # assert app.currentCategory == 'General'
    kf = app.keynoteFile
    assert kf is not None
    assert kf.fileName == 'testfile2 keynotes.xlsx'
    assert os.path.isfile(kf.lockedName(kf.fileName))
    assert len(kf.categories) == 5
    for i in range(5):
        assert kf.categories[i].number == i
    assert kf.categories[2].name == 'Floor'
    for i, n in zip(range(5), [7, 18, 9, 7, 7]):
        assert len(kf.categories[i].keynotes) == n
        assert kf.categories[i].demoKeynotes[0].number == 1
        assert kf.categories[i].existingKeynotes[0].number == 1
        assert kf.categories[i].newKeynotes[0].number == 1
    assert kf.categories[4].demoKeynotes[1].text == 'Demo 2'
    assert kf.categories[4].demoKeynotes[1].disabled is True
    app.onSaveTxt(0)  # Should be passed an EventObject
    app.onSaveXlsx(0)
    assert filecmp.cmp('testfile2 keynotes.txt', 'testfile2 keynotes_original.txt')
    app.onClose()
    assert app.keynoteFile is None
    assert os.path.isfile('testfile2 keynotes.xlsx')
    # Load a new one
    app.keynoteFile = knm.keynoteFile()
    assert os.path.isfile('singlecat keynotes.xlsx')
    app.keynoteFile.load('singlecat keynotes.xlsx', 'Excel')
    kf = app.keynoteFile
    assert kf is not None
    assert kf.fileName == 'singlecat keynotes.xlsx'
    assert os.path.isfile(kf.lockedName(kf.fileName))
    assert len(kf.categories) == 1
    assert kf.categories[0].name == 'General'
    print(len(kf.categories[0].keynotes))
    assert len(kf.categories[0].keynotes) == 8
    assert kf.categories[0].existingKeynotes[0].disabled is True
    app.onSaveTxt(0)  # Should be passed an EventObject
    app.onSaveXlsx(0)
    assert filecmp.cmp('singlecat keynotes.txt', 'singlecat keynotes_original.txt')
    app.onClose()
    assert os.path.isfile('singlecat keynotes.xlsx')


def teardown():
    if os.path.isfile('testfile2 keynotes_tim.xlsx'):
        os.remove('testfile2 keynotes_tim.xlsx')
    for f in glob.glob('testfile2 keynotes.xlsx.*'):
        os.remove(f)
    if os.path.isfile('singlecat keynotes_tim.xlsx'):
        os.remove('singlecat keynotes_tim.xlsx')
    for f in glob.glob('singlecat keynotes.xlsx.*'):
        os.remove(f)
