# Tests for knm
import sys
import os
import pytest
sys.path.insert(0, '..')
import knm


kf = None  # Handle for keynoteFile


def setup():
    global kf
    kf = knm.keynoteFile()
    kf.load('testfile2.xlsx', 'Excel')


def test_load():
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
