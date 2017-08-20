from django.shortcuts import render,redirect,HttpResponse
from django.db import transaction
from background.view import views
from app01 import models
from background.forms import Article
from utils.paging import Pageinfo
from utils.xss import xss
import json,os
# Create your views here.
def manage(request):
    if request.method=="GET":
        dic=views.manage_base(request)
        if not dic:
            return redirect("/")
        return render(request,"background/manage.html",dic)

def classify(request,type,*args,**kwargs):
    id = request.session.get("id")

    dic=views.manage_base(request,*args,**kwargs)
    if not dic:
        return redirect("/")

    if type=="category":
        obj=models.Category.objects.filter(blog__user__nid=id).all()
    elif type=="tag":
        obj=models.Tag.objects.filter(blog__user__nid=id).all()
    elif type=="article":
        condition = {}
        for k, v in kwargs.items():
            if v=='00':
                condition[k] = None
                continue
            kwargs[k] = int(v)
            if v != '0':
                condition[k] = v

        # 大分类
        type_list = models.Article.type_choices
        # 个人分类
        category_list = models.Category.objects.filter(blog__user__nid=id)
        # 个人标签
        tag_list = models.Tag.objects.filter(blog__user__nid=id)
        # 进行筛选
        condition['blog__user__nid'] = id

        obj = models.Article.objects.filter(**condition)
        dic["type_list"] = type_list
        dic["category_list"]=category_list
        dic["tag_list"]=tag_list
        dic["kwargs"]=kwargs
    else:
        return redirect("/")
    url = "background/"+type + ".html"

    page = request.GET.get("page")
    if page == None:
        page = 1
    count = obj.count()
    p = Pageinfo(page, count, 10, request.path_info)
    finall_obj = obj[p.start():p.stop()]
    pager = p.pager()

    dic["obj"]=finall_obj
    dic["pager"]=pager
    return render(request, url, dic)

def article_add_edit(request,*args,**kwargs):
    uid=request.session.get("id")
    type=kwargs.get("type")
    dic = views.manage_base(request)
    if not dic:
        return redirect("/")
    if request.method=="GET":
        if type=="add":
            art=Article(dic.get("user"))
            post_url="/add.html/"
            operation="添加文章"
        else:
            aid=request.GET.get("nid")
            art_dic=models.Article.objects.filter(nid=aid,blog__user_id=uid).values().first()
            if not art_dic:
                return redirect(request.path_info)
            content=models.ArticleDetail.objects.filter(article__nid=aid).values().first()
            art_dic["content"]=content.get("content")
            art_dic["tag_id"]=[]
            tag_list=models.Article2Tag.objects.filter(article__nid=aid).values()
            for i in tag_list:
                art_dic["tag_id"].append(i["tag_id"])

            art = Article(dic.get("user"),art_dic)

            post_url="/edit.html/?nid=%s"%(art_dic["nid"])
            operation="编辑文章"

        dic["art"]=art
        dic["post_url"]=post_url
        dic["operation"]=operation
        return render(request,"background/art_add.html",dic)
    else:
        obj=Article(dic.get("user"),request.POST,request.FILES)
        if obj.is_valid():
            data=obj.cleaned_data
            old=obj.cleaned_data.get("content")
            content=xss(old)

            data.pop("content")
            tag_list=data.pop("tag_id")
            data["blog_id"]=dic["user"].nid

            if type=="add":
                art_obj=models.Article.objects.create(**data)
                nid=art_obj.nid
                models.ArticleDetail.objects.create(**{"content":content,"article":art_obj})
            else:
                nid=request.GET.get("nid")
                models.Article.objects.filter(nid=nid).update(**data)
                models.ArticleDetail.objects.filter(article__nid=nid).update(content=content)
                models.Article2Tag.objects.filter(article__nid=nid).delete()

            for i in tag_list:
                models.Article2Tag.objects.create(**{"article_id": nid, "tag_id": i})
            return redirect("/manage/article/0-0-0.html")
        else:
            dic["art"] = obj
            return render(request,"background/art_add.html",dic)

def upload(request):
    if request.method=="POST":
        """
        图片上传
        :param request:
        :return:
        """
        imag=request.FILES.get("imgFile")
        path=os.path.join("static/upload/",imag.name)

        with open(path,"wb") as f:
            for i in imag.chunks():
                f.write(i)

        dic = {
            'error': 0,
            'url': '/'+path,
            'message': '错误了...'
        }
        return HttpResponse(json.dumps(dic))

