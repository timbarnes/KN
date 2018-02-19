# Tests for knm
import sys
import os
import glob
import shutil
import pytest
sys.path.insert(0, '..')
import knm


kf = None  # Handle for keynoteFile


def setup():
    shutil.copyfile('testfile2_original.xlsx', 'testfile2.xlsx')


def test_category():
    c = knm.Category(0, 'General')
    assert c is not None
    assert c.num == 0
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


def test_load():
    kf = knm.keynoteFile()
    kf.load('testfile2.xlsx', 'Excel')
    assert kf is not None
    assert kf.fileName == 'testfile2.xlsx'
    assert os.path.isfile(kf.lockedName(kf.fileName))
    assert len(kf.categories) == 5
    for i in range(5):
        assert kf.categories[i].num == i
    assert kf.categories[2].name == 'Floor'
    for i, n in zip(range(5), [7, 18, 9, 7, 7]):
        assert len(kf.categories[i].keynotes) == n
    assert kf.categories[4].demoKeynotes[1].text == 'Demo 2'
    assert kf.categories[4].demoKeynotes[1].disabled is True
    assert kf.unlockFile(kf.fileName)
    assert kf.fileName is None
    assert kf.categories is None


def teardown():
    if os.path.isfile('testfile2_tim.xlsx'):
        os.remove('testfile2_tim.xlsx')
    for f in glob.glob('testfile2.xlsx.*'):
        print(f'Removing {f}')
        os.remove(f)
