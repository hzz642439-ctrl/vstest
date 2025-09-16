from __future__ import unicode_literals
from rest_framework import serializers, viewsets
from api_manage import models



class ApiUrlSerializers(serializers.ModelSerializer):
    """用户序列化"""
    # pg_accredits = MemberAccreditSerializers(many=True, read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = models.ApiUrl
        fields = '__all__'

class ApiGroupSerializers(serializers.ModelSerializer):
    """用户序列化"""
    api_url = ApiUrlSerializers(many=True, read_only=True)
    # pg_accredits = MemberAccreditSerializers(many=True, read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)


    class Meta:
        model = models.ApiGroup
        fields = '__all__'



class UrlVersionsSerializers(serializers.ModelSerializer):
    """用户序列化"""
    api_group = ApiGroupSerializers(many=True, read_only=True)
    no_group_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    def get_no_group_url(self, obj):
        url_obj = models.ApiUrl.objects.filter(versions_id=obj.id, group__isnull=True)
        return ApiUrlSerializers(url_obj, many=True, context=self.context).data


    class Meta:
        model = models.UrlVersions
        fields = '__all__'


class ApiDataSerializers(serializers.ModelSerializer):
    """用户序列化"""
    url_versions = UrlVersionsSerializers(many=True, read_only=True)
    collect =serializers.SerializerMethodField()
    # api_group = ApiGroupSerializers(many=True, read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    def get_collect(self,obj):
        request=self.context.get('request')
        if not request:
            return False
        gid = getattr(request,'gid',None)
        uid = getattr(request,'uid',None)
        return obj.api_collect.filter(gid=gid,uid=uid).exists()

    class Meta:
        model = models.ApiData
        fields = '__all__'



class ApiDataAllSerializers(serializers.ModelSerializer):
        """用户序列化"""
        collect = serializers.SerializerMethodField()
        subscribe = serializers.SerializerMethodField()
        created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
        updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

        def get_collect(self, obj):
            request=self.context.get('request')
            if not request:
                return False
            gid = getattr(request,'gid',None)
            uid = getattr(request,'uid',None)
            return obj.api_collect.filter(gid=gid,uid=uid).exists()
        def get_subscribe(self, obj):
            """判断 api_group 外键是否存在"""
            return obj.subscribe_api.exists()
        class Meta:
            model = models.ApiData
            fields = '__all__'




class SubscribeSerializers(serializers.ModelSerializer):
    """用户序列化"""
    api_data = ApiDataAllSerializers()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    expiration_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = models.SubscribeApi
        fields = '__all__'

class Api_CategorySerializers(serializers.ModelSerializer):
    data = serializers.JSONField()