def article_del(request):
    if request.method=="GET":
        res={"status":True,"msg":None}
        try:
            with transaction.atomic():
                nid=request.GET.get("nid")
                uid=request.session.get("id")
                models.ArticleDetail.objects.filter(article__nid=nid,article__blog__user_id=uid).delete()
                models.Article2Tag.objects.filter(article__nid=nid,article__blog__user_id=uid).delete()
                models.Article.objects.filter(nid=nid,blog__user_id=uid).delete()
                res["msg"]="删除成功！"
        except Exception as e:
            res["status"]=False
            res["msg"]=str(e)

        return HttpResponse(json.dumps(res))

def category_add_edit(request,*args,**kwargs):
    type=kwargs.get("type")
    bid = request.session.get("bid")
    if request.method=="GET":
        dic=views.manage_base(request)
        nid=request.GET.get("nid")
        dic["nid"]=nid
        if nid:
            obj=models.Category.objects.filter(nid=nid,blog_id=bid).first()
            dic["old"]=obj.title
            return render(request,'background/cat_edit.html',dic)
        else:
            return redirect('/manage/category/')
    else:
        res={"status":True,"msg":None,'url':None}
        new_category=request.POST.get("new_category").strip()
        if len(new_category)>0:
            if type=="add":
                obj=models.Category.objects.filter(title=new_category,blog_id=request.session["bid"]).first()
                if not obj:
                    models.Category.objects.create(title=new_category,blog_id=request.session["bid"])
                    res["msg"]="添加成功！！！"
                    return HttpResponse(json.dumps(res))
                else:
                    res["status"]=False
                    res["msg"]="该分类已存在！！！"
                    return HttpResponse(json.dumps(res))
            elif type=="edit":
                nid=request.GET.get("nid")
                obj=models.Category.objects.filter(nid=nid,blog_id=bid)
                if obj.first():
                    obj.update(title=new_category)
                    res["msg"]="修改成功！！！"
                    res["url"]="/manage/category/"
                else:
                    res["status"]=False
                    res["msg"]="该分类不存在！！！"
                return HttpResponse(json.dumps(res))
        else:
            res["status"]=False
            res["msg"]="不能为空！请输入正确的值！！！"
            return HttpResponse(json.dumps(res))

def category_del(request):
    if request.method=="GET":
        res = {"status": True, "msg": None}
        try:
            with transaction.atomic():
                nid = request.GET.get("nid")
                bid = request.session.get("bid")
                models.Article.objects.filter(category_id=nid,blog_id=bid).update(category_id=None)
                models.Category.objects.filter(nid=nid,blog_id=bid).delete()
                res["msg"] = "删除成功！"
        except Exception as e:
            res["status"] = False
            res["msg"] = str(e)

        return HttpResponse(json.dumps(res))


def tag_add_edit(request,*args,**kwargs):
    type = kwargs.get("type")
    bid = request.session.get("bid")
    if request.method == "GET":
        dic = views.manage_base(request)
        nid = request.GET.get("nid")
        dic["nid"] = nid
        if nid:
            obj = models.Tag.objects.filter(nid=nid, blog_id=bid).first()
            dic["old"] = obj.title
            return render(request, 'background/tag_edit.html', dic)
        else:
            return redirect('/manage/tag/')
    else:
        new_tag=request.POST.get("new_tag").strip()
        res = {"status": True, "msg": None, 'url': None}
        if len(new_tag) > 0:
            if type=="add":
                obj=models.Tag.objects.filter(title=new_tag,blog_id=request.session["bid"]).first()
                if not obj:
                    models.Tag.objects.create(title=new_tag,blog_id=request.session["bid"])
                    res["msg"]="添加成功！！！"
                    return HttpResponse(json.dumps(res))
                else:
                    res["status"]=False
                    res["msg"]="该标签已存在，请重新输入！！！"
                    return HttpResponse(json.dumps(res))
            elif type=="edit":
                nid=request.GET.get("nid")
                obj=models.Tag.objects.filter(nid=nid,blog_id=bid)
                if obj.first():
                    obj.update(title=new_tag)
                    res["msg"]="修改成功！！！"
                    res["url"]="/manage/tag/"
                else:
                    res["status"]=False
                    res["msg"]="该标签不存在！！！"
                return HttpResponse(json.dumps(res))
        else:
            res["status"]=False
            res["msg"]="不能为空！请输入正确的值！！！"
            return HttpResponse(json.dumps(res))

def tag_del(request):
    if request.method=="GET":
        res = {"status": True, "msg": None}
        try:
            with transaction.atomic():
                nid = request.GET.get("nid")
                bid = request.session.get("bid")
                models.Article2Tag.objects.filter(tag_id=nid,article__blog_id=bid).delete()
                models.Tag.objects.filter(nid=nid,blog_id=bid).delete()
                res["msg"] = "删除成功！"
        except Exception as e:
            res["status"] = False
            res["msg"] = str(e)

        return HttpResponse(json.dumps(res))