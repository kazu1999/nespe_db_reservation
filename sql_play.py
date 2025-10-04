from utils.db_utils import DBUtils
from connection import get_connection
import pprint

building_id = '3760'
#print("Fetching WakuPattern for building_id:")
#print(building_id)
#print(type(building_id))

#row = DBUtils.execute_single_query(connection, "SELECT WakuPattern FROM tSettingM WHERE ClientCD = %s", (building_id))
#print(row)


conn = get_connection()

with conn.cursor() as cursor:
    sql = """
        SELECT ClientCD, WakuPattern
        FROM tSettingM
        WHERE ClientCD = 3760
    """
    #cursor.execute(f"SELECT WakuPattern FROM tSettingM WHERE ClientCD = {building_id}")
    cursor.execute(sql)
    result = cursor.fetchall()
    pprint.pprint(result)