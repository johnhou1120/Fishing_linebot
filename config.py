import os

class Config:
    Air_key='CWB-6D26AA4C-02BF-49C2-974D-EF4A0B2668ED'
    STORE_IMAGE_URL = 'https://i.imgur.com/3BPzJkU.png'
    GOOGLE_API = 'AIzaSyApVac4VUq47R3baxPMTa8DiExURBRKEoU'

    #=====Line機器人=====#
    CHANNEL_ACCESS_TOKEN = 'W+tf75Kwb41cwj/Ph7mUPougdlD58CuouY4vKaPIT89h51zNeIYA/DqRBx83GtC3VXSIjwZPUmCy8kTIfHijJjd2M/T1UGSU/1YkNeHMOSDSlzJ3EoO0VpZQ85PXx6da+1If4hhDg5TVG5bp/cLhqAdB04t89/1O/w1cDnyilFU='
    CHANNEL_SECRET = '62a915337e738dd73fd3f706b3bec8bf'
    CHANNEL_ID = '1656429403'
    BASE_ID = '@704zipha'
    
    #=====Line_PAY=====#
    LINE_PAY_ID = '1656224031'
    LINE_PAY_SECRET ='f17d9671a7406c538a6380915e705e19'
    STORE_IMAGE_URL = 'https://i.imgur.com/Xwmc0B9.jpg'
    
    #=====資料庫=====#
    DATABASE_NAME = 'fishing'

    #=====fishingmap & report=====#
    REPORT_LOCATION_LIST = ['基隆', '台北', '新北', '桃園', '新竹', '苗栗', '台中', '彰化', '南投', '雲林', '嘉義', '台南', '高雄', '屏東', '宜蘭', '花蓮', '台東', '金門', '馬祖', '澎湖']
    REPORT_TYPE_LIST = ['堤岸釣' , '港區垂釣' , '出海船釣' , '磯釣', '岩釣', '筏釣', '沙/礫灘釣',  '野溪/河釣', '野塘釣', '水庫釣']
    REPORT_FISH_LIST = ['鱸魚', '真鯛魚', '牙鮃(比目魚)', '黑鯧', '鮁魚', '黑鯛', '魷魚', '鮐魚', '軟絲', '剝皮魚' , '象魚', '瓜瓜']