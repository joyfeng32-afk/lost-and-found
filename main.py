# main.py FastAPI 极简后端演示Demo
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
import uvicorn
import sqlite3

app = FastAPI(title="LostFound Demo")
conn = sqlite3.connect("./lostfound.db", check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS items
(id INTEGER PRIMARY KEY AUTOINCREMENT,
item_type TEXT,
category TEXT,
area TEXT,
find_time TEXT,
surname TEXT,
id_last4 TEXT,
desc TEXT,
status TEXT DEFAULT 'pending')''')
cur.execute('''CREATE TABLE IF NOT EXISTS claim
(id INTEGER PRIMARY KEY AUTOINCREMENT,
item_id INTEGER,
claim_surname TEXT,
claim_last4 TEXT,
secret_info TEXT,
contact_msg TEXT,
pass_flag INTEGER DEFAULT 0)''')
conn.commit()

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <h2>公益失物招领 Demo</h2>
    <a href="/publish">发布捡到物品</a> | <a href="/search">查找遗失物</a>
    """

@app.get("/publish", response_class=HTMLResponse)
async def publish_page():
    return """
    <form action="/add" method="post">
    物品分类：<select name="category"><option>证件</option><option>钥匙/背包/文件</option></select><br>
    物品类型：<input name="item_type"><br>
    捡到片区：<input name="area"><br>
    捡到时间：<input name="find_time"><br>
    姓氏（证件填）：<input name="surname"><br>
    证件尾4位（可选）：<input name="id_last4"><br>
    外观描述：<textarea name="desc"></textarea><br>
    <button type="submit">提交</button>
    </form>
    """

@app.post("/add")
async def add_item(category:str=Form(),item_type:str=Form(),area:str=Form(),find_time:str=Form(),surname:str=Form(),id_last4:str=Form(),desc:str=Form()):
    cur.execute("INSERT INTO items (category,item_type,area,find_time,surname,id_last4,desc) VALUES (?,?,?,?,?,?,?)",
                (category,item_type,area,find_time,surname,id_last4,desc))
    conn.commit()
    return "<h3>提交成功</h3><a href='/'>返回首页</a>"

@app.get("/search", response_class=HTMLResponse)
async def search_page():
    return """
    <form action="/do_search" method="post">
    丢失片区：<input name="area"><br>
    姓氏：<input name="surname"><br>
    证件尾4位：<input name="id_last4"><br>
    <button type="submit">检索候选</button>
    </form>
    """

@app.post("/do_search", response_class=HTMLResponse)
async def do_search(area:str=Form(),surname:str=Form(),id_last4:str=Form()):
    res = cur.execute("SELECT * FROM items WHERE area LIKE ? AND surname LIKE ? AND id_last4 LIKE ?",
                     (f"%{area}%",f"%{surname}%",f"%{id_last4}%")).fetchall()
    html = "<h3>候选列表</h3>"
    for row in res:
        html += f"<div>ID:{row[0]} | 分类:{row[1]} | 物品:{row[2]} | 片区:{row[3]} | 描述:{row[6]} <br><a href='/claim_form?itemid={row[0]}'>发起认领</a></div>"
    return html

@app.get("/claim_form", response_class=HTMLResponse)
async def claim_form(itemid:int):
    return f"""
    <form action="/submit_claim" method="post">
    <input type="hidden" name="item_id" value="{itemid}">
    你的姓氏：<input name="csurname"><br>
    证件尾4位：<input name="clast4"><br>
    【私密核验信息（只有你知道的细节）】：<textarea name="secret"></textarea><br>
    留言：<textarea name="msg"></textarea><br>
    <button type="submit">提交认领申请</button>
    </form>
    """

@app.post("/submit_claim")
async def submit_claim(item_id:int=Form(),csurname:str=Form(),clast4:str=Form(),secret:str=Form(),msg:str=Form()):
    cur.execute("INSERT INTO claim (item_id,claim_surname,claim_last4,secret_info,contact_msg) VALUES (?,?,?,?,?)",
                (item_id,csurname,clast4,secret,msg))
    conn.commit()
    return "<h3>认领申请提交成功，等待核验</h3><a href='/'>返回首页</a>"

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000)
