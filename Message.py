from linebot.models import *
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from config import Config
from urllib.parse import quote
import json
import time
import re
import os

#selenium背景運行
# options=Options()   #本機用
options=webdriver.ChromeOptions()  #上傳Heroku用
options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")  #上傳Heroku用
# 關閉瀏覽器跳出訊息
prefs = {
    'profile.default_content_setting_values' :
    {
        'notifications' : 2
        }
    }
options.add_experimental_option('prefs',prefs)
options.add_argument("--headless")            #不開啟實體瀏覽器背景執行
options.add_argument("--incognito")           #開啟無痕模式
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
#上傳Heroku用
driver=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)

#滾動頁面
def scroll(scrolltimes):
    for i in range(scrolltimes):
        # 每一次頁面滾動都是滑到網站最下方
        js = 'window.scrollTo(0, document.body.scrollHeight);'
        driver.execute_script(js)
        time.sleep(0.1)

#點開所有查看更多
def clickReadMore():
    btn_class = 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p'
    btn_class = btn_class.replace(" ", ".")
    while True:
        try:
            btn_more = driver.find_element_by_css_selector('div.' + btn_class)
            ActionChains(driver).move_to_element(btn_more).perform()
            btn_more.click()
            time.sleep(0.1)
        except selenium.common.exceptions.NoSuchElementException:
            break

#爬取fb po文-漁獲日誌
def getgroupshare():
    url = r'https://www.facebook.com/hashtag/%E6%BC%81%E7%8D%B2%E6%97%A5%E8%AA%8C?__gid__=531488838107644'
    driver.get(url)
    # for i in range(2):
    #     scroll(1)
    #     clickReadMore()
    #     time.sleep(0.3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elem = soup.select('image[preserveAspectRatio="xMidYMid slice"]')

    fishx = []
    for i in elem:
        fishx.append(i)

    datas = []
    for i in fishx:
        j = i.find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent()
        datas.append(j)

    postlist = []
    imglist = []
    urllist = []
    lovefishurl = 'https://www.facebook.com/Fishx12345/'
    for data in datas:
        i=data.find('i',{'data-visualcompletion':'css-img'})
        if i['aria-label']=='發佈到':
            posts = data.find('div').find('div').find_next_sibling('div').find_next_sibling('div').find('div').find('div').find('div').find('div').find('span')
        else:
            posts = data
        posts = posts.find_all('div', {'dir': 'auto'})
        text = ''
        img_link = ''
        url = ''
        for post in posts:
            post = post.text
            text += post + '\n'
        url += r'https://www.facebook.com/groups/531488838107644'

        postlist.append(text)
        urllist.append(url)
        img = data.find_all('img')
        img.pop()
        for j in img:
            try:
                if re.match(r'^(data:.*)$', j['src']):
                    img_link += '{},,,'.format(lovefishurl)
                elif j['height'] == '16':
                    continue
                else:
                    img_link += '{},,,'.format(j['src'])
            except KeyError:
                img_link += '{},,,'.format(j['src'])

        imglist.append(img_link)
    return postlist, imglist, urllist

# 用hashtag爬取文章內容
def getFbPost(hashtag):
    hashtag = hashtag
    url = ''
    if hashtag == '釣魚知識':
        url = r'https://www.facebook.com/hashtag/%E9%87%A3%E9%AD%9A%E7%9F%A5%E8%AD%98'
    elif hashtag == '政府公告':
        url = r'https://www.facebook.com/hashtag/%E6%94%BF%E5%BA%9C%E5%85%AC%E5%91%8A'
    elif hashtag == '釣魚點':
        url=r'https://www.facebook.com/hashtag/%E9%87%A3%E9%AD%9A%E9%BB%9E'
    elif hashtag == '釣魚資訊':
        url=r'https://www.facebook.com/hashtag/%E9%87%A3%E9%AD%9A%E8%B3%87%E8%A8%8A'
    elif hashtag == '漁獲日誌':
        url = r'https://www.facebook.com/hashtag/%E6%BC%81%E7%8D%B2%E6%97%A5%E8%AA%8C'

    driver.get(url)
    
    # for i in range(2):
    #     scroll(1)
    #     clickReadMore()
    #     time.sleep(0.3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elem=soup.select('image[preserveAspectRatio="xMidYMid slice"]')

    fishx=[]
    for i in elem:
        if re.match(r'^.*(240495479_100643409025461_3390718755814161181_n.jpg).*$', i['xlink:href']):
            fishx.append(i)

    datas=[]
    for i in fishx:
        j=i.find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent().find_parent()
        datas.append(j)

    postlist=[]
    imglist=[]
    urllist=[]
    lovefishurl='https://www.facebook.com/Fishx12345/'
    for data in datas:
        posts = data.find('div').find_next_sibling('div').find_next_sibling('div').find('div').find('div').find('div').find('div').find('span')
        posts=posts.find_all('div',{'dir':'auto'})
        text=''
        img_link=''
        url=''
        for post in posts:
            if re.match(r'^.*(https:).*$', post.text):
                ragex = post.text
                ragex = ragex.split('https://')
                urr = ''
                for a in ragex:
                    if re.match(r'^www.+', a):
                        urr += 'https://' + a
                    else:
                        continue
                url += urr
            else:
                post = post.text
                text += post + '\n'

        postlist.append(text)
        urllist.append(url)
        img=data.find_all('img')
        img.pop()
        for j in img:
            try:
                if re.match(r'^(data:.*)$', j['src']):
                    img_link += '{},,,'.format(lovefishurl)
                elif j['height']=='16':
                    continue
                else:
                    img_link += '{},,,'.format(j['src'])
            except KeyError:
                img_link += '{},,,'.format(j['src'])

        imglist.append(img_link)
    return postlist,imglist,urllist

