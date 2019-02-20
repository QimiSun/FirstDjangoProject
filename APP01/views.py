from django.shortcuts import render, HttpResponse


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "awehome" and password == "awehome666":
            return_obj = render(request, "choice.html")
            return_obj.set_cookie("cookies", "aaaaaa")
            return return_obj
        else:
            return render(request, "login.html", {"error": "输入的用户名或密码错误,请重新输入"})
    return render(request, "login.html")


def choice(request):
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "choice.html")
        else:
            return render(request, "login.html")


def dida(request):
    # 判断是否登陆，没有登录就返回登录界面
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "dida.html")
        else:
            return render(request, "login.html")

    # POST请求的话就拿到前端发过来的数据
    else:
        city = request.POST.get("city")

        if city == "悉尼":
            city = 1
            school0 = "12"
            school1 = "17"
            school2 = "18"
            jingweidu = "151.20929550000005,-33.8688197"

        if city == "墨尔本":
            city = 2
            school0 = "10"
            school1 = "11"
            school2 = "19"
            jingweidu = "144.96305759999996,-37.8136276"
        if city == "布里斯班":
            city = 4
            school0 = "15"
            school1 = "20"
            school2 = "38"
            jingweidu = "153.02512350000006,-27.4697707"
        if city == "阿德莱德":
            city = 5
            school0 = "13"
            school1 = "31"
            school2 = "33"
            jingweidu = "138.60074559999998,-34.9284989"
        if city == "堪培拉":
            city = 3
            school0 = "14"
            school1 = "35"
            school2 = "87"
            jingweidu = "149.13000920000002,-35.2809368"

        quhao = request.POST.get("quhao")
        username = request.POST.get("username")
        password = request.POST.get("password")
        detail_url = request.POST.get("detail_url")
        from APP01 import models
        filter_object = models.awehomeinfos.objects.filter(refer=detail_url).first()
        if filter_object:
            return HttpResponse("非常抱歉,这条房源已在Awehome平台存在,请另外寻找上传")

        from APP01.config.rk import RClient
        import requests
        import json
        from lxml import etree
        import time
        import re
        from requests_toolbelt import MultipartEncoder
        import upyun

        requests = requests.session()

        # 抓取第三方房源标题、价格、等信息
        try:
            detail_response = requests.get(detail_url).content.decode()
            dida_detail_all_srt_dic = json.loads(re.findall(r'articleTool.baseInfo = (.*?);', detail_response)[0])
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,上传失败,请再次确认输入的url来源是否为滴答网")
        # 拿到所有图片地址列表
        HTML = etree.HTML(detail_response)
        tid = dida_detail_all_srt_dic["tid"]
        title = dida_detail_all_srt_dic["title"].replace(",", "").replace("，", "").replace("！", "").replace("!",
                                                                                                            "").replace(
            "[", "").replace("]", "").replace("【", "").replace("】", "").replace(".", "").replace("。", "").replace("@",
                                                                                                                  "").replace(
            "#", "").replace("（", "").replace("*", "").replace("）", "").replace("-", "").replace("_", "").replace("/",
                                                                                                                  "").replace(
            "%", "").replace("$", "").replace("^", "").replace("&", "").replace("*", "").replace("(", "").replace(")",
                                                                                                                  "").replace(
            "█", "").replace("☆", "").replace("+", "").replace("、", "").replace("★", "").replace("|", "").replace("▂",
                                                                                                                  "").replace(
            "▃", "").replace("▆", "").replace("▇", "").replace("∎", "")[0:30]
        img_src_list = HTML.xpath('//article[@style="background-color:#fff;"]//img/@data-src')
        if len(img_src_list) == 0 or img_src_list[0][0:4] == "http":
            print("名称为{}的房源没有图片,此条房源已跳过".format(title))
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有图片,已跳过".format(title))
        if len(img_src_list) < 3:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息图片少于三张,已跳过".format(title))
        # 通过etree获取房源详细描述
        detail_desc_list = HTML.xpath('//article[@style="background-color:#fff;"]//text()')
        if len(detail_desc_list) == 0:
            print("名称为{}的房源没有详情描述,此条房源已跳过".format(title))
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有详情描述,已跳过".format(title))

        # 判断详情描述多少字,超过五百就取前五百个字符
        finally_desc = ""
        for detail_desc in detail_desc_list:
            finally_desc += detail_desc

        # 判断其他描述长度是否大于五百字符，大于五百就取前五百个字节
        if len(finally_desc) > 500:
            finally_desc = finally_desc[0:500]

        # 判断是几个卧室、几个卫浴
        roomtype = dida_detail_all_srt_dic["roomtype"]
        if roomtype == "1" or roomtype == "2":
            bedroomNum = "1"
            bathroomNum = "1"
        elif roomtype == "3" or roomtype == "4":
            bedroomNum = "2"
            bathroomNum = "2"
        elif roomtype == "5" or roomtype == "6":
            bedroomNum = "3"
            bathroomNum = "3"
        else:
            bedroomNum = "4"
            bathroomNum = "4"

        # 实时时间
        now_startDate = time.strftime("%Y-%m-%d", time.localtime())

        # 从JS中获取价格、详细地址
        price = dida_detail_all_srt_dic["prices"]
        phone = dida_detail_all_srt_dic["linknum"]
        weixin = ""
        detail_addr = dida_detail_all_srt_dic["address"]
        if detail_addr == "":
            detail_addr = "Sydney"

        try:
            # 实例化又拍云对象
            rc = RClient('awehome', 'xQiFb76y6hJCTe6', '119809', '0202040b5e4647cb8a0cc60c822e986d')
            # 实例化若快打码对象
            up = upyun.UpYun(service="house-image", username="awehomezhangxiaowei", password="awehomezhangxiaowei")
        except Exception as f:
            print("登陆错误:", f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))

        # 发送验证码图片,拿到验证码字符串
        awehome_login_code = requests.get("http://awehome.com.cn/site/captcha?refresh=true").content.decode()
        img_src = "http://awehome.com.cn" + json.loads(awehome_login_code)["url"]
        img_response = requests.get(img_src).content
        img_fonz = json.loads(rc.rk_create(img_response, 3040))["Result"]

        # 登录
        post_login_url = "http://awehome.com.cn/landlord/login"
        post_login_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Length": "169",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_identity=c308968c88fdbbce9551e193975a3546914ee428af7607951aaac678e8618ffaa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B6112%2C%22PK7GArlTBAPCkespZ0pku4qAns6S6rXo%22%2C604800%5D%22%3B%7D; expires=Tue, 15-Jan-2019 07:36:56 GMT; Max-Age=604800; path=/; HttpOnly",
            "Host": "awehome.com.cn",
            "Origin": "http://awehome.com.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://awehome.com.cn/tenant/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        post_login_data = {
            "referer": "http://awehome.com.cn/",
            "Login[dialcode]": str(quhao),
            "Login[phone]": str(username),
            "Login[captcha]": str(img_fonz),
            "Login[password]": str(password),
            "Login[rememberMe]": "0",
        }
        post_login_response = requests.post(url=post_login_url, headers=post_login_headers,
                                            data=post_login_data, ).content.decode()
        print(post_login_response)
        try:
            result_error = json.loads(post_login_response)["errors"]
            if "password" in result_error.keys():
                return HttpResponse("非常抱歉,您输入的用户名或密码错误,请重新输入")
            if "captcha" in result_error.keys():
                return HttpResponse("非常抱歉,登录Awehome过程中验证码错误,此条房源url为     {}".format(detail_url))
        except Exception:
            pass

        # 从前端拿到房源链接进行发布
        try:
            # 访问发布界面
            requests.get("http://awehome.com.cn/housing/create").content.decode()

            # 自动发布帖子
            post_publish_url = "http://awehome.com.cn/housing/create"
            post_publish_headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Date": "Wed, 09 Jan 2019 08:02:58 GMT",
                "Expires": "Thu, 19 Nov 1981 08:52:00 GMT",
                "Pragma": "no-cache",
                "Server": "nginx/1.10.3 (Ubuntu)",
                "Set-Cookie": "_identity=09ce810bc65bd52e6903f36268fc5b50ff1c77e3acea40021410655b598d853ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B3049%2C%22dU1uwbSvekMvFSANgsROwP8y55vq0D1q%22%2C604800%5D%22%3B%7D; expires=Wed, 16-Jan-2019 08:02:58 GMT; Max-Age=604800; path=/; HttpOnly",
                # "Transfer-Encoding": "chunked",
                "X-Powered-By": "PHP/7.1.13",
            }

            post_publish_data = {
                # 第一页请求
                "Housing[form]": "uploadForm",
                "Housing[view]": "form",
                "Housing[rentalType]": "2",  # 出租类型 独立房间
                "Housing[houseType]": "1",  # 户型 公寓
                "Housing[bedroomNum]": str(bedroomNum),  # 卧室数量 2
                "Housing[bathroomNum]": str(bathroomNum),  # 卫浴数量 2
                "Housing[occupancyNum]": "2",  # 总住人数 2
                "Housing[isFurniture]": "1",  # 是否包含家具 包含
                # 第二页请求
                "Housing[countryId]": "4",  # 国家 英国
                "Housing[cityId]": str(city),  # 城市 伦敦
                "Housing[mapCoordinate]": str(jingweidu),  # 地址 坐标
                "Housing[mapDescribe]": str(detail_addr),  # "A4, London WC2N 5DU英国", #详细地址
                "Housing[housingSchool][0][id]": str(school0),  # 附近学校0 悉尼大学
                "Housing[housingSchool][0][text]": "",  # 距离描述0
                "Housing[housingSchool][1][id]": str(school1),  # 附近学校1 悉尼科技大学
                "Housing[housingSchool][1][text]": "",  # 距离描述1
                "Housing[housingSchool][2][id]": str(school2),  # 附近学校2 新南威尔士大学
                "Housing[housingSchool][2][text]": "",  # 距离描述2
                # 第三页请求
                "Housing[housingFacilities][22]": "22",  # 设施 洗衣机、电视、冰箱、WIFI、空调、厨房、阳台、电梯、包bill
                "Housing[housingFacilities][23]": "23",  # 设施
                "Housing[housingFacilities][24]": "24",  # 设施
                "Housing[housingFacilities][25]": "25",  # 设施
                "Housing[housingFacilities][26]": "26",  # 设施
                "Housing[housingFacilities][27]": "27",  # 设施
                "Housing[housingFacilities][28]": "28",  # 设施
                "Housing[housingFacilities][29]": "29",  # 设施
                "Housing[housingFacilities][30]": "30",  # 设施
                "Housing[housingPeriphery][50][id]": "50",  # 周边 超市、游泳池、健身房、火车站、公交站
                "Housing[housingPeriphery][50][text]": "",  # 描述说明
                "Housing[housingPeriphery][6][id]": "6",  # 周边
                "Housing[housingPeriphery][6][text]": "",  # 描述说明
                "Housing[housingPeriphery][7][id]": "7",  # 周边
                "Housing[housingPeriphery][7][text]": "",  # 描述说明
                "Housing[housingPeriphery][8][id]": "8",  # 周边
                "Housing[housingPeriphery][8][text]": "",  # 描述说明
                "Housing[housingPeriphery][9][id]": "9",  # 周边
                "Housing[housingContact][293][id]": "293",  # 微信参数相关
                "Housing[housingContact][293][text]": str(weixin),  # 微信号
                "Housing[housingPeriphery][9][text]": "",  # 描述说明
                "Housing[housingContact][294][id]": "294",  # 手机号参数相关
                "Housing[housingContact][294][text]": str(phone),  # 手机号
                "Housing[introText]": str(finally_desc),  # 其他介绍
                # 第四页请求
                "Housing[name][2]": str(title),  # "最后一间房子出租",#标题
                "Housing[housingHouse][2][0][singleType]": "1",  # 独立房间类型 主卧
                "Housing[housingHouse][2][0][bedType]": "2",  # 床型 双人床
                "Housing[housingHouse][2][0][bedNum]": "1",  # 床位数
                "Housing[housingHouse][2][0][isBathroom]": "1",  # 独立卫浴 是
                "Housing[housingHouse][2][0][price]": str(price),  # "500",#价格 500英镑GBP/每周
                "Housing[housingHouse][2][0][startDate]": str(now_startDate),  # "2019-01-10",#起租日期
                "Housing[housingHouse][2][0][leaseType]": "1",  # 租期 租期不限
                # 第五页请求-上传图片
                "Housing[housingHouse][2][0][upload][0][imageId]": "0",
                # "Housing[housingHouse][2][0][upload][0][imageUrl]": "",
                "Housing[housingHouse][2][0][upload][0][imageFile]": "",
                # "filename": "blob",
                # "Content-Type": "image/jpegahttp://bbs.tigtag.com/a1546698533817019500.html",
            }
            m = MultipartEncoder(post_publish_data)
            post_publish_headers['Content-Type'] = m.content_type
            post_publish_response = json.loads(
                requests.post(url=post_publish_url, headers=post_publish_headers, data=m).content.decode())
            print(post_publish_response)
            housing_key = post_publish_response["id"]

            # 已发布成功的awehome房源详情链接
            awehomesrc = "http://awehome.com.cn/housing/view?id={}".format(housing_key)

            # 连接数据库，并创建游标
            from APP01.config.connect_mysql import conn_MySQL
            db = conn_MySQL(
                host="47.91.43.200",
                port=3315,
                user="awehome",
                password="AFrokRANYodgYqfdnCpHc4RA",
                database="awehome",
                charset="utf8"
            )

            cursor = db.cursor()

            # aweh_housing_house_image表中找到housing_house_id，然后 + 1
            # sql = 'select * from aweh_housing_house_image order by housing_house_image_id DESC limit 1;'
            # cursor.execute(sql)
            # result = cursor.fetchall()
            # housing_house_id = result[0][1] + 1

            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            sql = 'select * from aweh_housing where housing_key={}'.format(housing_key)
            cursor.execute(sql)
            result = cursor.fetchall()
            housing_id = result[0][0]

            # 往Awehome封面图里面上传从滴答网获取到的第一张图片
            # img_src = img_src_list[0]
            # img_src = "http://www.ybirds.com{}".format(img_src)
            # img_name = re.findall(r'Class/(.*?).j|Class/(.*?).J|Class/(.*?).p|Class/(.*?).P', img_src)[0][0]
            #
            # # 向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
            # tasks = [{"url": img_src, "random": False, "overwrite": True,"save_as": "/yingniao/{}".format(img_name)}]
            # up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
            # awehome_sql_img = "http://img.awehome.com.cn/yingniao/{}".format(img_name)
            #
            # # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
            # sql = 'insert into aweh_housing_house_image(housing_house_id,housing_id,image_url,status) values ({},{},"{}",{})'.format(housing_house_id, housing_id, awehome_sql_img, 10)
            # cursor.execute(sql)
            # db.commit()

            # 往Awehome其他图片里面上传所有图片
            for img_src in img_src_list:
                img_src = "http://cdn2.aus5.com/a/{}/{}!pc-a".format(tid, img_src)
                img_name = re.findall(r'\d/(.*?).gif', img_src)[0]

                # 向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
                tasks = [{"url": img_src, "random": False, "overwrite": True, "save_as": "/dida/{}".format(img_name)}]
                up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
                awehome_sql_img = "http://img.awehome.com.cn/dida/{}".format(img_name)

                # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
                sql = 'insert into aweh_housing_image(housing_id,image_url,explain_text,status) values ({},"{}","",10)'.format(
                    housing_id, awehome_sql_img)
                cursor.execute(sql)
                db.commit()

        except Exception as f:
            print("发布错误:", f)
            return HttpResponse("非常抱歉,名称为 {} 的帖子上传过程中出错,已跳过".format(title))
            # return render(request, "dida.html", {"message_result": "非常抱歉,上传过程中出错,请重新上传或者换一条房源"})
        cursor.close()
        cursor.close()
        new_object = models.awehomeinfos.objects.create(web_site="dida", title=title, refer=detail_url, awehome=awehomesrc)
        new_object.save()
        return HttpResponse("恭喜您,名称为 {} 的帖子发布完毕".format(title))


