from PIL import Image
import requests, json
import io
from datetime import datetime



class ImageService:
    def __init__(self, image_dao, config, s3_client):
        self.image_dao = image_dao
        self.config = config
        self.s3 = s3_client

    def get_image_list_by_user(self, user_no):
        return self.image_dao.get_image_list_by_user(user_no)

    def get_image_list_by_tags(self, tag_list, user_no=None):
        return self.image_dao.get_image_list_by_tags(tag_list, user_no)

    def get_image_detail(self, img_no, user_no):
        return self.image_dao.get_image_detail(img_no, user_no)





    def insert_image(self, upload_image_info):
        URL = 'http://e4933cdbab5e.ngrok.io/recognized_tag'
        headers = {
            'Content-Type': 'application/json;'
        }
        data = {
            'img_url': upload_image_info['img_url']}
        res = requests.post(URL, data=json.dumps(data), headers=headers)
        res.raise_for_status()
        tags_info = json.loads(res.text)
        upload_image_info['tag_data'] = []

        for tag in tags_info['tag']:
            tag_info = {}
            tag_info['tag_no'] = list(tag.keys())[0]
            tag_values = list(tag.values())
            print(tag_values)
            tag_info['point_x'] = tag_values[0][0]
            tag_info['point_y'] = tag_values[0][1]
            tag_info['width'] = tag_values[0][2]
            tag_info['height'] = tag_values[0][3]
            upload_image_info['tag_data'].append(tag_info)

        print(upload_image_info['tag_data'])
        return self.image_dao.insert_image(upload_image_info)

    def get_recommend_image_list_by_user(self, user_no):
        return self.image_dao.get_recommend_image_list_by_user(user_no)

    def get_like_image_by_user(self, user_no):
        return self.image_dao.get_like_image_list_by_user(user_no)

    def get_image_info(self, img_no):  # 텐서 서버에서 받은 이미지에  정보에 추가 정보를 가져옴
        return self.image_dao.get_image_info(img_no)

    def like_or_unlike_by_user_img(self, img_no, user_no):
        return self.image_dao.like_or_unlike_by_user_img(img_no, user_no)

    def insert_like(self, img_no, user_no):
        return self.image_dao.insert_like(img_no, user_no)

    def delete_like(self, img_no, user_no):
        return self.image_dao.delete_like(img_no, user_no)

    def upload_image(self, upload_image, filename, user_no):
        filename = str(datetime.utcnow()) + filename
        thumfilename = "thum_" + filename
        # #셈네일 만들기
        original_image = Image.open(upload_image)
        # #이미지 사이즈 측정
        img_size = original_image.size
        in_mem_file = io.BytesIO()
        original_image.save(in_mem_file, format=original_image.format)
        in_mem_file.seek(0)
        self.s3.upload_fileobj(
            in_mem_file,
            self.config['S3_BUCKET'],
            filename,
            ExtraArgs={
            "ContentType": 'image/jpeg'
            }
        )

        thum_image = Image.open(upload_image)
        thum_image.thumbnail((190, 190))
        thum_in_mem_file = io.BytesIO()
        thum_image.save(thum_in_mem_file, format=thum_image.format)
        thum_in_mem_file.seek(0)
        self.s3.upload_fileobj(
            thum_in_mem_file,
            self.config['S3_BUCKET'],
            thumfilename,
            ExtraArgs={
                "ContentType": 'image/jpeg'
            }
        )

        thum_url = f"{self.config['S3_BUCKET_URL']}{thumfilename}"
        img_url = f"{self.config['S3_BUCKET_URL']}{filename}"


        img = {'filename':filename, 'img_url':img_url, 'thum_url':thum_url, 'user_no':user_no, 'img_w':img_size[0], 'img_h':img_size[1]}

        return img



    def delete_image(self, img_no):
        # sql에서 img_no로  파일명을 받아옴,
        self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key='파일명')
        self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key='thum_' + '파일명')

        # 성공 했을시
        # sql에서 파일 번호 지움
        return self.image_dao.delete_image(img_no)
