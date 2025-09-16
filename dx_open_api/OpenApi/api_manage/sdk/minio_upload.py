import uuid
from minio import Minio

MINIO_ENDPOINT = "192.168.1.203:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_ACCESS_SECRET = "minioadmin"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_ACCESS_SECRET,
    secure=False
)

def minio_upload(file, bucket):
    try:
        # 确保 bucket 存在
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)

        # 生成唯一的随机文件名
        ext = file.name.split(".")[-1]
        file_name = f"{uuid.uuid4().hex}.{ext}"

        # 上传文件
        minio_client.put_object(
            bucket,
            file_name,
            file.file,
            length=file.size,
            content_type=file.content_type
        )

        # 拼接访问 URL用https拼接
        file_url = f"https://minio.s.qubit-dance.com/{bucket}/{file_name}"

        return file_url

    except Exception as e:
        raise Exception(f"MinIO 上传失败：{e}")

