from PIL import Image
import requests, json
import io
from datetime import datetime
import math


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

    def insert_rec_tag_importance(self, img_no, importance_data):
        total_data = {}
        total_data["img_no"] = img_no
        total_data["importances"] = importance_data
        print(total_data)

        return self.image_dao.insert_rec_tag_importance(total_data)

    def insert_image(self, upload_image_info):
        URL = 'http://409e5a8b0796.ngrok.io/recognized_tag'
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
        def tag_area(x_1, x_2, y_1, y_2):
            return abs((x_2 - x_1) * (y_2 - y_1))
        def tag_location(x_1, x_2, y_1, y_2):
            location_score = math.sqrt((0.5 - ((x_1 + x_2) / 2))**2 + (0.5 - ((y_1 + y_2) / 2))**2)*100
            if location_score == 0:
                location_score += 0.1
            return 1/location_score

        rec_tags_info = rec_tags_info['reg_tags']
        tag_nos = [tag_info['tag_no'] for tag_info in rec_tags_info]
        tag_no_set = set(tag_nos)
        tag_num_dict = {}
        for tag_no in tag_no_set:
            num = tag_nos.count(tag_no)
            tag_num_dict[tag_no] = num
        print(tag_num_dict)
        # {48: 5, 50: 5, 47: 3}
        dupli_tags_process = {}

        for tag_no, num in tag_num_dict.items():
            dupli_tags_process[tag_no] = [0, num]
        for tag_no, num in tag_num_dict.items():
            for tag_info in rec_tags_info:
                if tag_info['tag_no'] == tag_no:
                    x_1 = tag_info['x_1']
                    x_2 = tag_info['x_2']
                    y_1 = tag_info['y_1']
                    y_2 = tag_info['y_2']
                    dupli_tags_process[tag_no][0] += 0.88*tag_area(x_1,x_2,y_1,y_2)
                    dupli_tags_process[tag_no][0] += 0.12*tag_location(x_1,x_2,y_1,y_2)/num
        print(dupli_tags_process)
        return dupli_tags_process
    # {"tag_no":[score, num]}

    def get_importance_percentage(self, score_data):
        # {img_no: 이미지번호,  importances : [{ tag_no : 태그 번호, importance : 중요도, num : 갯수}]
        # tag_no: [score, num]
        #  최종 결과값
        #  score들의 합을 구하자
        ## tag별 score값들의 리스트 구하기
        score_list = [info[0] for info in list(score_data.values())]
        score_sum = sum(score_list)
        importances = []
        for tag_no, score_info in score_data.items():
            each_tag_info = {}
            each_tag_info["tag_no"] = tag_no
            each_tag_info["importance"] = score_info[0]/score_sum
            each_tag_info["num"] = score_info[1]
            importances.append(each_tag_info)

        print(importances)
        return importances

    def get_image_tags_rec_info(self, img_no):
        return self.test_dao.get_image_data(img_no, ['person', 'dining table', 'chair'])

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

        str_user_no = str(user_no)
        self.s3.upload_fileobj(
            in_mem_file,
            self.config['S3_BUCKET'],
            "beet/"+str_user_no+"/"+filename,
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
            "beet/"+str_user_no+"/"+thumfilename,
            ExtraArgs={
                "ContentType": 'image/jpeg'
            }
        )

        thum_url = f"{self.config['S3_BUCKET_URL']}/beet/{str_user_no}/{thumfilename}"
        img_url = f"{self.config['S3_BUCKET_URL']}/beet/{str_user_no}/{filename}"


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

    def get_img_no(self):
        return self.test_dao.get_img_no_by_all()
