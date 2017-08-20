from app01 import models


def manage_base(request,*args,**kwargs):
    id = request.session.get("id")
    username = request.session.get("name")
    user = models.Blog.objects.filter(user__nid=id).first()
    if not id or not username or not user:
        return None

    base_dict = {"user": user}

    return base_dict
