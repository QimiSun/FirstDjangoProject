import requests
import json
import re
import time

detail_url = "http://www.yeeyi.com/bbs/forum.php?mod=viewthread&tid=4291270"
tid = re.findall(r'tid=(\d+)', detail_url)[0]
url = "https://app.yeeyi.com.cn/index.php?app=thread&act=getThreadContent"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "157",
    "Host": "app.yeeyi.com.cn",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.7.0",
}
data = {
    "clientid": "c1ba34268f4d393a2e07fff7bb325c01",
    "app_ver": "2_0_3_android",
    "tid": str(tid)
}
response = json.loads(requests.post(url=url, headers=headers, data=data).content.decode())["threadInfo"]
img_src_list = response["section_1"]
if len(img_src_list) == 0:
    print("container")
title = response["section_2"]["subject"]
price_temp = response["section_2"]["house_rents"]
price = re.findall(r'\$(\d+)/', price_temp)[0]
phone = response["section_5"][1][1]
weixin = response["section_5"][2][1]
if len(weixin) == 0:
    weixin = ""
finally_desc = response["section_4"]["message"].replace("<p>", "").replace("</p>", "").replace("\r\n", "")
if len(finally_desc) == 0:
    print("container")
detail_addr = response["section_2"]["address"]
bedroomNum = response["section_2"]["house_room"]
bathroomNum = response["section_2"]["house_toilet"]
now_startDate = time.strftime("%Y-%m-%d", time.localtime())