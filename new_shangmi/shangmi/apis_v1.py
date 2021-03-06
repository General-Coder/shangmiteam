import json

import requests
from django.conf import settings
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from .utils import *
from .models import *
from django.core.cache import caches
from .getqr import *
import uuid
user_cache = caches['user']
class LoginAPI(View):

    def post(self, request):

        params = request.POST
        code = params.get('code')
        avatar = params.get('avatar')
        # gender = params.get('gender')
        nick_name = params.get('name')
        mini_type = params.get('mini_type')
        token = params.get("token")
        user_id = user_cache.get(token)
        if user_id:
            user_cache.set(token, user_id, settings.LOGIN_TIMEOUT)
            return JsonResponse({'code': 0, 'data': {'token': token, "uid": user_id}})
        if mini_type == 'background':
            appid = 'wx4a8c99d5d8b43556'
            secret = '014ad578b31357e53b61b9ab69db0761'
        elif mini_type == 'customer':
            appid = 'wx8b50ab8fa813a49e'
            secret = 'b32f63c36ea123710173c4c9d4b15e8b'
        else:
            appid = 'wxebd828458f8b2b38'
            secret = 'a40cb9c5ecb1f4f5c0f31b75829fed03'
        url = settings.SMALL_WEIXIN_OPENID_URL
        params = {"appid": appid,
                  "secret": secret,
                  "js_code": code,
                  "grant_type": 'authorization_code'
                  }
        response = requests.get(url, params=params)

        data = json.loads(response.content.decode())
        if 'openid' in data:
            openid = data.get('openid')
            user = ShangmiUser.objects.get_or_create(openid=openid)[0]
            # token = generate_validate_token(str(user.id))
            token = uuid.uuid4().hex
            user_cache.set(token, user.id, settings.LOGIN_TIMEOUT)
            user.nick_name = nick_name
            user.icon = avatar
            user.source = mini_type
            user.save()
            return HttpResponse(json.dumps({'code': 0, 'data': {'token': token, "uid": user.id}}),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({'code': 1, 'msg': 'failed'}),
                                content_type='application/json')

class ActivesAPI(View):

    def get(self, req):

        actives = Active.objects.filter(
            is_active=True
        )
        fast = actives.filter(is_fast=True)
        unfast = actives.filter(is_fast=False)
        # fast_data = [model_to_dict(i) for i in fast]
        unfast_data = [model_to_dict(i) for i in unfast]
        fast_data = []
        for i in fast:
            tmp = model_to_dict(i)
            if i.need_num == 0:
                tmp["percent"] = "0%"
            else:
                tmp["percent"] = str((i.complete_num / i.need_num) * 100) + "%"
            fast_data.append(tmp)
        unfast_data = []
        for i in unfast:
            tmp = model_to_dict(i)
            if i.need_num == 0:
                tmp["percent"] = "0%"
            else:
                tmp["percent"] = str((i.complete_num / i.need_num) * 100) + "%"
            unfast_data.append(tmp)
        result = {
            "code": 1,
            "msg": "ok",
            "data": {
                "fast": fast_data,
                "unfast": unfast_data
            }
        }
        return JsonResponse(result)


class AdvAPI(View):

    def get(self,req):
        advs = Advertise.objects.filter(
            is_used=True
        )
        res = [model_to_dict(i) for i in advs]
        data = {
            "code":1,
            "msg": "ok",
            "data": res
        }
        return JsonResponse(data)

class IndexAPI(View):
    # @login_req
    def get(self, req):
        user = ShangmiUser.objects.get(pk=int(user_cache.get(req.GET.get("token"))))
        actives = UserActiveLog.objects.filter(user=user)
        # 未通过的
        doing_count = actives.filter(status=0).count()
        # 审核通过的
        finish_count = actives.filter(status=1).count()
        # 用户余额

        try:
            money = Balance.objects.get(user=user).money
        except:
            money = 0
        data = {
            "code": 0,
            "data": {
                'money': money,
                'doing_count': doing_count,
                'finish_count': finish_count
            }
        }
        return JsonResponse(data)


# 用户参加活动明细
class UserActiveLogAPI(View):

    def get(self, req):
        user = ShangmiUser.objects.get(
            pk=int(user_cache.get(
                req.GET.get("token")
                )
            )
        )
        logs = UserActiveLog.objects.filter(
            user=user,
            status=1
        ).order_by("-create_time")
        data_logs = []

        for i in logs:
            tmp = model_to_dict(i)

            tmp['create_time'] = i.create_time.strftime("%Y年%m月%d日 %H:%M")
            tmp["status"] = i.get_status_display()
            tmp["active_msg"] = model_to_dict(i.active)
            tmp["type"] = i.get_type_display()
            data_logs.append(tmp)

        return JsonResponse({"code": 0, "data": data_logs})


