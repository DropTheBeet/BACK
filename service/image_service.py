
class ImageService:
    def __init__(self, image_dao):
        self.image_dao = image_dao

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

    def get_image_info(self, img_no):   #텐서 서버에서 받은 이미지에  정보에 추가 정보를 가져옴
        return self.image_dao.get_image_info(img_no)

    def like_or_unlike_by_id_img(self, img_no, user_no):
        return self.image_dao.like_or_unlike_by_id_img(img_no, user_no)

    def insert_like(self, img_no, user_no):
        return self.image_dao.insert_like(img_no, user_no)

    def delete_like(self, img_no, user_no):
        return self.image_dao.delte_like(img_no, user_no)

    def upload_image(self, upload_image, filename, user_no):
        ### 이미지 썸네일 처리하는 프로세스 추가하여야함
        thum_img = upload_image
        thumfilename = filename+"_thum"
        self.s3.upload_fileobj(
            thum_img,
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
        ## s3에서 thum_img, upload_img 제거하는 프로세스 구현
        return self.image_dao.delete_image(img_no)






