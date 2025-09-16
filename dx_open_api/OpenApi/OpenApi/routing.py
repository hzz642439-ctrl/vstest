from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from fzwebsocket import routing as fz_routing



# 第二种设置的方法，需要手动指定可以访问的IP
from channels.security.websocket import OriginValidator


application = ProtocolTypeRouter({
    # 普通的HTTP协议在这里不需要写，框架会自己指明
    'websocket': OriginValidator(
	AuthMiddlewareStack(
    	URLRouter(
        	# 指定去对应应用的routing中去找路由
        	fz_routing.websocket_urlpatterns
    		)
		),
        # 设置可以访问的IP列表
        ['*']
	)
})
