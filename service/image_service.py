from PIL import Image


class ImageService:
    def __init__(self, image_dao, config, s3_client):
        self.image_dao = image_dao
        self.config = config
        self.s3 = s3_client

    def get_image_list_by_id(self, user_no):
        return self.image_dao.get_image_list_by_id(user_no)

    def get_image_list_by_tags(self, tag_list, user_no=None):
        return self.image_dao.get_image_list_by_tags(tag_list, user_no)

    def get_image_detail(self, img_no, user_no):
        return self.image_dao.get_image_dtail(img_no, user_no)

    def get_recommended_image_by_tensor(self, recommended_tags_rating, user_no):
        ## 추천시스템 알고리즘 활용 tag, rating 딕셔너리 값 매개변수에 삽입
        ## 태그와, 이미지에 관한 데이터를 텐서서버에 넘김
        ##  텐서 서버에 user_no와, 태그의 추천도를 넘김
        ##  머신러닝 서버에서  유저의 추천 이미지들을 받음(이미지 번호)
        recommended_image_no_by_tensor
        return self.image_dao.get_image_info(recommended_image_no_by_tensor)

    def get_like_image_by_id(self, user_no):
        return self.image_dao.get_like_image_list_by_id(user_no)

    def get_image_info(self, img_no):  # 텐서 서버에서 받은 이미지에  정보에 추가 정보를 가져옴
        return self.image_dao.get_image_info(img_no)

    def like_or_unlike_by_id_img(self, img_no, user_no):
        return self.image_dao.like_or_unlike_by_id_img(img_no, user_no)

    def insert_like(self, img_no, user_no):
        return self.image_dao.insert_like(img_no, user_no)

    def delete_like(self, img_no, user_no):
        return self.image_dao.delte_like(img_no, user_no)

    def upload_image(self, upload_image, filename, user_no):
        thum_image = Image.open(upload_image)
        thum_image.thumbnail((190, 190))
        thumfilename = "_thum" + filename
        self.s3.upload_fileobj(
            thum_image,
            self.config['S3_BUCKET'],
            thumfilename
        )

        self.s3.upload_fileobj(
            upload_image,
            self.config['S3_BUCKET'],
            filename
        )
        thum_url = f"{self.config['S3_BUCKET_URL']}{thumfilename}"
        img_url = f"{self.config['S3_BUCKET_URL']}{filename}"

        return self.image_dao.upload_image(thum_url, img_url, user_no, filename)

    def delete_image(self, img_no):
        # sql에서 img_no로  파일명을 받아옴,
        self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key='파일명')
        self.s3.delete_object(Bucket=self.config['S3_BUCKET'], Key='thum_' + '파일명')
        # 성공 했을시
        # sql에서 파일 번호 지움
        return self.image_dao.delete_image(img_no)
