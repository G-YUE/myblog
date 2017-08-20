import os

def avatar(img_obj, img_name, img_url):
    url = os.path.join(img_url, img_name)
    f = open(url, "wb")
    for i in img_obj.chunks():
        f.write(i)
    f.close()
    return "/%s" % url