def bingtang(request):
    # 判断是否登陆，没有登录就返回登录界面
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "bingtang.html")
        else:
            return render(request, "login.html")

    # POST请求的话就拿到前端发过来的数据
    else:
        quhao = request.POST.get("quhao")
        username = request.POST.get("username")
        password = request.POST.get("password")
        detail_url = request.POST.get("detail_url")
        from APP01 import models
        filter_object = models.awehomeinfos.objects.filter(refer=detail_url).first()
        if filter_object:
            return HttpResponse("非常抱歉,这条房源已在Awehome平台存在,请另外寻找上传")

        from APP01.config.rk import RClient
        import requests
        import json
        import time
        import re
        from requests_toolbelt import MultipartEncoder
        import upyun
        requests = requests.session()
        # 抓取第三方房源标题、价格、等信息
        try:
            detail_id = re.findall(r'rid=(\d{4})', detail_url)[0]
            real_detail_url = "http://www.islistings.com/index.php?g=api&m=room&a=get_houseinfo&id={}".format(detail_id)
            response = json.loads(requests.get(url=real_detail_url).content.decode())
            houseinfo = response["houseinfo"]
            room = response["rooms"][0]

            detail_addr = houseinfo["area"]
            start_addr = re.findall(r'(.*?),', detail_addr)[0]
            houseinfo_type = houseinfo["room_type"]
            rent_type = houseinfo["rent_type"]
            title = (start_addr + houseinfo_type + " " + rent_type)[0:30]
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,上传失败,请再次确认输入的url来源是否为冰糖房源")

        img_src_list = json.loads(houseinfo["img"])
        if img_src_list == None:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有图片,已跳过".format(title))
        img_src_list = img_src_list["photo"]
        if len(img_src_list) < 3:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息图片少于三张,已跳过".format(title))

        price = room["rent_price"].replace("$", "")
        if price == "价格面议":
            price = 0
        else:
            price = room["rent_price"].replace("$", "").replace("/周", "")
        bedroomNum = houseinfo["woshi"]
        if bedroomNum == "0":
            bedroomNum = "2"
        bathroomNum = houseinfo["weiyu"]
        if bathroomNum == "0":
            bathroomNum = "2"
        # jingdu = houseinfo["jingdu"]
        # weidu = houseinfo["weidu"]
        id = houseinfo["id"]
        detail_json_response = json.loads(requests.get(
            "http://www.islistings.com/index.php?g=api&m=room&a=get_houseinfo&id={}".format(id)).content.decode())[
            "houseinfo"]
        phone = [detail_json_response["phone"]][0]
        weixin = [detail_json_response["weixin"]][0]

        now_startDate = time.strftime("%Y-%m-%d", time.localtime())
        finally_desc = houseinfo["s_desc"]
        if finally_desc == None:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有详情描述,已跳过".format(title))
        if len(finally_desc) > 500:
            finally_desc = finally_desc[0:500]
        try:
            # 实例化又拍云对象
            rc = RClient('awehome', 'xQiFb76y6hJCTe6', '119809', '0202040b5e4647cb8a0cc60c822e986d')
            # 实例化若快打码对象
            up = upyun.UpYun(service="house-image", username="awehomezhangxiaowei", password="awehomezhangxiaowei")
        except Exception as f:
            print("登陆错误:", f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))

        # 发送验证码图片,拿到验证码字符串
        awehome_login_code = requests.get("http://awehome.com.cn/site/captcha?refresh=true").content.decode()
        img_src = "http://awehome.com.cn" + json.loads(awehome_login_code)["url"]
        img_response = requests.get(img_src).content
        img_fonz = json.loads(rc.rk_create(img_response, 3040))["Result"]

        # 登录
        post_login_url = "http://awehome.com.cn/landlord/login"
        post_login_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Length": "169",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_identity=c308968c88fdbbce9551e193975a3546914ee428af7607951aaac678e8618ffaa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B6112%2C%22PK7GArlTBAPCkespZ0pku4qAns6S6rXo%22%2C604800%5D%22%3B%7D; expires=Tue, 15-Jan-2019 07:36:56 GMT; Max-Age=604800; path=/; HttpOnly",
            "Host": "awehome.com.cn",
            "Origin": "http://awehome.com.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://awehome.com.cn/tenant/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        post_login_data = {
            "referer": "http://awehome.com.cn/",
            "Login[dialcode]": str(quhao),
            "Login[phone]": str(username),
            "Login[captcha]": str(img_fonz),
            "Login[password]": str(password),
            "Login[rememberMe]": "0",
        }
        post_login_response = requests.post(url=post_login_url, headers=post_login_headers,data=post_login_data, ).content.decode()
        print(post_login_response)
        try:
            result_error = json.loads(post_login_response)["errors"]
            if "password" in result_error.keys():
                return HttpResponse("非常抱歉,您输入的用户名或密码错误,请重新输入")
            if "captcha" in result_error.keys():
                return HttpResponse("非常抱歉,登录Awehome过程中验证码错误,此条房源url为     {}".format(detail_url))
        except Exception:
            pass

        # 从前端拿到房源链接进行发布
        try:
            # 访问发布界面
            requests.get("http://awehome.com.cn/housing/create").content.decode()

            # 自动发布帖子
            post_publish_url = "http://awehome.com.cn/housing/create"
            post_publish_headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Date": "Wed, 09 Jan 2019 08:02:58 GMT",
                "Expires": "Thu, 19 Nov 1981 08:52:00 GMT",
                "Pragma": "no-cache",
                "Server": "nginx/1.10.3 (Ubuntu)",
                "Set-Cookie": "_identity=09ce810bc65bd52e6903f36268fc5b50ff1c77e3acea40021410655b598d853ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B3049%2C%22dU1uwbSvekMvFSANgsROwP8y55vq0D1q%22%2C604800%5D%22%3B%7D; expires=Wed, 16-Jan-2019 08:02:58 GMT; Max-Age=604800; path=/; HttpOnly",
                # "Transfer-Encoding": "chunked",
                "X-Powered-By": "PHP/7.1.13",
            }

            post_publish_data = {
                # 第一页请求
                "Housing[form]": "uploadForm",
                "Housing[view]": "form",
                "Housing[rentalType]": "2",  # 出租类型 独立房间
                "Housing[houseType]": "1",  # 户型 公寓
                "Housing[bedroomNum]": str(bedroomNum),  # 卧室数量 2
                "Housing[bathroomNum]": str(bathroomNum),  # 卫浴数量 2
                "Housing[occupancyNum]": "2",  # 总住人数 2
                "Housing[isFurniture]": "1",  # 是否包含家具 包含
                # 第二页请求
                "Housing[countryId]": "4",  # 国家 英国
                "Housing[cityId]": "4",  # 城市 伦敦
                "Housing[mapCoordinate]": "153.02512350000006,-27.4697707",  # 地址 坐标
                "Housing[mapDescribe]": str(detail_addr),  # "A4, London WC2N 5DU英国", #详细地址
                "Housing[housingSchool][0][id]": "15",  # 附近学校0 悉尼大学
                "Housing[housingSchool][0][text]": "",  # 距离描述0
                "Housing[housingSchool][1][id]": "20",  # 附近学校1 悉尼科技大学
                "Housing[housingSchool][1][text]": "",  # 距离描述1
                "Housing[housingSchool][2][id]": "38",  # 附近学校2 新南威尔士大学
                "Housing[housingSchool][2][text]": "",  # 距离描述2
                # 第三页请求
                "Housing[housingFacilities][22]": "22",  # 设施 洗衣机、电视、冰箱、WIFI、空调、厨房、阳台、电梯、包bill
                "Housing[housingFacilities][23]": "23",  # 设施
                "Housing[housingFacilities][24]": "24",  # 设施
                "Housing[housingFacilities][25]": "25",  # 设施
                "Housing[housingFacilities][26]": "26",  # 设施
                "Housing[housingFacilities][27]": "27",  # 设施
                "Housing[housingFacilities][28]": "28",  # 设施
                "Housing[housingFacilities][29]": "29",  # 设施
                "Housing[housingFacilities][30]": "30",  # 设施
                "Housing[housingPeriphery][50][id]": "50",  # 周边 超市、游泳池、健身房、火车站、公交站
                "Housing[housingPeriphery][50][text]": "",  # 描述说明
                "Housing[housingPeriphery][6][id]": "6",  # 周边
                "Housing[housingPeriphery][6][text]": "",  # 描述说明
                "Housing[housingPeriphery][7][id]": "7",  # 周边
                "Housing[housingPeriphery][7][text]": "",  # 描述说明
                "Housing[housingPeriphery][8][id]": "8",  # 周边
                "Housing[housingPeriphery][8][text]": "",  # 描述说明
                "Housing[housingPeriphery][9][id]": "9",  # 周边
                "Housing[housingContact][293][id]": "293",  # 微信参数相关
                "Housing[housingContact][293][text]": weixin,  # 微信号
                "Housing[housingPeriphery][9][text]": "",  # 描述说明
                "Housing[housingContact][294][id]": "294",  # 手机号参数相关
                "Housing[housingContact][294][text]": str(phone),  # 手机号
                "Housing[introText]": str(finally_desc),  # 其他介绍
                # 第四页请求
                "Housing[name][2]": str(title),  # "最后一间房子出租",#标题
                "Housing[housingHouse][2][0][singleType]": "1",  # 独立房间类型 主卧
                "Housing[housingHouse][2][0][bedType]": "2",  # 床型 双人床
                "Housing[housingHouse][2][0][bedNum]": "1",  # 床位数
                "Housing[housingHouse][2][0][isBathroom]": "1",  # 独立卫浴 是
                "Housing[housingHouse][2][0][price]": str(price),  # "500",#价格 500英镑GBP/每周
                "Housing[housingHouse][2][0][startDate]": str(now_startDate),  # "2019-01-10",#起租日期
                "Housing[housingHouse][2][0][leaseType]": "1",  # 租期 租期不限
                # 第五页请求-上传图片
                "Housing[housingHouse][2][0][upload][0][imageId]": "0",
                # "Housing[housingHouse][2][0][upload][0][imageUrl]": "",
                "Housing[housingHouse][2][0][upload][0][imageFile]": "",
                # "filename": "blob",
                # "Content-Type": "image/jpegahttp://bbs.tigtag.com/a1546698533817019500.html",
            }
            m = MultipartEncoder(post_publish_data)
            post_publish_headers['Content-Type'] = m.content_type
            post_publish_response = json.loads(
                requests.post(url=post_publish_url, headers=post_publish_headers, data=m).content.decode())
            print(post_publish_response)
            housing_key = post_publish_response["id"]

            # 已发布成功的awehome房源详情链接
            awehomesrc = "http://awehome.com.cn/housing/view?id={}".format(housing_key)

            # 连接数据库，并创建游标
            from APP01.config.connect_mysql import conn_MySQL
            db = conn_MySQL(
                host="47.91.43.200",
                port=3315,
                user="awehome",
                password="AFrokRANYodgYqfdnCpHc4RA",
                database="awehome",
                charset="utf8"
            )

            cursor = db.cursor()

            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            sql = 'select * from aweh_housing where housing_key={}'.format(housing_key)
            cursor.execute(sql)
            result = cursor.fetchall()
            housing_id = result[0][0]

            # # 往Awehome封面图里面上传从滴答网获取到的第一张图片
            #     img_src = img_src_list[0]
            #     img_src = "http://cdn2.aus5.com/a/{}/{}!pc-a".format(tid, img_src)
            #     img_name = re.findall(r'\d/(.*?).gif', img_src)[0] + ".jpg"
            #
            #
            #     #向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
            #     tasks = [{"url": img_src, "random": False, "overwrite": True, "save_as": "/dida/{}".format(img_name)}]
            #     response = up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
            #     awehome_sql_img = "http://img.awehome.com.cn/dida/{}".format(img_name)
            #
            #
            #     # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
            #     sql = 'insert into aweh_housing_house_image(housing_house_id,housing_id,image_url,status) values ({},{},"{}",{})'.format(housing_house_id, housing_id, awehome_sql_img, 10)
            #     cursor.execute(sql)
            #     db.commit()

            # 往Awehome其他图片里面上传从滴答网获取到的除了第一张照片之外的其他图片
            # 往Awehome其他图片里面上传所有图片

            for img_src in img_src_list:
                img_src = "https://images.islistings.com/data/upload/thumb/{}".format(img_src["url"])
                img_name = re.findall(r'thumb/(.*?).jpg', img_src)

                # 向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
                tasks = [
                    {"url": img_src, "random": False, "overwrite": True, "save_as": "/bingtang/{}".format(img_name)}]
                response = up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
                awehome_sql_img = "http://img.awehome.com.cn/bingtang/{}!222".format(img_name)

                # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
                sql = 'insert into aweh_housing_image(housing_id,image_url,explain_text,status) values ({},"{}","",10)'.format(housing_id, awehome_sql_img)
                cursor.execute(sql)
                db.commit()

        except Exception as f:
            print("发布错误:", f)
            return HttpResponse("非常抱歉,名称为 {} 的帖子上传过程中出错,已跳过".format(title))
            # return render(request, "dida.html", {"message_result": "非常抱歉,上传过程中出错,请重新上传或者换一条房源"})
        cursor.close()
        cursor.close()
        new_object = models.awehomeinfos.objects.create(web_site="bingtang", title=title, refer=detail_url, awehome=awehomesrc)
        new_object.save()
        return HttpResponse("恭喜您,名称为 {} 的帖子发布完毕".format(title))


