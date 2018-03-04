# Tests for knm
import sys
import os
import glob
import shutil
import filecmp
import pytest
sys.path.insert(0, '..')
import knm


kf = None  # Handle for keynoteFile


def setup():
    shutil.copyfile('testfile2 keynotes_original.xlsx',
                    'testfile2 keynotes.xlsx')


def test_category():
    c = knm.Category(0, 'General')
    assert c is not None
    assert c.number == 0
    assert c.name == 'General'
    assert c.__str__() == 'Category 0: General'
    assert c.keynotes == []
    assert c.demoKeynotes == []
    assert c.existingKeynotes == []
    assert c.newKeynotes == []
    assert c.fullstring == '0\tGeneral'

    with pytest.raises(TypeError):
        c = knm.Category()
    with pytest.raises(TypeError):
        c = knm.Category(1)
    with pytest.raises(TypeError):
        c = knm.Category('Binky')
    with pytest.raises(ValueError):
        c = knm.Category('bar', 12)


def test_keynote():

    c = knm.Category(12, 'Testing')
    k1 = knm.Keynote(kType='E', category=c)
    k2 = knm.Keynote(numString='D1201', kText='Keynote 2',
                     catString='12')
    k3 = knm.Keynote(numString='D1202', kText='Keynote 3',
                     catString='disabled')
    c.addKeynote(k1)
    c.addKeynote(k2)
    c.addKeynote(k3)
    assert k1.number == 1
    assert k1.text == '<Empty>'
    assert not k1.disabled
    assert k2.number == 1
    assert k2.text == 'Keynote 2'
    assert k2.disabled is not True
    assert k3.number == 2
    assert k3.text == 'Keynote 3'
    assert k3.disabled is True
    assert k3.catnum == 12
    assert len(c.keynotes) == 3
    assert c.existingKeynotes[0] == k1
    assert c.demoKeynotes[0] == k2
    assert c.demoKeynotes[0].text == 'Keynote 2'
    assert c.existingKeynotes[0].text == '<Empty>'
    assert c.newKeynotes == []
    assert c.existingKeynotes[0].category == c
    assert c.demoKeynotes[0].category == c
    assert k1.disabled is not True
    assert k3.disabled is True


def test_load():
    kf = knm.keynoteFile()
    kf.load('testfile2 keynotes.xlsx', 'Excel')
    assert os.path.isfile('testfile2 keynotes_tim.xlsx')
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
    assert kf.saveTxt() == (5, 48)
    assert kf.saveXlsx() == (5, 48)
    assert kf.unlockFile(kf.fileName)
    assert filecmp.cmp('testfile2 keynotes.txt',
                       'testfile2 keynotes_original.txt')
    assert kf.fileName is None
    assert kf.categories == []
    kf = knm.keynoteFile()
    assert len(kf.categories) == 0
    assert kf.fileName == None
    kf.load('testfile2 keynotes.xlsx', 'Excel')
    assert os.path.isfile('testfile2 keynotes_tim.xlsx')
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
    assert kf.saveTxt() == (5, 48)
    assert kf.saveXlsx() == (5, 48)
    assert kf.unlockFile(kf.fileName)
    assert filecmp.cmp('testfile2 keynotes.txt',
                       'testfile2 keynotes_original.txt')
    assert kf.fileName is None
    assert kf.categories == []


def teardown():
    if os.path.isfile('testfile2 keynotes_tim.xlsx'):
        os.remove('testfile2_tim.xlsx')
    for f in glob.glob('testfile2 keynotes.xlsx.*'):
        os.remove(f)
