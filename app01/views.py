from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction  # 事务
from django.db.models import F
from django.conf import settings
from app01.view import views
from app01 import models
from io import BytesIO
from utils.random_check_code import rd_check_code
from utils import Bform, paging
import json, re, random, string, qrcode, time


def foo(fun):
    def wor(request):
        tk = request.session.get("name")
        if not tk:
            return redirect("/login/")
        else:
            x = fun(request)
            return x

    return wor


def index(request, *args, **kwargs):
    # 获取当前URL
    url = request.path_info
    condition = {}
    type_id = int(kwargs.get('type_id')) if kwargs.get('type_id') else None
    if type_id:
        condition['article_type_id'] = type_id
    article_obj = models.Article.objects.filter(**condition).order_by("-create_time")

    username = request.session.get("name")
    if not username:
        blog_url = "#"
    else:
        sit = models.Blog.objects.filter(user__username=username).first()
        if sit:
            blog_url = sit.site
        else:
            blog_url = "application/"
    type_list = models.Article.type_choices

    page = request.GET.get("page")
    if not page:
        page = 1
    count = article_obj.count()
    p = paging.Pageinfo(page, count, 10, url)
    article = article_obj[p.start():p.stop()]
    pager = p.pager()

    read_top10 = models.Article.objects.all().order_by("-read_count")[0:10]

    comment_top10 = models.Article.objects.all().order_by("-comment_count")[0:10]

    return render(request, "index.html",
                  {
                      "article": article,
                      "user": username,
                      "type_list": type_list,
                      "type_id": type_id,
                      "pager": pager,
                      "blog_url": blog_url,
                      "read": read_top10,
                      "comment": comment_top10,
                  }
                  )


def login(request):
    if request.method == "GET":
        obj = Bform.Login(request)
        return render(request, "pages-login.html", {"obj": obj})
    else:
        obj = Bform.Login(request, request.POST, request.FILES)
        if obj.is_valid():
            cok = redirect("/")
            request.session["name"] = obj.cleaned_data.get("username")
            request.session["id"] = obj.cleaned_data.get("password")
            if not request.POST.get("cookie"):
                request.session.set_expiry(86400)
            else:
                request.session.set_expiry(604800)
            return cok
        return render(request, "pages-login.html", {"obj": obj})


def login1(request):
    if request.method == "GET":
        obj = Bform.Login(request)
        return render(request, "login1.html", {"obj": obj})
    else:
        erweima = request.GET.get('mg')
        er_obj = models.Erweima.objects.filter(req=erweima).first()
        if er_obj.status:
            return HttpResponse("该二维码已失效")
        obj = Bform.Login(request, request.POST, request.FILES)
        if obj.is_valid():
            er_obj.status = 1
            er_obj.save()
            models.Login.objects.create(user_id=obj.cleaned_data.get("password"), erweima=er_obj)
            return redirect("/codesuccess.html/")
        else:
            return render(request, "login1.html", {"obj": obj})


