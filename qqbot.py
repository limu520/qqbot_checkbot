from flask import *
import requests
import sqlite3
import random
import json
##配置文件
api_url1 = 'http://127.0.0.1:5700/send_msg'
api_url2 = "http://127.0.0.1:5700/delete_msg"

qq_group=["723174283"]

##初始化
for a in qq_group:
    db = sqlite3.connect("qq.db")
    cur=db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS qq"+a+"(qq_id TEXT,confirm TEXT)")
    db.commit()
    cur.close()
    db.close()

##数据库增加
def inc(db_name = "", qq_id = "",con_id = ""):
    db = sqlite3.connect("qq.db")
    cur=db.cursor()
    cur.execute("INSERT INTO qq"+db_name+" values(?,?)",(str(qq_id),str(con_id)))
    db.commit()
    cur.close()
    db.close()
    return ''

##数据库删除
def delqq(db_name = "", qq_id = ""):
    db = sqlite3.connect("qq.db")
    cur=db.cursor()
    n=cur.execute("DELETE FROM qq"+db_name+" WHERE qq_id="+qq_id+"")
    db.commit()
    cur.close()
    db.close()
    return ''

##数据库查询
def check(db_name = "", qq_id = ""):
    db = sqlite3.connect("qq.db")
    cur=db.cursor()
    cur.execute("SELECT * FROM qq"+db_name+" where qq_id="+qq_id+"")
    result = cur.fetchone()
    cur.close()
    db.close()
    return result

##撤回
def del_msg(msg_id = 0):
    msg = {
            "message_id":msg_id
            }
    msg_re = requests.post(api_url2,data=msg)
    print(msg_re)
    return ''

##群消息发送
def group_msg(group_id = 0 , message = ""):
    msg = {
            'group_id':group_id,
            'message':message,
            'auto_escape':False
            }
    msg_re = requests.post(api_url1,data=msg)
    print(msg_re)
    return ''

##主程序
bot_server = Flask(__name__)
@bot_server.route('/',methods=['POST'])

def server():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    print(data)
    ##进群消息
    if data["post_type"] == "notice" and data["notice_type"] == "group_increase":
        con_id = random.sample('zyxwvutsrqponmlkjihgfedcba',8)
        inc(str(data["group_id"]),str(data["user_id"]),str(con_id))
        group_msg(data["group_id"],"请在群内发送以下字符串\n"+str(con_id)+"\n然后您将可以在本群发言")
    if data["post_type"] == "message": 
        if str(data["group_id"]) in qq_group:     
            result = check(str(data["group_id"]),str(data["user_id"]))
            if result: 
                if result[1] in data["message"]:
                    group_msg(data["group_id"],"恭喜您通过验证！！！")
                    delqq(str(data["group_id"]), str(data["user_id"]))
                else:
                    del_msg(data["message_id"])
                    group_msg(data["group_id"],"请完成验证")

    return ''
if __name__ == '__main__':
    bot_server.run(host="127.0.0.1",port=5701,debug=True)