def wuba(request):
    if request.method == "POST":
        pass
    return render(request, "wuba.html")


def yiyi(request):
    # 判断是否登陆，没有登录就返回登录界面
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "yiyi.html")
        else:
            return render(request, "login.html")

    # POST请求的话就拿到前端发过来的数据
    else:
        city = request.POST.get("city")

        if city == "悉尼":
            city = 1
            school0 = "12"
            school1 = "17"
            school2 = "18"
            jingweidu = "151.20929550000005,-33.8688197"

        if city == "墨尔本":
            city = 2
            school0 = "10"
            school1 = "11"
            school2 = "19"
            jingweidu = "144.96305759999996,-37.8136276"
        if city == "布里斯班":
            city = 4
            school0 = "15"
            school1 = "20"
            school2 = "38"
            jingweidu = "153.02512350000006,-27.4697707"
        if city == "阿德莱德":
            city = 5
            school0 = "13"
            school1 = "31"
            school2 = "33"
            jingweidu = "138.60074559999998,-34.9284989"
        if city == "堪培拉":
            city = 3
            school0 = "14"
            school1 = "35"
            school2 = "87"
            jingweidu = "149.13000920000002,-35.2809368"

        quhao = request.POST.get("quhao")
        username = request.POST.get("username")
        password = request.POST.get("password")
        detail_url = request.POST.get("detail_url")
        from APP01 import models
        filter_object = models.awehomeinfos.objects.filter(refer=detail_url).first()
        if filter_object:
            return HttpResponse("非常抱歉,这条房源已在Awehome平台存在,请另外寻找上传")

        from APP01.config.rk import RClient
        import requests
        import json
        from lxml import etree
        import time
        import re
        from requests_toolbelt import MultipartEncoder
        import upyun

        requests = requests.session()

        # 抓取第三方房源标题、价格、等信息
        try:
            tid = re.findall(r'tid=(\d+)', detail_url)[0]
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,上传失败,请再次确认输入的url来源是否为滴答网")


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
        title = response["section_2"]["subject"].replace(",", "").replace("，", "").replace("！", "").replace("!",
                                                                                                            "").replace(
            "[", "").replace("]", "").replace("【", "").replace("】", "").replace(".", "").replace("。", "").replace("@",
                                                                                                                  "").replace(
            "#", "").replace("（", "").replace("*", "").replace("）", "").replace("-", "").replace("_", "").replace("/",
                                                                                                                  "").replace(
            "%", "").replace("$", "").replace("^", "").replace("&", "").replace("*", "").replace("(", "").replace(")",
                                                                                                                  "").replace(
            "█", "").replace("☆", "").replace("+", "").replace("、", "").replace("★", "").replace("|", "").replace("▂",
                                                                                                                  "").replace(
            "▃", "").replace("▆", "").replace("▇", "").replace("∎", "")[0:30]
        img_src_list = response["section_1"]
        if len(img_src_list) == 0:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有图片,已跳过".format(title))

        price_temp = response["section_2"]["house_rents"]
        price = re.findall(r'\$(\d+)/', price_temp)[0]
        phone = response["section_5"][1][1]
        weixin = response["section_5"][2][1]
        if len(weixin) == 0:
            weixin = ""
        finally_desc = response["section_4"]["message"].replace("<p>", "").replace("</p>", "").replace("\r\n", "")
        if len(finally_desc) == 0:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有详情描述,已跳过".format(title))
        detail_addr = response["section_2"]["address"]
        bedroomNum = response["section_2"]["house_room"]
        bathroomNum = response["section_2"]["house_toilet"]
        now_startDate = time.strftime("%Y-%m-%d", time.localtime())

        try:
            # 实例化又拍云对象
            rc = RClient('awehome', 'xQiFb76y6hJCTe6', '119809', '0202040b5e4647cb8a0cc60c822e986d')
            # 实例化若快打码对象
            up = upyun.UpYun(service="house-image", username="awehomezhangxiaowei", password="awehomezhangxiaowei")
        except Exception as f:
            print("登陆错误:", f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))

        # 发送验证码图片,拿到验证码字符串
        awehome_login_code = requests.get("http://awehome.com.cn/site/captcha?refresh=true").content.decode()
        img_src = "http://awehome.com.cn" + json.loads(awehome_login_code)["url"]
        img_response = requests.get(img_src).content
        img_fonz = json.loads(rc.rk_create(img_response, 3040))["Result"]

        # 登录
        post_login_url = "http://awehome.com.cn/landlord/login"
        post_login_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Length": "169",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_identity=c308968c88fdbbce9551e193975a3546914ee428af7607951aaac678e8618ffaa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B6112%2C%22PK7GArlTBAPCkespZ0pku4qAns6S6rXo%22%2C604800%5D%22%3B%7D; expires=Tue, 15-Jan-2019 07:36:56 GMT; Max-Age=604800; path=/; HttpOnly",
            "Host": "awehome.com.cn",
            "Origin": "http://awehome.com.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://awehome.com.cn/tenant/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        post_login_data = {
            "referer": "http://awehome.com.cn/",
            "Login[dialcode]": str(quhao),
            "Login[phone]": str(username),
            "Login[captcha]": str(img_fonz),
            "Login[password]": str(password),
            "Login[rememberMe]": "0",
        }
        post_login_response = requests.post(url=post_login_url, headers=post_login_headers,
                                            data=post_login_data, ).content.decode()
        print(post_login_response)
        try:
            result_error = json.loads(post_login_response)["errors"]
            if "password" in result_error.keys():
                return HttpResponse("非常抱歉,您输入的用户名或密码错误,请重新输入")
            if "captcha" in result_error.keys():
                return HttpResponse("非常抱歉,登录Awehome过程中验证码错误,此条房源url为     {}".format(detail_url))
        except Exception:
            pass

        # 从前端拿到房源链接进行发布
        try:
            # 访问发布界面
            requests.get("http://awehome.com.cn/housing/create").content.decode()

            # 自动发布帖子
            post_publish_url = "http://awehome.com.cn/housing/create"
            post_publish_headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Date": "Wed, 09 Jan 2019 08:02:58 GMT",
                "Expires": "Thu, 19 Nov 1981 08:52:00 GMT",
                "Pragma": "no-cache",
                "Server": "nginx/1.10.3 (Ubuntu)",
                "Set-Cookie": "_identity=09ce810bc65bd52e6903f36268fc5b50ff1c77e3acea40021410655b598d853ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B3049%2C%22dU1uwbSvekMvFSANgsROwP8y55vq0D1q%22%2C604800%5D%22%3B%7D; expires=Wed, 16-Jan-2019 08:02:58 GMT; Max-Age=604800; path=/; HttpOnly",
                # "Transfer-Encoding": "chunked",
                "X-Powered-By": "PHP/7.1.13",
            }

            post_publish_data = {
                # 第一页请求
                "Housing[form]": "uploadForm",
                "Housing[view]": "form",
                "Housing[rentalType]": "2",  # 出租类型 独立房间
                "Housing[houseType]": "1",  # 户型 公寓
                "Housing[bedroomNum]": str(bedroomNum),  # 卧室数量 2
                "Housing[bathroomNum]": str(bathroomNum),  # 卫浴数量 2
                "Housing[occupancyNum]": "2",  # 总住人数 2
                "Housing[isFurniture]": "1",  # 是否包含家具 包含
                # 第二页请求
                "Housing[countryId]": "4",  # 国家 英国
                "Housing[cityId]": str(city),  # 城市 伦敦
                "Housing[mapCoordinate]": str(jingweidu),  # 地址 坐标
                "Housing[mapDescribe]": str(detail_addr),  # "A4, London WC2N 5DU英国", #详细地址
                "Housing[housingSchool][0][id]": str(school0),  # 附近学校0 悉尼大学
                "Housing[housingSchool][0][text]": "",  # 距离描述0
                "Housing[housingSchool][1][id]": str(school1),  # 附近学校1 悉尼科技大学
                "Housing[housingSchool][1][text]": "",  # 距离描述1
                "Housing[housingSchool][2][id]": str(school2),  # 附近学校2 新南威尔士大学
                "Housing[housingSchool][2][text]": "",  # 距离描述2
                # 第三页请求
                "Housing[housingFacilities][22]": "22",  # 设施 洗衣机、电视、冰箱、WIFI、空调、厨房、阳台、电梯、包bill
                "Housing[housingFacilities][23]": "23",  # 设施
                "Housing[housingFacilities][24]": "24",  # 设施
                "Housing[housingFacilities][25]": "25",  # 设施
                "Housing[housingFacilities][26]": "26",  # 设施
                "Housing[housingFacilities][27]": "27",  # 设施
                "Housing[housingFacilities][28]": "28",  # 设施
                "Housing[housingFacilities][29]": "29",  # 设施
                "Housing[housingFacilities][30]": "30",  # 设施
                "Housing[housingPeriphery][50][id]": "50",  # 周边 超市、游泳池、健身房、火车站、公交站
                "Housing[housingPeriphery][50][text]": "",  # 描述说明
                "Housing[housingPeriphery][6][id]": "6",  # 周边
                "Housing[housingPeriphery][6][text]": "",  # 描述说明
                "Housing[housingPeriphery][7][id]": "7",  # 周边
                "Housing[housingPeriphery][7][text]": "",  # 描述说明
                "Housing[housingPeriphery][8][id]": "8",  # 周边
                "Housing[housingPeriphery][8][text]": "",  # 描述说明
                "Housing[housingPeriphery][9][id]": "9",  # 周边
                "Housing[housingContact][293][id]": "293",  # 微信参数相关
                "Housing[housingContact][293][text]": str(weixin),  # 微信号
                "Housing[housingPeriphery][9][text]": "",  # 描述说明
                "Housing[housingContact][294][id]": "294",  # 手机号参数相关
                "Housing[housingContact][294][text]": str(phone),  # 手机号
                "Housing[introText]": str(finally_desc),  # 其他介绍
                # 第四页请求
                "Housing[name][2]": str(title),  # "最后一间房子出租",#标题
                "Housing[housingHouse][2][0][singleType]": "1",  # 独立房间类型 主卧
                "Housing[housingHouse][2][0][bedType]": "2",  # 床型 双人床
                "Housing[housingHouse][2][0][bedNum]": "1",  # 床位数
                "Housing[housingHouse][2][0][isBathroom]": "1",  # 独立卫浴 是
                "Housing[housingHouse][2][0][price]": str(price),  # "500",#价格 500英镑GBP/每周
                "Housing[housingHouse][2][0][startDate]": str(now_startDate),  # "2019-01-10",#起租日期
                "Housing[housingHouse][2][0][leaseType]": "1",  # 租期 租期不限
                # 第五页请求-上传图片
                "Housing[housingHouse][2][0][upload][0][imageId]": "0",
                # "Housing[housingHouse][2][0][upload][0][imageUrl]": "",
                "Housing[housingHouse][2][0][upload][0][imageFile]": "",
                # "filename": "blob",
                # "Content-Type": "image/jpegahttp://bbs.tigtag.com/a1546698533817019500.html",
            }
            m = MultipartEncoder(post_publish_data)
            post_publish_headers['Content-Type'] = m.content_type
            post_publish_response = json.loads(
                requests.post(url=post_publish_url, headers=post_publish_headers, data=m).content.decode())
            print(post_publish_response)
            housing_key = post_publish_response["id"]

            # 已发布成功的awehome房源详情链接
            awehomesrc = "http://awehome.com.cn/housing/view?id={}".format(housing_key)

            # 连接数据库，并创建游标
            from APP01.config.connect_mysql import conn_MySQL
            db = conn_MySQL(
                host="47.91.43.200",
                port=3315,
                user="awehome",
                password="AFrokRANYodgYqfdnCpHc4RA",
                database="awehome",
                charset="utf8"
            )

            cursor = db.cursor()


            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            sql = 'select * from aweh_housing where housing_key={}'.format(housing_key)
            cursor.execute(sql)
            result = cursor.fetchall()
            housing_id = result[0][0]

            # 往Awehome其他图片里面上传所有图片
            for img_src in img_src_list:
                img_name = re.findall(r'\d+/\d+/(.*?).jpg', img_src)[0]


                #向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
                tasks = [{"url": img_src, "random": False, "overwrite": True, "save_as": "/yiyi/{}".format(img_name)}]
                up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
                awehome_sql_img = "http://img.awehome.com.cn/yiyi/{}".format(img_name)


                # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
                sql = 'insert into aweh_housing_image(housing_id,image_url,explain_text,status) values ({},"{}","",10)'.format(housing_id, awehome_sql_img)
                cursor.execute(sql)
                db.commit()

        except Exception as f:
            print("发布错误:", f)
            return HttpResponse("非常抱歉,名称为 {} 的帖子上传过程中出错,已跳过".format(title))
            # return render(request, "dida.html", {"message_result": "非常抱歉,上传过程中出错,请重新上传或者换一条房源"})
        cursor.close()
        cursor.close()
        new_object = models.awehomeinfos.objects.create(web_site="yiyi", title=title, refer=detail_url, awehome=awehomesrc)
        new_object.save()
        return HttpResponse("恭喜您,名称为 {} 的帖子发布完毕".format(title))