# 付款明细
class UserPayLogAPI(View):

    def get(self, req):
        user = ShangmiUser.objects.get(
            pk=int(user_cache.get(
                req.GET.get("token")
            )
            )
        )
        logs = UserPayLog.objects.filter(user=user, status=1).order_by("-create_time")
        datas = []
        for i in logs:
            tmp = model_to_dict(i)
            tmp['create_time'] = i.create_time.strftime("%Y年%m月%d日 %H:%M:%S")
            tmp["store_name"] = i.store.name
            tmp["money"] = i.money / 100
            tmp["integral"] = i.integral / 100
            datas.append(tmp)

        data = {
            "code": 0,
            "data": datas
        }
        return JsonResponse(data)


# 任务明细
class TaskDetailAPI(View):

    def get(self, req):
        user = ShangmiUser.objects.get(
            pk=int(user_cache.get(
                req.GET.get("token")
            )
            )
        )
        datas = UserActiveLog.objects.filter(user=user).order_by("-create_time")
        details = []
        for i in datas:
            tmp = model_to_dict(i)
            tmp['create_time'] = i.create_time.strftime("%Y年%m月%d日 %H:%M")
            tmp["status"] = i.get_status_display()
            tmp["active_msg"] = model_to_dict(i.active)
            tmp["type"] = i.get_type_display()
            details.append(tmp)

        data = {
            "code": 0,
            "data": details
        }
        return JsonResponse(data)

class ActiveAPI(View):

    def get(self, req):
        id = int(req.GET.get("id"))
        active = Active.objects.get(pk=id)
        data = {
            "code": 0,
            "data": model_to_dict(active)
        }
        return JsonResponse(data)

class ShareGetMoneyAPI(View):

    def post(self, req):
        token = req.POST.get("token")
        share_uid = req.POST.get("uid")
        user = user_cache.get()


class JoinActiveAPI(View):

    def post(self, req):

        user = ShangmiUser.objects.get(pk=int(user_cache.get(
                req.POST.get("token")
            )))
        uid = req.POST.get("uid")
        id = req.POST.get("id")
        active = Active.objects.get(id=id)
        if active.is_active == False:
            data = {
                "code": 3,
                "data": "活动已结束"
            }
            return JsonResponse(data)
        # 先判断该用户是不是已经参与了
        if UserActiveLog.objects.filter(user_id=user.id).exists():
            data = {
                "code": 2,
                "data": "您已参加，想赚更多可分享"
            }
            return JsonResponse(data)
        log = UserActiveLog.objects.create(
            active_id=id,
            user_id=user.id,
            integral=active.give_money,
            type="join",
            status=1
        )
        active.complete_num += 1
        active.save()
        # 更新用户余额表
        user_balance = Balance.objects.get_or_create(user_id=user.id)[0]
        user_balance.money += active.give_money
        user_balance.save()
        if int(uid) != -1 and int(uid) != user.id:
            UserActiveLog.objects.create(
                active_id=id,
                user_id=uid,
                integral=active.share_give_money,
                type="share",
                status=1
            )
            # 更新分享人用户积分余额
            share_user_balance = Balance.objects.get(user_id=uid)
            share_user_balance.money += active.share_give_money
            share_user_balance.save()
        data = {
            "code": 0,
            "data": "参与成功，积分已发放到个人中心"
        }
        return JsonResponse(data)


class QrcodeAPI(View):
    def get(self, request):
        params = request.GET
        active_id = int(params.get('active_id'))

        wx_mini_path = 'pages/join/join?uid=-1&aid=%s' % active_id
        image_data = get_qrcode(wx_mini_path)
        return HttpResponse(image_data,content_type="image/png")


class StoreAPI(View):

    def get(self, req):
        user = ShangmiUser.objects.get(
            pk=int(user_cache.get(
                req.GET.get("token")
            )
            )
        )
        balance = Balance.objects.get(user_id=user.id)
        store_id = int(req.GET.get("sid"))
        store = Store.objects.get(id=store_id)
        if store.is_active == False:
            data = {
                "code": 2,
                "data": "该店暂不参与"
            }
            return JsonResponse(data)
        else:
            store_dict = model_to_dict(store)
            store_dict["boss_name"] = store.boss.nick_name
            store_dict["boss_icon"] = store.boss.icon
            store_dict["user_balance"] = balance.money / 100
            return JsonResponse({"code": 0, "data": store_dict})