# 釣手知識+
def learn():
    FlexMessage = json.load(open('./json/card.json','r',encoding='utf-8'))
    message = FlexSendMessage('釣魚知識報你知~',FlexMessage)
    return message

# 魚類百科
def fish_encyclopedia():
    FlexMessage = json.load(open('./json/fish.json','r',encoding='utf-8'))
    FlexMessage['contents'][0]['footer']['contents'][0]['action']['uri']='line://oaMessage/{base_id}/?{message}'.format(base_id=Config.BASE_ID,message=quote('@'))
    message = FlexSendMessage('你知道你釣到什麼魚嗎??',FlexMessage)
    return message

# 知識+
def quick_reply_FB_hashtag():
    message = TextSendMessage(
        text="請選擇要查詢的文章標籤",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="釣魚知識", text="釣魚知識")
                ),
                QuickReplyButton(
                    action=MessageAction(label="政府公告", text="政府公告")
                ),
                QuickReplyButton(
                    action=MessageAction(label="釣魚點", text="釣魚點")
                ),
                # QuickReplyButton(
                #     action=MessageAction(label="釣魚資訊", text="釣魚資訊")
                # ),
                QuickReplyButton(
                    action=MessageAction(label="漁獲日誌", text="漁獲日誌")
                ),
                QuickReplyButton(
                    action=MessageAction(label="愛釣客", text="愛釣客")
                )
            ]
        )
    )
    return message

# 台灣常見魚類 & 繼續探索
def quick_reply_taiwanese_fish():
    message=TextSendMessage(
    text="請選擇魚的特性",
    quick_reply=QuickReply(
        items=[
            QuickReplyButton(
                image_url='https://i.imgur.com/y1FfTzg.png',
                action=MessageAction(label="有毒魚類",text="有毒魚類")
                ),
            QuickReplyButton(
                image_url='https://i.imgur.com/dwpRDhS.png',
                action=MessageAction(label="經濟性魚類",text="經濟性魚類")
                ),
            QuickReplyButton(
                image_url='https://i.imgur.com/EgIoOo8.png',
                action=MessageAction(label="可食用魚類",text="可食用魚類")
                ),
            QuickReplyButton(
                image_url='https://i.imgur.com/dSZvf7J.png',
                action=MessageAction(label="觀賞魚類",text="觀賞魚類")
                ),
            QuickReplyButton(
                image_url='https://i.imgur.com/Ybacbsn.png',
                action=MessageAction(label="瀕危魚類",text="瀕危魚類")
                )
            ]
        )
    )
    return message

