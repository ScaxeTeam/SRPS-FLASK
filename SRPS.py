from flask import Flask, request
from random import choices
import pandas as pd

app = Flask(__name__)
df = pd.read_excel('data.xlsx')

def checkn(name):  # 唯一
    return name not in df.name.values

def checkq(qq):  # 唯一
    return qq.isdigit() and qq not in df.qq.values

def checkp(player):  # 唯一
    return player not in df.player.values

def deliveri():  # 唯一备案号
    d1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    d2 = 'abcdefghijklmnopqrstuvwxyz'
    d3 = '0123456789'
    indexv = ''.join(choices(d1, k=3)) + ''.join(choices(d2, k=3)) + ''.join(choices(d3, k=3))
    if indexv in df.indexv.values:
        return deliveri()
    return indexv

def groupe(indexv):  # 取消吊销
    df.loc[df.indexv == indexv, 'fg'] = 0

def avacheck(name, qq, player, picurl):  # 输入合规性检测
    if 'http' not in picurl:
        return False
    if len(qq) <= 5 or not checkq(qq):
        return False
    if not checkn(name) or not checkp(player) or len(name) > 8:
        return False
    return True

def checkfg(name):  # 是否吊销
    return df.loc[df.name == name, 'fg'].values[0] == 0

def checkdel(name):  # 是否删除
    return df.loc[df.name == name, 'del'].values[0] == 0

def checkch(name):  # 是否审核
    return df.loc[df.name == name, 'ch'].values[0] == 1

def groupy(name):  # 审核通过
    if not checkch(name) and checkdel(name) and not checkfg(name):
        df.loc[df.name == name, ['indexv', 'fg', 'ch']] = [deliveri(), 0, 1]

def groupf(indexv):  # 吊销组织
    df.loc[df.indexv == indexv, 'fg'] = 1

def chdelc(name):  # 已审核且未删除
    return checkch(name) and checkdel(name)

def showni():  # 输出所有已审核且未删除的组织名称和对应备案号
    return df.loc[chdelc(df.name), ['name', 'indexv']].apply(lambda x: f"{x['name']}={x['indexv']}", axis=1).tolist()

def setl(slevel, indexv):  # 设置对应备案号组织等级
    df.loc[(chdelc(df.name)) & (df.indexv == indexv), 'level'] = slevel

def delg(name):  # 删除对应名称组织
    df.loc[(chdelc(df.name)) & (df.name == name), 'del'] = 1

def searchg(sname):  # 模糊搜索对应组织
    return df.loc[(chdelc(df.name)) & (df.name.str.contains(sname)), ['name', 'indexv', 'player', 'level', 'fg']].apply(lambda x: f"{x['name']}={x['indexv']}={x['player']}={x['level']}+{x['fg']}", axis=1).tolist()

def backy():  # 输出已审核未删除组织，admin only
    return df.loc[chdelc(df.name), ['name', 'indexv', 'player', 'qq', 'fg', 'level', 'picurl']].apply(lambda x: f"{x['name']}={x['indexv']}={x['player']}={x['qq']}={x['fg']}={x['level']}+{x['picurl']}", axis=1).tolist()

def backn():  # 输出未审核组织，admin only
    return df.loc[~checkch(df.name) & checkdel(df.name), ['name', 'indexv', 'player', 'qq', 'fg', 'level', 'picurl']].apply(lambda x: f"{x['name']}={x['indexv']}={x['player']}={x['qq']}={x['fg']}={x['level']}+{x['picurl']}", axis=1).tolist()

password = '33666789qw'

@app.route('/', methods=['GET'])  # 前端测活
def alivecheck():
    return '200/OK'

@app.route('/sendg', methods=['GET'])  # 从前端接收数据
def receivedata():
    name = request.args.get('name', '')
    qqn = request.args.get('qq', '')
    player = request.args.get('player', '')
    picu = request.args.get('pic', '')
    fgn = '1'
    deln = '0'
    chn = '0'
    leveln = '2'
    if avacheck(name, qqn, player, picu):
        global df
        df = pd.concat([df, pd.DataFrame([{'name': name, 'qq': qqn, 'player': player, 'picurl': picu, 'fg': fgn, 'del': deln, 'ch': chn, 'level': leveln}])], ignore_index=True)
        return 'Received'
    else:
        return 'ERR'

@app.route('/check', methods=['GET'])
def checkdata():  # 操作xlsx admin only
    passinput = request.args.get('pass', '')
    getlist = request.args.get('gety', '')
    indv = request.args.get('index', '')
    cch = request.args.get('ch', '')
    ddel = request.args.get('del', '')
    name = request.args.get('name', '')
    fg1 = request.args.get('fg', '')
    if passinput == password:
        if getlist == 'Y':
            return backy()
        if getlist == 'N':
            return backn()
        if cch == '0' and name:
            groupy(name)
            return 'done'
        if ddel == '1' and name:
            delg(name)
            return 'done'
        if fg1 == 'Y' and name:
            groupf(indv)
            return 'done'
        if fg1 == 'N' and indv:
            groupe(indv)
            return 'done'
        if getlist == 'ALL':
            return showni()
    return '429'

@app.route('/gsb', methods=['GET'])  # 搜索
def search():
    name = request.args.get('name', '')
    return searchg(name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=54431, threaded=True, debug=True)  # 启动
