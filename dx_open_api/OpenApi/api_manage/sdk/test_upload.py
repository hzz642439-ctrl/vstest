from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from pathlib import Path
import sys
# 假设 upload_minio 已经在 utils.py 里写好了
from api_manage.sdk.minio_upload import minio_upload

# 用本地文件模拟 Django 的 UploadedFile
file_path = r"D:\python\img\test.jpg"   # 换成你本地的图片
with open(file_path, "rb") as f:
    file_data = f.read()

file_obj = InMemoryUploadedFile(
    file=BytesIO(file_data),
    field_name=None,
    name=Path(file_path).name,
    content_type="image/jpeg",
    size=len(file_data),
    charset=None
)

# 调用上传方法
url = minio_upload(file_obj, "images")
print("上传成功，访问URL:", url)