import unittest
import os
import pytest
import pickle
from mydb import *

@pytest.fixture
def db_file():
    fName = "test_db.db"
    
    #Set Up
    if os.path.isfile(fName):
        os.remove(fName)
    #yields fName to test function
    yield fName
    
    #Tear Down
    if os.path.isfile(fName):
        os.remove(fName)

def describe_MyDB():
    def describe_Init():
        
        def test_init_file_that_DNE(db_file):
            testDB = MyDB(db_file)
            assert os.path.isfile(db_file)
            assert testDB.loadStrings() == []
        
        def test_init_file_that_exists(db_file):
            testDB1 = MyDB(db_file)
            testDB1.saveString("hello")
            assert testDB1.loadStrings(),["hello"]
            testDB2 = MyDB(db_file)
            assert os.path.isfile(db_file)
            assert testDB2.loadStrings() == ["hello"]
    
    def describe_load_strings():
        def test_loads_strings_from_empty_file(db_file):
            testDB = MyDB(db_file)
            assert testDB.loadStrings() == []

        def test_loads_one_string(db_file):
            testDB = MyDB(db_file)
            testDB.saveString("hello")
            assert testDB.loadStrings() == ["hello"]

        def test_loads_multiple_strings(db_file):
            testDB = MyDB(db_file)
            strings = ["hello","my","name","is","Justin"]
            testDB.saveStrings(strings)
            assert testDB.loadStrings() == strings

        def test_load_strings_with_only_integers(db_file):
            testDB = MyDB(db_file)
            with open (db_file,'wb') as f:
                pickle.dump([0,1,2,3,4,5],f)
            assert testDB.loadStrings() == [0,1,2,3,4,5]
    
    def describe_save_string():
        def test_save_string_with_empty_file(db_file):
            testDB = MyDB(db_file)
            testDB.saveString("hello")
            assert testDB.loadStrings() == ["hello"]
            
        def test_save_string_with_unempty_file(db_file):
            testDB = MyDB(db_file)
            strings = ["hello","world","I'm","here"]
            testDB.saveStrings(strings)
            assert testDB.loadStrings() == strings
            testDB.saveString("Hi")
            assert testDB.loadStrings() == strings + ["Hi"]

    def describe_save_strings():
        def test_save_strings_with_empty_file(db_file):
            testDB = MyDB(db_file)
            strings = ["hello","world","I'm","here"]
            testDB.saveStrings(strings)
            assert testDB.loadStrings() == strings

        def test_save_strings_with_unempty_file(db_file):
            testDB = MyDB(db_file)
            strings1 = ["hello","world","I'm","here"]
            testDB.saveStrings(strings1)
            assert testDB.loadStrings() == strings1
            strings2 = ["hi","my","name","is","Justin"]
            testDB.saveStrings(strings2)
            assert testDB.loadStrings() == strings2        
