from PIL import Image
import requests, json
import io
from datetime import datetime
import math
import pandas as pd


class ImageService:
    def __init__(self, image_dao, config, s3_client, test_dao):
        self.image_dao = image_dao
        self.config = config
        self.s3 = s3_client
        self.test_dao = test_dao

    def get_image_list_by_user(self, user_no):
        return self.image_dao.get_image_list_by_user(user_no)

    def get_image_list_by_tags(self, tag_list, user_no=None):
        return self.image_dao.get_image_list_by_tags(tag_list, user_no)

    def get_image_detail(self, img_no, user_no):
        return self.image_dao.get_image_detail(img_no, user_no)

    def insert_image(self, upload_image_info):
        URL = 'http://39228f543fce.ngrok.io/recognized_tag'
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
            tag_info['tag_no'] = int(list((tag.keys()))[0]) + 1
            tag_values = list(tag.values())
            tag_info['x_1'] = tag_values[0][0]
            tag_info['y_1'] = tag_values[0][1]
            tag_info['x_2'] = tag_values[0][2]
            tag_info['y_2'] = tag_values[0][3]
            upload_image_info['tag_data'].append(tag_info)

        print(upload_image_info['tag_data'])
        return self.image_dao.insert_image(upload_image_info)

    def get_recommend_image_list_by_user(self, user_no):
        return self.image_dao.get_recommend_image_list_by_user(user_no)


    def get_tag_importance_test(self, rec_tags_info):
        def tag_area(x_1, x_2, y_1, y_2, num):
            if num == 1:
                return abs((x_2 - x_1) * (y_2 - y_1))
            if num == 2:
                return math.sqrt(abs((x_2 - x_1) * (y_2 - y_1)))
            if num == 3:
                return math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)

        def tag_location(x_1, x_2, y_1, y_2):
            return 1/(math.sqrt((0.5 - ((x_1 + x_2) / 2)) ** 2 + (0.5 - ((y_1 + y_2) / 2)) ** 2)*100)
        tag_nos = [ tag_info['tag_no'] for tag_info in rec_tags_info]
        print(tag_nos)
        tag_no_set = set(tag_nos)
        print(tag_no_set)
        tag_num_dict = {}
        for tag_no in tag_no_set:
            num = tag_nos.count(tag_no)
            tag_num_dict[tag_no] = num
        print(tag_num_dict)
        # {48: 5, 50: 5, 47: 3}
        dupli_tags_process = {}

        for tag_no, num in tag_num_dict.items():
            dupli_tags_process[tag_no] = [0, 0, 0, 0, 0, 0, "no_name"]
        for tag_no, num in tag_num_dict.items():
            for tag_info in rec_tags_info:
                if tag_info['tag_no'] == tag_no:
                    x_1 = tag_info['x_1']
                    x_2 = tag_info['x_2']
                    y_1 = tag_info['y_1']
                    y_2 = tag_info['y_2']
                    dupli_tags_process[tag_no][0] += 0.88*tag_area(x_1,x_2,y_1,y_2,1)
                    dupli_tags_process[tag_no][0] += 0.12*tag_location(x_1,x_2,y_1,y_2)/num
                    dupli_tags_process[tag_no][1] += 0.88*tag_area(x_1,x_2,y_1,y_2,2)
                    dupli_tags_process[tag_no][1] += 0.12*tag_location(x_1,x_2,y_1,y_2)/num
                    dupli_tags_process[tag_no][2] += 0.88*tag_area(x_1, x_2, y_1, y_2, 3)
                    dupli_tags_process[tag_no][2] += 0.12*tag_location(x_1,x_2,y_1,y_2)/num
                    dupli_tags_process[tag_no][3] += tag_area(x_1,x_2,y_1,y_2,1)
                    dupli_tags_process[tag_no][4] += tag_area(x_1,x_2,y_1,y_2,2)
                    dupli_tags_process[tag_no][5] += tag_area(x_1, x_2, y_1, y_2, 3)
                    dupli_tags_process[tag_no][6] = tag_info['tag']
        return dupli_tags_process

    def get_importance_percentage(self, tags_importance):
        # tags_importance.values():[1,2,3,4,5,6,name]
        # 바나나 [1,2,3,4,5,6,name], 오렌지 [1,2,3,4,5,6,name]
        # 최종 결과값, stratege1,  바나나:34%, 오렌지 :34% ...
        k = tags_importance.values()
        df = pd.DataFrame(k)
        df = df.transpose()
        dt2 = df.rename(columns=df.iloc[6])
        dt3 = dt2.drop(dt2.index[6])
        dt3['sum'] = dt3.sum(axis=1)
        columns = list(dt3.columns)

        dt4 = pd.DataFrame()
        for column in columns:
            dt4[column] = dt3[column]/dt3['sum']

        print(dt4)

        return

    def get_image_tags_rec_info(self, img_no):
        return self.test_dao.get_image_data(img_no)

    def get_like_image_by_user(self, user_no):
        return self.image_dao.get_like_image_list_by_user(user_no)

    def like_or_unlike_by_user_img(self, img_no, user_no):
        return self.image_dao.like_or_unlike_by_user_img(img_no, user_no)

    def insert_like(self, img_no, user_no):
        return self.image_dao.insert_like(user_no, img_no)

    def delete_like(self, img_no, user_no):
        return self.image_dao.delete_like(user_no, img_no)

    def insert_click_data(self, user_no, img_no, type):
        return self.image_dao.insert_click_data(user_no, img_no, type)

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
        filename = self.image_dao.delete_image(img_no)
        try:
            self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key=filename)
            self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key='thum_' + filename)
            return filename
        except Exception as e:
            # Error 발생할 경우
            print(f"s3 안 파일 {filename} 삭제 실패 ")
            print(e)
            return filename
