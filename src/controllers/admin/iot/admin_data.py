from entities.iot.Data import Data, NumericData, StringData

def get_datas(current_user, db):
    data = Data.getAllData(db)
    return data

def get_numeric_data(current_user, db):
    data = NumericData.getAllNumericData(db)
    return data

def get_string_data(current_user, db):
    data = StringData.getAllStringData(db)
    return data
