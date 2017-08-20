from django.shortcuts import render, HttpResponse, redirect
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction  #事务
from django.db.models import F
from app01.view import views
from django.db.models import Count
from app01 import models
from io import BytesIO
from utils.random_check_code import rd_check_code
from utils import Bform, paging, upload_avatar
import json


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
    article_obj = models.Article.objects.filter(**condition)

    username = request.session.get("name")
    if username == None:
        blog_url = "#"
    else:
        sit = models.Blog.objects.filter(user__username=username).first()
        if sit:
            blog_url = sit.site
        else:
            blog_url="/"
    type_list = models.Article.type_choices

    page = request.GET.get("page")
    if page == None:
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
        return render(request, "login.html", {"obj": obj})
    else:
        obj = Bform.Login(request, request.POST, request.FILES)
        if obj.is_valid():
            cok = redirect("/")
            # cok.set_signed_cookie("id", obj.cleaned_data.get("password"), salt="gao")
            request.session["name"] = obj.cleaned_data.get("username")
            request.session["id"] = obj.cleaned_data.get("password")
            if not request.POST.get("cookie"):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(604800)
            return cok
        return render(request, "login.html", {"obj": obj})


def logout(request):
    request.session.delete(request.session.session_key)
    return redirect("/")


def register(request):
    if request.method == "GET":
        obj = Bform.Register(request)
        return render(request, "register.html", {"obj": obj})
    else:
        obj = Bform.Register(request, request.POST, request.FILES)
        if obj.is_valid():
            newuser = obj.cleaned_data

            img = request.FILES.get("avatar")
            # url = upload_avatar.avatar(img, newuser["username"] + img.name, "static/image/")

            newuser.pop("pwd_again")
            newuser.pop("code")
            # newuser["avatar"] = url
            newuser["nickname"] = newuser["username"]
            # print(newuser)

            models.UserInfo.objects.create(**newuser)
            return redirect("/login/")

        else:
            print(obj.errors)
            return render(request, "register.html", {"obj": obj})


# def avatar(request):
#     if request.method == "POST":
#         print(request.POST)
#         print(request.FILES)
#         img = request.FILES.get("fafafa")
#         url = upload_avatar.avatar(img, img.name, "static/clean/")
#         return HttpResponse(url)


def check_code(request):
    img, code = rd_check_code()
    stream = BytesIO()
    img.save(stream, 'png')
    request.session['code'] = code
    return HttpResponse(stream.getvalue())


def test(request):
    from app02.views import menu
    x=menu(3,request.path_info)
    return render(request,"test.html",x)
    # msg_list = [
    #     {'id': 1, 'content': 'xxx', 'parent_id': None},
    #     {'id': 2, 'content': 'xxx', 'parent_id': None},
    #     {'id': 3, 'content': 'xxx', 'parent_id': None},
    #     {'id': 4, 'content': 'xxx', 'parent_id': 1},
    #     {'id': 5, 'content': 'xxx', 'parent_id': 4},
    #     {'id': 6, 'content': 'xxx', 'parent_id': 2},
    #     {'id': 7, 'content': 'xxx', 'parent_id': 5},
    #     {'id': 8, 'content': 'xxx', 'parent_id': 3},
    #     {'id': 9, 'content': 'xxx', 'parent_id': 7},
    # ]
    # one = []
    # two = []
    # for i in msg_list:
    #     if not i.get("parent_id"):
    #         one.append(i)
    #     else:
    #         two.append(i)
    #
    # def dg(one, two):
    #     a = []
    #     for i in range(len(two)):
    #         two[i]["child"] = []
    #         for j in range(1, len(two)):
    #             if two[i]["id"] == two[j]["parent_id"]:
    #                 two[i]["child"].append(two[j])
    #                 a.append(two[j]["id"])
    #                 print(two[i])
    #                 print(two)
    #                 print("----------------------------------------------------------------")
    #     for i in a:
    #         for j in two:
    #             if j["id"] == i:
    #                 two.remove(j)
    #
    #     for i in one:
    #         i["child"] = []
    #         for j in two:
    #             if i["id"] == j["parent_id"]:
    #                 i["child"].append(j)
    #
    #     return one
    #
    # li = dg(one, two)
    # return HttpResponse(li)

def user_blog(request, *args, **kwargs):
    site=kwargs.get("user")
    obj = models.Blog.objects.filter(site=site).first()
    if not obj:
        return redirect("/")
    request.session["bid"]=obj.nid
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
    user=site

    obj = models.Blog.objects.filter(site=site).first()
    if not obj:
        return redirect("/")

    if type == "tag":
        article = models.Article.objects.filter(blog__user__username=user,tags__nid=tid) #article2tag__tag_id=tid,
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
            if type=="up":
                res["message"] = "您已经赞过了！！！"
            else:
                res["message"]="您已经踩过了！！！"
            return HttpResponse(json.dumps(res))
        else:
            with transaction.atomic():
                if type == "up":
                    models.UpDown.objects.create(up=1, article_id=nid, user_id=uid)
                    art = models.Article.objects.filter(nid=nid)
                    art.update(up_count=F("up_count") + 1)
                    res["count"] = art.first().up_count
                    res["status"]="up"

                elif type == "down":
                    models.UpDown.objects.create(up=0, article_id=nid, user_id=uid)
                    art = models.Article.objects.filter(nid=nid)
                    art.update(down_count=F("down_count") + 1)
                    res["count"] = art.first().down_count
                    res["status"]="down"

                res["message"] = "提交成功！！"
                return HttpResponse(json.dumps(res))

        res["message"]="操作错误！请稍后再试！！"
        return HttpResponse(json.dumps(res))


def comment(request,*args,**kwargs):
    if request.method=="GET":
        res={"status":True,"data":None}
        try:
            art_id=kwargs.get("nid")
            art = models.Article.objects.filter(nid=art_id).first()
            msg_list = art.comment_set.values("nid","content","reply_id","user__username")
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
            res["data"]=comment_list
        except Exception as e:
            res["status"]=False
            res["message"]=str(e)
        return HttpResponse(json.dumps(res))
    else:
        temp = {'status': True, 'result': None, 'message': None}
        try:
            art_id = request.POST.get('article_id')
            if request.session['id']:
                content = request.POST.get('comment_content').strip()
                if len(content) == 0:
                    raise ValueError("评论内容不能为空！！！")
                models.Comment.objects.create(
                    content=content,
                    user_id=request.session['id'],
                    article_id=art_id
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