def sgroom(request):
    # 判断是否登陆，没有登录就返回登录界面
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "sgroom.html")
        else:
            return render(request, "login.html")

    # POST请求的话就拿到前端发过来的数据
    else:
        quhao = request.POST.get("quhao")
        username = request.POST.get("username")
        password = request.POST.get("password")
        detail_url = request.POST.get("detail_url")
        from APP01 import models
        filter_object = models.awehomeinfos.objects.filter(refer=detail_url).first()
        if filter_object:
            return HttpResponse("非常抱歉,这条房源已在Awehome平台存在,请另外寻找上传")

        from APP01.config.rk import RClient
        import requests
        import json
        from lxml import etree
        import time
        import re
        from requests_toolbelt import MultipartEncoder
        import upyun
        requests = requests.session()
        # 抓取第三方房源标题、价格、等信息
        try:
            url_id = re.findall(r'post/(\d+)', detail_url)[0]
            response = requests.get(url=detail_url).content.decode()
            HTML = etree.HTML(response)
            title = HTML.xpath('//span[@class="post-title"]/text()')[0].replace("，", "").replace("！", "").replace("[", "").replace("]", "").replace("【", "").replace("】", "").replace(".", "").replace("。", "").replace("@", "").replace("#", "").replace("（", "").replace("*", "").replace("）", "").replace(r",", "").replace("-", "").replace("_", "").replace("/", "").replace("%", "").replace("$", "").replace("^", "").replace("&", "").replace("*", "").replace("(", "").replace(")", "").replace("█", "").replace("☆", "").replace("+", "").replace("、", "").replace("★", "").replace("|", "").replace("!", "").replace("$", "").replace(":", "").replace("：", "")[0:30]
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,上传失败,请再次确认输入的url来源是否为SGroom")
        # 拿到所有图片地址列表
        img_src_list1 = HTML.xpath('//div[@class="fotorama__nav__shaft"]//img//@src')
        img_src_list2 = HTML.xpath('//div[@class="fotorama"]/a/@src')
        if len(img_src_list1) == 0 and len(img_src_list2) == 0:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有图片,已跳过".format(title))
        if len(img_src_list1) == 0:
            img_src_list = img_src_list2
        if len(img_src_list1) > 0:
            img_src_list = img_src_list1
        if len(img_src_list) < 3:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息图片少于三张,已跳过".format(title))

        detail_desc_list = HTML.xpath('//div[@class="row layout-block description-block"][2]/div[@class="col-12"][1]//text()')
        if len(detail_desc_list) == 0:
            return HttpResponse("非常抱歉,标题为 {} 的房源信息没有详情描述,已跳过".format(title))
        finally_desc = ""
        for detail_desc in detail_desc_list:
            finally_desc += detail_desc
        # 判断其他描述长度是否大于五百字符，大于五百就取前五百个字节
        if len(finally_desc) > 500:
            finally_desc = finally_desc[0:500]

        price = HTML.xpath('//span[@class="price-value"]/text()')[0].replace("&nbsp", "")
        detail_addr = HTML.xpath('//div[@class="container main-shadow"]/div[@class="row layout-block description-block"][1]/div[@class="col-sm-6 col-12"]/div[@class="row parameter-row"][5]/div[@class="col-7 parameter-item"]/span/text()')[0]
        phone_first = re.findall(r'phone_first = "(.*?)";', response)[0]
        phone_second = re.findall(r'phone_second = "(.*?)";', response)[0]
        phone = phone_first + phone_second
        weixin = ""
        bedroomNum = "2"
        bathroomNum = "2"
        now_startDate = time.strftime("%Y-%m-%d", time.localtime())
        try:
            # 实例化又拍云对象
            rc = RClient('awehome', 'xQiFb76y6hJCTe6', '119809', '0202040b5e4647cb8a0cc60c822e986d')
            # 实例化若快打码对象
            up = upyun.UpYun(service="house-image", username="awehomezhangxiaowei", password="awehomezhangxiaowei")
        except Exception as f:
            print("登陆错误:", f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))

        # 发送验证码图片,拿到验证码字符串
        awehome_login_code = requests.get("http://awehome.com.cn/site/captcha?refresh=true").content.decode()
        img_src = "http://awehome.com.cn" + json.loads(awehome_login_code)["url"]
        img_response = requests.get(img_src).content
        img_fonz = json.loads(rc.rk_create(img_response, 3040))["Result"]

        # 登录
        post_login_url = "http://awehome.com.cn/landlord/login"
        post_login_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Length": "169",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_identity=c308968c88fdbbce9551e193975a3546914ee428af7607951aaac678e8618ffaa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B6112%2C%22PK7GArlTBAPCkespZ0pku4qAns6S6rXo%22%2C604800%5D%22%3B%7D; expires=Tue, 15-Jan-2019 07:36:56 GMT; Max-Age=604800; path=/; HttpOnly",
            "Host": "awehome.com.cn",
            "Origin": "http://awehome.com.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://awehome.com.cn/tenant/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        post_login_data = {
            "referer": "http://awehome.com.cn/",
            "Login[dialcode]": str(quhao),
            "Login[phone]": str(username),
            "Login[captcha]": str(img_fonz),
            "Login[password]": str(password),
            "Login[rememberMe]": "0",
        }
        post_login_response = requests.post(url=post_login_url, headers=post_login_headers,data=post_login_data, ).content.decode()
        print(post_login_response)
        try:
            result_error = json.loads(post_login_response)["errors"]
            if "password" in result_error.keys():
                return HttpResponse("非常抱歉,您输入的用户名或密码错误,请重新输入")
            if "captcha" in result_error.keys():
                return HttpResponse("非常抱歉,登录Awehome过程中验证码错误,此条房源url为     {}".format(detail_url))
        except Exception:
            pass

        # 从前端拿到房源链接进行发布
        try:
            # 访问发布界面
            requests.get("http://awehome.com.cn/housing/create").content.decode()

            # 自动发布帖子
            post_publish_url = "http://awehome.com.cn/housing/create"
            post_publish_headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Date": "Wed, 09 Jan 2019 08:02:58 GMT",
                "Expires": "Thu, 19 Nov 1981 08:52:00 GMT",
                "Pragma": "no-cache",
                "Server": "nginx/1.10.3 (Ubuntu)",
                "Set-Cookie": "_identity=09ce810bc65bd52e6903f36268fc5b50ff1c77e3acea40021410655b598d853ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B3049%2C%22dU1uwbSvekMvFSANgsROwP8y55vq0D1q%22%2C604800%5D%22%3B%7D; expires=Wed, 16-Jan-2019 08:02:58 GMT; Max-Age=604800; path=/; HttpOnly",
                # "Transfer-Encoding": "chunked",
                "X-Powered-By": "PHP/7.1.13",
            }

            post_publish_data = {
                # 第一页请求
                "Housing[form]": "uploadForm",
                "Housing[view]": "form",
                "Housing[rentalType]": "2",  # 出租类型 独立房间
                "Housing[houseType]": "1",  # 户型 公寓
                "Housing[bedroomNum]": str(bedroomNum),  # 卧室数量 2
                "Housing[bathroomNum]": str(bathroomNum),  # 卫浴数量 2
                "Housing[occupancyNum]": "2",  # 总住人数 2
                "Housing[isFurniture]": "1",  # 是否包含家具 包含
                # 第二页请求
                "Housing[countryId]": "255",  # 国家 英国
                "Housing[cityId]": "83",  # 城市 伦敦
                "Housing[mapCoordinate]": "103.81983600000001,1.352083",  # 地址 坐标
                "Housing[mapDescribe]": str(detail_addr),  # "A4, London WC2N 5DU英国", #详细地址
                "Housing[housingSchool][0][id]": "256",  # 附近学校0 悉尼大学
                "Housing[housingSchool][0][text]": "",  # 距离描述0
                "Housing[housingSchool][1][id]": "265",  # 附近学校1 悉尼科技大学
                "Housing[housingSchool][1][text]": "",  # 距离描述1
                "Housing[housingSchool][2][id]": "266",  # 附近学校2 新南威尔士大学
                "Housing[housingSchool][2][text]": "",  # 距离描述2
                # 第三页请求
                "Housing[housingFacilities][22]": "22",  # 设施 洗衣机、电视、冰箱、WIFI、空调、厨房、阳台、电梯、包bill
                "Housing[housingFacilities][23]": "23",  # 设施
                "Housing[housingFacilities][24]": "24",  # 设施
                "Housing[housingFacilities][25]": "25",  # 设施
                "Housing[housingFacilities][26]": "26",  # 设施
                "Housing[housingFacilities][27]": "27",  # 设施
                "Housing[housingFacilities][28]": "28",  # 设施
                "Housing[housingFacilities][29]": "29",  # 设施
                "Housing[housingFacilities][30]": "30",  # 设施
                "Housing[housingPeriphery][50][id]": "50",  # 周边 超市、游泳池、健身房、火车站、公交站
                "Housing[housingPeriphery][50][text]": "",  # 描述说明
                "Housing[housingPeriphery][6][id]": "6",  # 周边
                "Housing[housingPeriphery][6][text]": "",  # 描述说明
                "Housing[housingPeriphery][7][id]": "7",  # 周边
                "Housing[housingPeriphery][7][text]": "",  # 描述说明
                "Housing[housingPeriphery][8][id]": "8",  # 周边
                "Housing[housingPeriphery][8][text]": "",  # 描述说明
                "Housing[housingPeriphery][9][id]": "9",  # 周边
                "Housing[housingContact][293][id]": "293",  # 微信参数相关
                "Housing[housingContact][293][text]": str(weixin),  # 微信号
                "Housing[housingPeriphery][9][text]": "",  # 描述说明
                "Housing[housingContact][294][id]": "294",  # 手机号参数相关
                "Housing[housingContact][294][text]": str(phone),  # 手机号
                "Housing[introText]": str(finally_desc),  # 其他介绍
                # 第四页请求
                "Housing[name][2]": str(title),  # "最后一间房子出租",#标题
                "Housing[housingHouse][2][0][singleType]": "1",  # 独立房间类型 主卧
                "Housing[housingHouse][2][0][bedType]": "2",  # 床型 双人床
                "Housing[housingHouse][2][0][bedNum]": "1",  # 床位数
                "Housing[housingHouse][2][0][isBathroom]": "1",  # 独立卫浴 是
                "Housing[housingHouse][2][0][price]": str(price),  # "500",#价格 500英镑GBP/每周
                "Housing[housingHouse][2][0][startDate]": str(now_startDate),  # "2019-01-10",#起租日期
                "Housing[housingHouse][2][0][leaseType]": "1",  # 租期 租期不限
                # 第五页请求-上传图片
                "Housing[housingHouse][2][0][upload][0][imageId]": "0",
                # "Housing[housingHouse][2][0][upload][0][imageUrl]": "",
                "Housing[housingHouse][2][0][upload][0][imageFile]": "",
                # "filename": "blob",
                # "Content-Type": "image/jpegahttp://bbs.tigtag.com/a1546698533817019500.html",
            }
            m = MultipartEncoder(post_publish_data)
            post_publish_headers['Content-Type'] = m.content_type
            post_publish_response = json.loads(
                requests.post(url=post_publish_url, headers=post_publish_headers, data=m).content.decode())
            print(post_publish_response)
            housing_key = post_publish_response["id"]

            # 已发布成功的awehome房源详情链接
            awehomesrc = "http://awehome.com.cn/housing/view?id={}".format(housing_key)

            # 连接数据库，并创建游标
            from APP01.config.connect_mysql import conn_MySQL
            db = conn_MySQL(
                host="47.91.43.200",
                port=3315,
                user="awehome",
                password="AFrokRANYodgYqfdnCpHc4RA",
                database="awehome",
                charset="utf8"
            )

            cursor = db.cursor()

            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            sql = 'select * from aweh_housing where housing_key={}'.format(housing_key)
            cursor.execute(sql)
            result = cursor.fetchall()
            housing_id = result[0][0]

            # 往Awehome其他图片里面上传所有图片
            count = 1
            for img_src in img_src_list:
                img_src_name = url_id + "_" + str(count)
                img_src_b = requests.get(img_src).content
                count += 1

                # 向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
                up.put('/sgroom/{}'.format(img_src_name), img_src_b, checksum=True)
                awehome_sql_img = "http://img.awehome.com.cn/sgroom/{}".format(img_src_name)

                # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
                sql = 'insert into aweh_housing_image(housing_id,image_url,explain_text,status) values ({},"{}","",10)'.format(housing_id, awehome_sql_img)
                cursor.execute(sql)
                db.commit()

        except Exception as f:
            print("发布错误:", f)
            return HttpResponse("非常抱歉,名称为 {} 的帖子上传过程中出错,已跳过".format(title))
            # return render(request, "dida.html", {"message_result": "非常抱歉,上传过程中出错,请重新上传或者换一条房源"})
        cursor.close()
        cursor.close()
        new_object = models.awehomeinfos.objects.create(web_site="sgroom", title=title, refer=detail_url,awehome=awehomesrc)
        new_object.save()
        return HttpResponse("恭喜您,名称为 {} 的帖子发布完毕".format(title))


