import pyodbc
from flask import Flask, render_template
from flask import request
from config import DB_CONFIG

def get_db_connection():
  conn_str = f"DRIVER={DB_CONFIG['DRIVER']};SERVER={DB_CONFIG['SERVER']};DATABASE={DB_CONFIG['DATABASE']};UID={DB_CONFIG['UID']};PWD={DB_CONFIG['PWD']}"
  conn = pyodbc.connect(conn_str)
  return conn

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('index.html')

def getIdFabric(cursor, id):
  cursor.execute("SELECT ID, TRANG_THAI FROM DANH_SACH_CUON_VAI WHERE ID = ? AND TRANG_THAI IN (N'Nhập kho',N'Xả vải')", id)
  row = cursor.fetchone()
  return row

def getFabricPallet(cursor, pallet):
  cursor.execute("SELECT ID, TRANG_THAI FROM DANH_SACH_CUON_VAI WHERE PALLET = ?", pallet)
  rows = cursor.fetchall()
  return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

def updateStatusFabric(cursor, id, status):
  cursor.execute("UPDATE DANH_SACH_CUON_VAI SET TRANG_THAI = ? WHERE ID = ?", status, id)
  cursor.commit()

@app.route('/updateLocation', methods=['POST'])
def updateLocation():
  data = request.get_json()
  id = data['id']
  location = data['location']
  function = data['function']
  conn = get_db_connection()
  cursor = conn.cursor()
  # Check id
  if (function == "0" or function == "1"):
    row = getIdFabric(cursor, id)
    if not row:
      conn.close()
      return "ID của cuộn vải không hợp lệ", 404
    
    if row[1] not in ("Nhập kho", "Xả vải"):
      conn.close()
      return "Trạng thái của cuộn vải id={} không thể thay đổi vị trí.".format(id), 422
    
    # Update
    if function == "0":
      cursor.execute("SELECT VI_TRI FROM DANH_SACH_CUON_VAI WHERE PALLET = ?", location)
      palletRow = cursor.fetchone()
      if palletRow:
        cursor.execute("UPDATE DANH_SACH_CUON_VAI SET PALLET = ?, VI_TRI = ? WHERE ID = ?", location, palletRow[0], id)
      else:
        cursor.execute("UPDATE DANH_SACH_CUON_VAI SET PALLET = ? WHERE ID = ?", location, id)
      conn.commit()
      conn.close()
    else:
      cursor.execute("UPDATE DANH_SACH_CUON_VAI SET VI_TRI = ? WHERE ID = ?", location, id)
      conn.commit()
      conn.close()
  else:
    rows = getFabricPallet(cursor, id)
    if not rows:
      conn.close()
      return "ID của cuộn vải không hợp lệ", 404
    
    for row in rows:
      if row['TRANG_THAI'] not in ("Nhập kho", "Xả vải"):
        conn.close()
        return "Trạng thái của cuộn vải id={} không thể thay đổi vị trí.".format(id), 422
      
    # Update
    if function == "2":
      cursor.execute("UPDATE DANH_SACH_CUON_VAI SET VI_TRI = ? WHERE ID IN (SELECT ID FROM DANH_SACH_CUON_VAI WHERE PALLET = ?)", location, id)
      conn.commit()
  
  return "Cập nhật thành công", 200

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=86)