# 有毒魚類、經濟性魚類、可食用魚類、觀賞魚類、瀕危魚類
def fish_type(msg):
    reply=[]
    if msg == '有毒魚類':
        FlexMessage = json.load(open('./json/poison_fish.json','r',encoding='utf-8'))
        reply.append(FlexSendMessage('有毒魚類',FlexMessage))
        
    elif msg == '經濟性魚類':
        FlexMessage = json.load(open('./json/economy_fish.json','r',encoding='utf-8'))
        reply.append(FlexSendMessage('經濟性魚類',FlexMessage))

    elif msg == '可食用魚類':
        FlexMessage = json.load(open('./json/eat_fish.json','r',encoding='utf-8'))
        reply.append(FlexSendMessage('可食用魚類',FlexMessage))

    elif msg == '觀賞魚類':
        FlexMessage = json.load(open('./json/watch_fish.json','r',encoding='utf-8'))
        reply.append(FlexSendMessage('觀賞魚類',FlexMessage))

    elif msg == '瀕危魚類':
        FlexMessage = json.load(open('./json/endangered_fish.json','r',encoding='utf-8'))
        reply.append(FlexSendMessage('瀕危魚類',FlexMessage))

    reply.append(TextSendMessage(
        text="請問還要搜尋其他魚種嗎?",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="繼續探索",text="繼續探索")
                    ),
                QuickReplyButton(
                    action=MessageAction(label="先不要",text="先不要")
                    )
                ]
            )
        ))
    message = reply
    return message

# @
def fish_search_action(msg):
    message = TemplateSendMessage(
    alt_text=msg+' 的搜尋結果',
    template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/bSJmLCG.jpg',
                title=msg+' 的搜尋結果',
                text='以下為您的搜尋結果',
                actions=[
                    URITemplateAction(
                        label='點擊查看結果',
                        uri='https://fishdb.sinica.edu.tw/mobi/fishlist.php?key='+msg+'&B1=%E6%9F%A5%E8%A9%A2'
                            )
                        ]
                    )
                ]
            )
        )
    return message

# 政府公告、釣魚知識、釣魚點、釣魚資訊、漁獲日誌
def FbHashTag_flex_message(hashtag):
    hashtag=hashtag
    flex_carousel = r'{"type": "carousel","contents": [%s]}'
    bubble = r'{"type":"bubble","paddingAll": "none","size":"giga","body":{"type":"box","layout":"vertical","paddingAll": "15px","backgroundColor":"#FFFFFF","contents":[%s%s%s]},"footer":{"type":"box","layout": "horizontal","margin":"0px","backgroundColor":"#FFFFFF","contents":[{"type": "button","style": "primary","color":"#C36839","action": {"type": "uri","label": "前往連結","uri": "%s"}}]}},'
    flex_text = '{"type": "text","text": "%s","wrap": true,"size":"md","color":"#4D4D4D"},'
    flex_text_h1 = '{"type": "text","text": "%s","wrap": true,"size":"xxl","color":"#4493A3"},'
    flex_img_box = '{"type": "box","layout": "horizontal", "width":"290px","margin":"0px","paddingAll": "none","contents": [%s]}'
    flex_img = '''{
            "type": "image",
            "url": "%s",
            "size": "100%%"
          },'''

    flex_message = ''

    if hashtag=='漁獲日誌':
        fbcontent, fbimg, fburl = getgroupshare()
    else:
        fbcontent, fbimg, fburl = getFbPost(hashtag)
    testlist = fbcontent
    testimglist = fbimg
    testurllist = fburl
    for i in range(len(testlist)):
        # \n會造成json讀取出錯，用\\n替換
        text = testlist[i].split('\n')
        text_n = ''
        text_h1=''
        for te in range(len(text)):
            if te == 0:
                text_h1+=text[te]
            else:
                text_n += text[te] + '\\n'
        # 把內文加入flextext的內容裡
        textt_h1=flex_text_h1 %text_h1
        textt = flex_text % text_n

        if testurllist[i] == '':
            urll = r'https://www.facebook.com/Fishx12345/'
        else:
            urll = testurllist[i]
        # 圖片用,,,做分割
        testimglist1 = testimglist[i].split(r",,,")
        flex_img_try = ''
        # 繞行圖片
        for j in testimglist1:
            if j =='':
                continue
            else:
                # 把圖片url加入fleximg
                flex_img1 = flex_img % j
                # 建立多個fleximg
                flex_img_try += flex_img1
        # 刪除最後一個逗點
        flex_img_try = flex_img_try[:-1]
        # 把fleximg加入box內用,隔開
        imgg = flex_img_box % flex_img_try + ','
        # 消除最後一個逗點
        imgg = imgg[:-1]
        # 把文字跟圖片加入bubble內
        flex_message += bubble % (textt_h1,textt, imgg, urll)
    # 消除最後一個逗點
    flex_message = flex_message[:-1]
    # 把bubble放入carousel內
    flex_message = flex_carousel % flex_message
    #print(flex_message)
    FlexMessage=json.loads(flex_message)
    #print(FlexMessage)
    content=FlexSendMessage('知識+',FlexMessage)
    return content