def yingniao(request):
    # 判断是否登陆，没有登录就返回登录界面
    if request.method == "GET":
        login_cookies = request.COOKIES.get("cookies")
        if login_cookies == "aaaaaa":
            return render(request, "yingniao.html")
        else:
            return render(request, "login.html")

    # POST请求的话就拿到前端发过来的数据
    else:
        city = request.POST.get("city")

        if city == "伦敦":
            city = 19
            school0 = "61"
            school1 = "108"
            school2 = "109"
            jingweidu = "-0.12775829999998223,51.5073509"

        if city == "曼彻斯特":
            city = 36
            school0 = "234"
            school1 = "235"
            school2 = "237"
            jingweidu = "-2.2426305000000184,53.4807593"

        if city == "伯明翰":
            city = 39
            school0 = "231"
            school1 = "232"
            school2 = "233"
            jingweidu = "-1.8904009999999971,52.48624299999999"

        quhao = request.POST.get("quhao")
        username = request.POST.get("username")
        password = request.POST.get("password")
        detail_url = request.POST.get("detail_url")
        from APP01 import models
        filter_object = models.awehomeinfos.objects.filter(refer=detail_url).first()
        if filter_object:
            return HttpResponse("非常抱歉,这条房源已在Awehome平台存在,请另外寻找上传")

        from APP01.config.rk import RClient
        import requests
        import json
        from lxml import etree
        import time
        import re
        from requests_toolbelt import MultipartEncoder
        import upyun

        requests = requests.session()

        # 抓取第三方房源标题、价格、等信息
        try:
            detail_response = requests.get(detail_url).content.decode()
            HTML = etree.HTML(detail_response)
            title = HTML.xpath('//p[@class="infoTitle"]/text()')[0].replace("，", "").replace("！", "").replace("[", "").replace("]", "").replace("【", "").replace("】", "").replace(".", "").replace("。", "").replace("@", "").replace("#", "").replace("（", "").replace("*", "").replace("）", "").replace(r",", "").replace("-", "").replace("_", "").replace("/", "").replace("%", "").replace("$", "").replace("^", "").replace("&", "").replace("*", "").replace("(", "").replace(")", "").replace("█", "").replace("☆", "").replace("+", "").replace("、", "").replace("★", "").replace("|", "").replace("!", "").replace("£", "").replace("$", "")[0:30]
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,上传失败,请再次确认输入的url来源是否为英鸟网")


        # 从房源详情页拿到图片地址列表
        img_src_list1 = HTML.xpath('//div[@class="newsList"]//a/@href')
        img_src_list2 = HTML.xpath('//div[@class="infoDetailMain"]//img/@src')
        if len(img_src_list1) == 0 and len(img_src_list2) == 0:
            return HttpResponse("名称为{}的房源没有图片,此条房源已跳过".format(title))
        if len(img_src_list1) == 0:
            img_src_list = img_src_list2
        if len(img_src_list1) > 0:
            img_src_list = img_src_list1

        if len(img_src_list) < 3:
            return HttpResponse("此条房源图片少于三张，已跳过")

        price = HTML.xpath('//span[@class="infoVal salaryVal"]/div/text()')[0]
        price = re.findall(r'(\d+)', price)[0]
        if price == "面议":
            price = "0"

        try:
            phone = HTML.xpath('//span[@class="infoVal telVal"]/div/text()')[0]
        except:
            phone = ""

        weixin = ""
        bedroomNum = "2"
        bathroomNum = "2"
        now_startDate = time.strftime("%Y-%m-%d", time.localtime())

        detail_addr = HTML.xpath('//div[@class="infoList"]/ul/li[3]/span[@class="infoVal"]/div/text()')
        try:
            if len(detail_addr) == 0:
                detail_addr = HTML.xpath('//div[@class="infoList"]/ul/li[3]/span[@class="infoVal "]/div/text()')[0]
            else:
                detail_addr = detail_addr[0]
        except Exception as f:
            print(f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))


        detail_desc_list = HTML.xpath('//div[@class="infoDetailMain"]//text()')
        if len(detail_desc_list) == 0:
            return HttpResponse("名称为{}的房源没有详情描述,此条房源已跳过".format(title))
        finally_desc = ""
        for detail_desc in detail_desc_list:
            finally_desc += detail_desc
        finally_desc = finally_desc.replace("\n", "")

        # 判断其他描述长度是否大于五百字符，大于五百就取前五百个字节
        if len(finally_desc) > 500:
            finally_desc = finally_desc[0:500]


        try:
            # 实例化又拍云对象
            rc = RClient('awehome', 'xQiFb76y6hJCTe6', '119809', '0202040b5e4647cb8a0cc60c822e986d')
            # 实例化若快打码对象
            up = upyun.UpYun(service="house-image", username="awehomezhangxiaowei", password="awehomezhangxiaowei")
        except Exception as f:
            print("登陆错误:", f)
            return HttpResponse("非常抱歉,标题为 {} 的房源信息发布过程中出错,已跳过".format(title))

        # 发送验证码图片,拿到验证码字符串
        awehome_login_code = requests.get("http://awehome.com.cn/site/captcha?refresh=true").content.decode()
        img_src = "http://awehome.com.cn" + json.loads(awehome_login_code)["url"]
        img_response = requests.get(img_src).content
        img_fonz = json.loads(rc.rk_create(img_response, 3040))["Result"]

        # 登录
        post_login_url = "http://awehome.com.cn/landlord/login"
        post_login_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Length": "169",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Cookie": "_identity=c308968c88fdbbce9551e193975a3546914ee428af7607951aaac678e8618ffaa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B6112%2C%22PK7GArlTBAPCkespZ0pku4qAns6S6rXo%22%2C604800%5D%22%3B%7D; expires=Tue, 15-Jan-2019 07:36:56 GMT; Max-Age=604800; path=/; HttpOnly",
            "Host": "awehome.com.cn",
            "Origin": "http://awehome.com.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://awehome.com.cn/tenant/login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        post_login_data = {
            "referer": "http://awehome.com.cn/",
            "Login[dialcode]": str(quhao),
            "Login[phone]": str(username),
            "Login[captcha]": str(img_fonz),
            "Login[password]": str(password),
            "Login[rememberMe]": "0",
        }
        post_login_response = requests.post(url=post_login_url, headers=post_login_headers,
                                            data=post_login_data, ).content.decode()
        print(post_login_response)

        try:
            result_error = json.loads(post_login_response)["errors"]
            if "password" in result_error.keys():
                return HttpResponse("非常抱歉,您输入的用户名或密码错误,请重新输入")
            if "captcha" in result_error.keys():
                return HttpResponse("非常抱歉,登录Awehome过程中验证码错误,此条房源url为     {}".format(detail_url))
        except Exception:
            pass

        # 从前端拿到房源链接进行发布
        try:
            # 访问发布界面
            requests.get("http://awehome.com.cn/housing/create").content.decode()

            # 自动发布帖子
            post_publish_url = "http://awehome.com.cn/housing/create"
            post_publish_headers = {
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "Date": "Wed, 09 Jan 2019 08:02:58 GMT",
                "Expires": "Thu, 19 Nov 1981 08:52:00 GMT",
                "Pragma": "no-cache",
                "Server": "nginx/1.10.3 (Ubuntu)",
                "Set-Cookie": "_identity=09ce810bc65bd52e6903f36268fc5b50ff1c77e3acea40021410655b598d853ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A48%3A%22%5B3049%2C%22dU1uwbSvekMvFSANgsROwP8y55vq0D1q%22%2C604800%5D%22%3B%7D; expires=Wed, 16-Jan-2019 08:02:58 GMT; Max-Age=604800; path=/; HttpOnly",
                # "Transfer-Encoding": "chunked",
                "X-Powered-By": "PHP/7.1.13",
            }

            post_publish_data = {
                # 第一页请求
                "Housing[form]": "uploadForm",
                "Housing[view]": "form",
                "Housing[rentalType]": "2",  # 出租类型 独立房间
                "Housing[houseType]": "1",  # 户型 公寓
                "Housing[bedroomNum]": str(bedroomNum),  # 卧室数量 2
                "Housing[bathroomNum]": str(bathroomNum),  # 卫浴数量 2
                "Housing[occupancyNum]": "2",  # 总住人数 2
                "Housing[isFurniture]": "1",  # 是否包含家具 包含
                # 第二页请求
                "Housing[countryId]": "60",  # 国家 英国
                "Housing[cityId]": str(city),  # 城市 伦敦
                "Housing[mapCoordinate]": str(jingweidu),  # 地址 坐标
                "Housing[mapDescribe]": str(detail_addr),  # "A4, London WC2N 5DU英国", #详细地址
                "Housing[housingSchool][0][id]": str(school0),  # 附近学校0 悉尼大学
                "Housing[housingSchool][0][text]": "",  # 距离描述0
                "Housing[housingSchool][1][id]": str(school1),  # 附近学校1 悉尼科技大学
                "Housing[housingSchool][1][text]": "",  # 距离描述1
                "Housing[housingSchool][2][id]": str(school2),  # 附近学校2 新南威尔士大学
                "Housing[housingSchool][2][text]": "",  # 距离描述2
                # 第三页请求
                "Housing[housingFacilities][22]": "22",  # 设施 洗衣机、电视、冰箱、WIFI、空调、厨房、阳台、电梯、包bill
                "Housing[housingFacilities][23]": "23",  # 设施
                "Housing[housingFacilities][24]": "24",  # 设施
                "Housing[housingFacilities][25]": "25",  # 设施
                "Housing[housingFacilities][26]": "26",  # 设施
                "Housing[housingFacilities][27]": "27",  # 设施
                "Housing[housingFacilities][28]": "28",  # 设施
                "Housing[housingFacilities][29]": "29",  # 设施
                "Housing[housingFacilities][30]": "30",  # 设施
                "Housing[housingPeriphery][50][id]": "50",  # 周边 超市、游泳池、健身房、火车站、公交站
                "Housing[housingPeriphery][50][text]": "",  # 描述说明
                "Housing[housingPeriphery][6][id]": "6",  # 周边
                "Housing[housingPeriphery][6][text]": "",  # 描述说明
                "Housing[housingPeriphery][7][id]": "7",  # 周边
                "Housing[housingPeriphery][7][text]": "",  # 描述说明
                "Housing[housingPeriphery][8][id]": "8",  # 周边
                "Housing[housingPeriphery][8][text]": "",  # 描述说明
                "Housing[housingPeriphery][9][id]": "9",  # 周边
                "Housing[housingContact][293][id]": "293",  # 微信参数相关
                "Housing[housingContact][293][text]": str(weixin),  # 微信号
                "Housing[housingPeriphery][9][text]": "",  # 描述说明
                "Housing[housingContact][294][id]": "294",  # 手机号参数相关
                "Housing[housingContact][294][text]": str(phone),  # 手机号
                "Housing[introText]": str(finally_desc),  # 其他介绍
                # 第四页请求
                "Housing[name][2]": str(title),  # "最后一间房子出租",#标题
                "Housing[housingHouse][2][0][singleType]": "1",  # 独立房间类型 主卧
                "Housing[housingHouse][2][0][bedType]": "2",  # 床型 双人床
                "Housing[housingHouse][2][0][bedNum]": "1",  # 床位数
                "Housing[housingHouse][2][0][isBathroom]": "1",  # 独立卫浴 是
                "Housing[housingHouse][2][0][price]": str(price),  # "500",#价格 500英镑GBP/每周
                "Housing[housingHouse][2][0][startDate]": str(now_startDate),  # "2019-01-10",#起租日期
                "Housing[housingHouse][2][0][leaseType]": "1",  # 租期 租期不限
                # 第五页请求-上传图片
                "Housing[housingHouse][2][0][upload][0][imageId]": "0",
                # "Housing[housingHouse][2][0][upload][0][imageUrl]": "",
                "Housing[housingHouse][2][0][upload][0][imageFile]": "",
                # "filename": "blob",
                # "Content-Type": "image/jpegahttp://bbs.tigtag.com/a1546698533817019500.html",
            }
            m = MultipartEncoder(post_publish_data)
            post_publish_headers['Content-Type'] = m.content_type
            post_publish_response = json.loads(
                requests.post(url=post_publish_url, headers=post_publish_headers, data=m).content.decode())
            print(post_publish_response)
            housing_key = post_publish_response["id"]

            # 已发布成功的awehome房源详情链接
            awehomesrc = "http://awehome.com.cn/housing/view?id={}".format(housing_key)

            # 连接数据库，并创建游标
            from APP01.config.connect_mysql import conn_MySQL
            db = conn_MySQL(
                host="47.91.43.200",
                port=3315,
                user="awehome",
                password="AFrokRANYodgYqfdnCpHc4RA",
                database="awehome",
                charset="utf8"
            )

            cursor = db.cursor()

            # 在aweh_housing表中通过housing_key这个字段找到新发布的这一条房源，然后找到housing_id
            sql = 'select * from aweh_housing where housing_key={}'.format(housing_key)
            cursor.execute(sql)
            result = cursor.fetchall()
            housing_id = result[0][0]

            # 往Awehome其他图片里面上传所有图片
            for img_src in img_src_list:
                img_src = "http://www.ybirds.com{}".format(img_src)
                img_name = re.findall(r'Class/(.*?).j|Class/(.*?).J|Class/(.*?).p|Class/(.*?).P', img_src)[0][0]
                #向又拍云发送图片，进行格式转换，拿到可以向Awehome数据库存储的图片地址
                tasks = [{"url": img_src, "random": False, "overwrite": True, "save_as": "/yingniao/{}".format(img_name)}]
                up.put_tasks(tasks, "https://hooks.upyun.com/ryieG_2f4", "spiderman")
                awehome_sql_img = "http://img.awehome.com.cn/yingniao/{}".format(img_name)
                # aweh_housing_house_image表中通过housing_id找到这一条数据，然后插入图片
                sql = 'insert into aweh_housing_image(housing_id,image_url,explain_text,status) values ({},"{}","",10)'.format(housing_id, awehome_sql_img)
                cursor.execute(sql)
                db.commit()

        except Exception as f:
            print("发布错误:", f)
            return HttpResponse("非常抱歉,名称为 {} 的帖子上传过程中出错,已跳过".format(title))
            # return render(request, "dida.html", {"message_result": "非常抱歉,上传过程中出错,请重新上传或者换一条房源"})
        cursor.close()
        cursor.close()
        new_object = models.awehomeinfos.objects.create(web_site="yingniao", title=title, refer=detail_url, awehome=awehomesrc)
        new_object.save()
        return HttpResponse("恭喜您,名称为 {} 的帖子发布完毕".format(title))


def test(request):
    # from APP01 import models
    # a = models.awehomeinfos.objects.create(title="张小伟", refer="b", awehome="c", web_site="dida")
    # a.save()
    return HttpResponse("test")