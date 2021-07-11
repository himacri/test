from random import sample
from string import ascii_lowercase
import japanize_kivy #日本語使えるようにする
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
import selenium
import threading
import requests
from kivy.clock import Clock
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
from kivy.properties import StringProperty, ObjectProperty

#kivyの初期設定 上から、サイズ変更許可 縦横サイズ
Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
"""Config.set('graphics', 'height', '500')
Config.set('graphics', 'width', '775')"""

class MyClass:
    list1 = []
    col_jp = ["品名","説明"]
    columns = [
        "SKU","タイトル","状態","価格","画像","タグ :ItemID"
        #56項目
        #00-09:
        #10-19:
        #20-29:
        #30-39:
        #40-49:
        #50-55:
    ]
    itemlist_df = pd.DataFrame(data=list1,columns=columns)
    skuList_df = pd.DataFrame(data=list1, columns=["sku_List"])
    ListNo = "-"
#------------------------------------------------------------------
class Search:
    cate = ""
    KWD = ""
    min = ""
    max = ""
    sort = "新しい順"
    jotai = "すべて"
    futan = "送料込み"
    kosu = "5"
    rieki = "20"
    min_rieki = "10"
    rieki_waku = "％"
    tesuryo = ""
    soryo = ""
    url = ""
    rate = ""
#------------------------------------------------------------------

#kvファイル指定
Builder.load_file('search.kv')


class Test(GridLayout):
    img_src = './aaa01.jpg'
    #クリックするとリストを追加
    def click(self):
        thread01 = threading.Thread(target=self.search)
        #thread02 = threading.Thread(target=self.changeimg)
        #thread02.start()
        thread01.start()


    def items(self):
        a = Test()
        try :
            a.ids.L01.text = "./01.jpg"
            a.ids.L02.text = "./02.jpg"
            a.ids.L03.text = "./03.jpg"
            print("ok")
        except :
            print("no")
            import traceback
            traceback.print_exc()
        print("end")

    def search(self):
        name = self.ids.keyWD.text
        url = str("http://")
        value = str(random.randint(300, 20000))
        cnd = ['new','used']
        condi = str(random.choice(cnd))
        pht = ['https://icooon-mono.com/i/icon_10069/icon_100691_48.png','https://icooon-mono.com/i/icon_11164/icon_111641_48.png','https://icooon-mono.com/i/icon_11333/icon_113331_48.png','https://icooon-mono.com/i/icon_00290/icon_002901_48.png']
        photo = str(random.choice(pht))

        #メルカリ検索
        # 検索用URL
        URLs = 'https://www.mercari.com/jp/search/?keyword=' + str(name)
        print(URLs)
        # 指定したURLに遷移
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        resp = requests.get(URLs, headers=headers).text

        # 検索URLのsoupから個別SKUを取得→MyClass.skuList_dfにsku入れる
        soup = BeautifulSoup(resp, 'lxml')
        # そもそも検索結果があるか判定
        sonzai = soup.find("div", class_="search-result-number")
        if sonzai is None :
            return
        else :
            son = sonzai.string[9 :-6]
            #print(son)
            if int(son) < int(Search.kosu) :
                mes = ("条件が合いません。""希望件数:", kosu, "メルカリ件数:", son)
                tkmsg.askokcancel(title="エラー", message=mes)
                return

        i = 0
        ii = 0
        # 個別sku取得する
        div = soup.select("section.items-box")
        for div in div :
            for a in div.select("a") :
                href = a.attrs['href']
                href = href[10 :22]  # 必要な部分だけparseする→m~~~のsku
                if(len(href) ==12):
                    MyClass.skuList_df.loc[i] = (href)  # dfに入れる
                i = i + 1
        #検索で出てきたskuの数
        print(len(MyClass.skuList_df))
        # 1行ごとのデータ揃えていく
        for index_name, item in MyClass.skuList_df.iterrows() :
            messe = '商品サーチ中...' + str(ii) + "/" + str(len(MyClass.skuList_df)) + "個 完了"
            self.ids.result.text = str(messe)
            #sku入れる
            MyClass.itemlist_df.loc[ii, "SKU"] = (item[0])
            URLs = url = ("https://www.mercari.com/jp/items/" + str(item[0]) + "/")
            # URL入れる
            MyClass.itemlist_df.loc[ii, "タグ :ItemID"] = (URLs)
            print(URLs)
            # 画像入れる
            MyClass.itemlist_df.loc[ii, "画像"] = ('https://static.mercdn.net/item/detail/orig/photos/' + str(item[0]) +'_1.jpg')
            # 検索URLのsoupから個別SKUを取得→MyClass.skuList_dfにsku入れる
            resp = requests.get(url, headers=headers).text
            soup = BeautifulSoup(resp, 'lxml')

            # 品名入れる 翻訳済み
            name = soup.find("h1", class_="item-name")
            MyClass.itemlist_df.loc[ii, "タイトル"] = (name.text)
            # 価格
            val = soup.find("span", class_="item-price bold")
            val = val.string.replace('¥', '')
            val = val.replace(',', '')
            MyClass.itemlist_df.loc[ii, "価格"] = int(val)
            # 状態
            row = soup.find_all("td")[-5]
            row = row.string
            if row == "新品、未使用" :
                MyClass.itemlist_df.loc[ii, "状態"] = "新品"
            else :
                MyClass.itemlist_df.loc[ii, "状態"] = "中古"
            ii = ii + 1

        for index_name,item in MyClass.itemlist_df.iterrows():
            lbl = {'no' : str(index_name),'condi' : str(item[2]),'value' : str(item[3]), 'name' : str(item[1])}
            self.rv.data.append(lbl)
        #最後に空行を１つ追加 → 最後の行をクリックするため
        self.rv.data.append({'no' : "",'condi' : "",'value' : "", 'name' : ""})

        MN = round(MyClass.itemlist_df['価格'].mean(),1)
        self.ids.result.text = str("サーチ完了　アイテム数:"+str(len(MyClass.itemlist_df))+" 平均金額:"+str(MN))

    def changeIMG(root):
        a = Test()
        print(MyClass.ListNo)
        root.ids.L01.text = MyClass.ListNo
        root.ids.L02.text = MyClass.ListNo
        root.ids.L03.text = MyClass.ListNo

class VariousButtons(BoxLayout):
    def on_select_button(self ,root):#,button
        a = Test()
        MyClass.ListNo = self.ids.ListButton.text
        return a.changeIMG()
        print(MyClass.ListNo)
        print(a.ids.L01.text,a.ids.L02.text,a.ids.L03.text)
        a.ids.L01.text = MyClass.ListNo
        a.ids.L02.text = MyClass.ListNo
        a.ids.L03.text = MyClass.ListNo
        """thread01 = threading.Thread(target=a.changeIMG)
        thread01.start()"""

class TestApp(App):
    def build(self):
        b = Test()
        return b
if __name__ == '__main__':
    TestApp().run()