def erweima(request):
    if request.method == "GET":
        req = "".join(random.sample(string.ascii_lowercase + string.ascii_uppercase, 10))
        img = qrcode.make(settings.LOGIN_URL + req)
        with open("static/codeimg/%s.jpg" % req, "wb") as f:
            img.save(f)
        img_url = settings.IMG_URL + req + ".jpg"
        res = {"req": req, "url": img_url}
        models.Erweima.objects.create(req=req)
        return HttpResponse(json.dumps(res))
    else:
        req = request.POST.get("req")
        res = {"status": True, "msg": None}
        erweima_obj = models.Erweima.objects.filter(req=req).first()
        timeArray = time.strptime(erweima_obj.create_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        now = int(time.time())
        if now >= timeStamp + erweima_obj.ctime:
            res["status"] = False
            res["msg"] = "该二维码已失效！"
        elif erweima_obj.status:
            user_obj = models.Login.objects.filter(erweima_id=erweima_obj.id).values("user__avatar", "user__nid",
                                                                                     "user__username").first()
            head_url = settings.BASE_URL + user_obj.get("user__avatar")
            res["msg"] = head_url
            request.session["name"] = user_obj.get("user__username")
            request.session["id"] = user_obj.get("user__nid")
            request.session.set_expiry(86400)

        return HttpResponse(json.dumps(res))


def codesuccess(request):
    if request.method == "GET":
        return render(request, "codesuccess.html")


def logout(request):
    request.session.delete(request.session.session_key)
    return redirect("/")


def page404(request):
    return render(request, "pages-404.html")


def register(request):
    if request.method == "GET":
        obj = Bform.Register(request)
        return render(request, "pages-register.html", {"obj": obj})
    else:
        obj = Bform.Register(request, request.POST, request.FILES)
        if obj.is_valid():
            newuser = obj.cleaned_data
            newuser.pop("pwd_again")
            # newuser.pop("code")
            newuser["nickname"] = newuser["username"]
            models.UserInfo.objects.create(**newuser)
            return redirect("/login/")

        else:
            return render(request, "pages-register.html", {"obj": obj})


@foo
def application(request):
    if request.method == "POST":
        res = {"status": True, "msg": None}
        text = request.POST.get("application").strip()
        if len(text) >= 20:
            application_obj = models.Application.objects.filter(user__username=request.session["name"]).first()
            if not application_obj:

                x = models.Application.objects.create(user_id=request.session.get("id"), text=text)
                if x:
                    res["msg"] = "您的申请已经提交到后台，等待审核！"
                else:
                    res["status"] = False
                    res["msg"] = "申请提交失败，请稍候再试！"
            elif application_obj.status == 0:
                res["status"] = False
                res["msg"] = "您已经提交过申请了。正在审核，请不要重复提交！"
            elif application_obj.status == 1:
                res["status"] = False
                res["msg"] = "您提交的申请被拒绝了。请下周一再提交申请！"
        else:
            res["status"] = False
            res["msg"] = "字数小于20个字！"

        return HttpResponse(json.dumps(res))
    else:
        blog_obj = models.Blog.objects.filter(user__username=request.session["name"]).first()
        if not blog_obj:
            return render(request, "application.html")
        else:
            return redirect("/")


def check_code(request):
    img, code = rd_check_code()
    stream = BytesIO()
    img.save(stream, 'png')
    request.session['code'] = code
    return HttpResponse(stream.getvalue())


def user_blog(request, *args, **kwargs):
    site = kwargs.get("user")
    obj = models.Blog.objects.filter(site=site).first()
    if not obj:
        return render(request, "application.html")
    request.session["bid"] = obj.nid
    article = obj.article_set.all()

    dict = views.user_blog(request, obj, article, *kwargs, **kwargs)  # 调用app01.view.views中的函数拿到个人博客主页必须的值

    return render(request, "blog.html", dict)


def tag_blog(request, *args, **kwargs):
    path = request.path_info.strip("/").split("/")
    tid = kwargs.get("tid", None)
    year = kwargs.get("year", None)
    mouth = kwargs.get("mouth", None)
    type = path[1]
    site = path[0]
    user = site

    obj = models.Blog.objects.filter(site=site).first()
    if not obj:
        return redirect("/")

    if type == "tag":
        article = models.Article.objects.filter(blog__user__username=user, tags__nid=tid)  # article2tag__tag_id=tid,
    elif type == "category":
        article = models.Article.objects.filter(category_id=tid, blog__user__username=user)
    elif type == "datetime":
        article = models.Article.objects.filter(blog__user__username=user, create_time__year=year,
                                                create_time__month=mouth)

    dict = views.user_blog(request, obj, article, *args, **kwargs)

    return render(request, "blog.html", dict)


def user_article(request, user, articleid, *args, **kwargs):
    try:
        path = request.path_info.strip("/").split("/")
        site = path[0]
        obj = models.Blog.objects.filter(site=site).first()
        if not obj:
            return redirect("/")

        blog = models.Blog.objects.filter(user__username=user).first()

        art = models.Article.objects.filter(blog=blog, nid=articleid).first()

        models.Article.objects.filter(nid=art.nid).update(read_count=F("read_count") + 1)

        article = obj.article_set.all()
        dict = views.user_blog(request, obj, article, *args, **kwargs)

        dict["count"] = art
        return render(request, "blog_count.html", dict)
    except AttributeError as e:
        return redirect("/%s/" % user)
    except Exception as a:
        return redirect("/")


@csrf_exempt
def thumbs(request):
    if request.method == "POST":
        res = {"status": False, "message": None, "count": None}
        username = request.session.get("name")
        uid = request.session.get("id")
        if not username:
            res["message"] = "请登录再点赞！！！"
            return HttpResponse(json.dumps(res))
        type = request.POST.get("type")
        nid = request.POST.get("nid")

        user_id = models.Article.objects.filter(nid=nid).values("blog__user__nid").first().get("blog__user__nid")

        if int(user_id) == int(uid):
            res["message"] = "您不能给自己点！！！"
            return HttpResponse(json.dumps(res))

        count = models.UpDown.objects.filter(user__username=username, article__nid=nid).exists()
        if count:
            if type == "up":
                res["message"] = "您已经赞过了！！！"
            else:
                res["message"] = "您已经踩过了！！！"
            return HttpResponse(json.dumps(res))
        else:
            with transaction.atomic():
                if type == "up":
                    models.UpDown.objects.create(up=1, article_id=nid, user_id=uid)
                    art = models.Article.objects.filter(nid=nid)
                    art.update(up_count=F("up_count") + 1)
                    res["count"] = art.first().up_count
                    res["status"] = "up"

                elif type == "down":
                    models.UpDown.objects.create(up=0, article_id=nid, user_id=uid)
                    art = models.Article.objects.filter(nid=nid)
                    art.update(down_count=F("down_count") + 1)
                    res["count"] = art.first().down_count
                    res["status"] = "down"

                res["message"] = "提交成功！！"
                return HttpResponse(json.dumps(res))

        res["message"] = "操作错误！请稍后再试！！"
        return HttpResponse(json.dumps(res))


def comment(request, *args, **kwargs):
    if request.method == "GET":
        res = {"status": True, "data": None}
        try:
            art_id = kwargs.get("nid")
            art = models.Article.objects.filter(nid=art_id).first()
            msg_list = art.comment_set.values("nid", "content", "reply_id", "user__username")

            def dg(dic):
                msg_dict = {}
                for item in dic:
                    item["child"] = []
                    msg_dict[item["nid"]] = item
                end_list = []
                for row in dic:
                    par = row["reply_id"]
                    if par:
                        msg_dict[par]["child"].append(row)
                    else:
                        end_list.append(row)
                return end_list

            comment_list = dg(msg_list)
            res["data"] = comment_list
        except Exception as e:
            res["status"] = False
            res["message"] = str(e)
        return HttpResponse(json.dumps(res))
    else:
        temp = {'status': True, 'result': None, 'message': None}
        try:
            art_id = request.POST.get('article_id')
            reply_id = request.POST.get("replyId")

            if request.session['id']:
                content = request.POST.get('comment_content').strip()
                reply_obj = re.findall(r"(.+):.*", content)
                reply_contentF = re.findall(r".+:(.*)", content)
                if len(content) == 0:
                    raise ValueError("评论内容不能为空！！！")
                if len(reply_obj) == 1:
                    if len(reply_contentF) == 0 or reply_contentF[0] == "":
                        raise ValueError("评论内容不能为空！！！")
                    reply_name = reply_obj[0].replace("@", "")
                    reply_content = reply_contentF[0].strip()
                    a = models.Comment.objects.filter(nid=reply_id, user__username=reply_name).exists()
                    if a:
                        models.Comment.objects.create(
                            content=reply_content,
                            user_id=request.session['id'],
                            article_id=art_id,
                            reply_id=reply_id,
                        )
                    else:
                        raise ValueError("请单击楼层后面的回复！！")
                else:
                    models.Comment.objects.create(
                        content=content,
                        user_id=request.session['id'],
                        article_id=art_id,
                    )
                models.Article.objects.filter(nid=art_id).update(comment_count=F("comment_count") + 1)
                temp['message'] = '评论成功'
        except ValueError as a:
            temp['status'] = False
            temp['message'] = str(a)
        except Exception as e:
            temp['status'] = False
            temp['message'] = '登录后才可评论'
        return HttpResponse(json.dumps(temp))
