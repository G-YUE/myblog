from django.db.models import Count
from app01 import models
from utils import paging
import pytz


# def user_blog_data(request):
#     path = request.path_info.strip("/").split("/")
#     user = path[0]
#     site = "/" + user
#     obj = models.Blog.objects.filter(site=site).first()
#     if not obj:
#         return False
#     article = obj.article_set.all()
#     return (obj, article)

def myhome(request,obj):
    site=obj.site
    user = request.session.get("name")
    if user:
        us = models.Blog.objects.filter(user__username=user).first()
        if us:
            usite=us.site
        else:
            usite=""

    else:
        return None
    if site!=usite:
        return usite
    else:
        return None
def user_blog(request, obj, article, *args, **kwargs):
    page = request.GET.get("page")
    if page == None:
        page = 1
    count = obj.article_set.count()
    url = request.path_info
    p = paging.Pageinfo(page, count, 10, url)
    article = article[p.start():p.stop()]
    pager = p.pager()

    # 关注和粉丝
    attention = models.UserFans.objects.filter(follower=obj.user_id).count()
    follower = models.UserFans.objects.filter(user=obj.user_id).count()

    # 个人分类归档
    # category=models.Category.objects.filter(blog=obj).values("nid","title").annotate(count=Count("article__nid"))
    category = models.Article.objects.filter(blog=obj).values("category_id", "category__title").annotate(
        count=Count("nid"))

    # 时间归档
    # time_list = obj.article_set.all().datetimes('create_time', 'month', order='DESC', tzinfo=pytz.UTC)

    #time_list = obj.article_set.extra(select={"c": "date_format(create_time,'%%Y-%%m')"}).values("c").annotate(
        #count=Count("nid"))
    time_list = obj.article_set.extra(select={"c": "strftime('%%Y-%%m',create_time)"}).values("c").annotate(count=Count("nid"))
    # 个人标签归档
    # tag = models.Tag.objects.filter(blog=obj).values("nid", "title").annotate(count=Count("article__nid"))
    tag=models.Article2Tag.objects.filter(tag__blog=obj).values("tag__nid", "tag__title").annotate(count=Count("article__nid"))
    
    myho=myhome(request,obj)

    return {"user": obj,
            "article": article,
            "pager": pager,
            "attention": attention,
            "follower": follower,
            "tag": tag,
            "category": category,
            "dates": time_list,
            "usersite":myho,
            }
