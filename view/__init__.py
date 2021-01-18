import jwt

from flask import request, jsonify, current_app, Response, g, send_file
from flask.json import JSONEncoder
from functools import wraps
from werkzeug.utils import secure_filename


## Default JSON encoder는 set를 JSON으로 변환할 수 없다.
## 그럼으로 커스텀 엔코더를 작성해서 set을 list로 변환하여
## JSON으로 변환 가능하게 해주어야 한다.
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)


#########################################################
#       Decorators
#########################################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None

            if payload is None: return Response(status=401)

            user_no = payload['user_no']
            user_id = payload['user_id']
            g.user_no = user_no
            g.user_id = user_id
        else:
            return Response(status=401)

        return f(*args, **kwargs)

    return decorated_function


def create_endpoints(app, services):
    app.json_encoder = CustomJSONEncoder

    user_service = services.user_service
    tag_service = services.tag_service
    image_service = services.image_service
    model_service = services.model_service

    @app.route("/ping", methods=['GET'])
    def pin():

        return "pongg"


## id, 비밀번호 만 들어옴
    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json # user_id, user_pw
        new_user = user_service.create_new_user(new_user)

        return jsonify(new_user)

    @app.route('/login', methods=['POST'])
    def login():
        credential = request.json #user_id, user_pw
        authorized = user_service.login(credential)

        if authorized:
            user_credential = user_service.get_user_no_and_password(credential['user_id'])
            user_no = user_credential['user_no']
            token = user_service.generate_access_token(user_no, credential['user_id'])

            return jsonify({
                'user_no': user_no,
                'access_token': token
            })
        else:
            return '', 401

    @app.route('/home', methods=['POST'])
    @login_required
    def get_home_image_by_user():
        tag_list = request.json['tags']   # tags,  tag_no 리스트
        if tag_list == list([]):
            user_no = g.user_no
            user_id = g.user_id
            tag_list = tag_service.get_tag_list_by_user(user_no)
            user_images = image_service.get_image_list_by_user(user_no)
            if user_images:
                return jsonify({
                    'img_info': user_images,
                    'user_no': user_no,
                    'user_id': user_id,
                    'tag_list': tag_list,  # 대분류,중분류,태그
                    'type': 'S'
                })
            else:
                return '', 404
        else:
            user_no = g.user_no
            user_tags_images = image_service.get_image_list_by_tags(tag_list, user_no=user_no)
            if user_tags_images:
                return jsonify({
                    'img_info': user_tags_images,
                    'user_no': user_no,
                    'tag_list': tag_list,
                    'type': 'S'
                })
            else:
                return '', 404

    # 유입 , 이미지 넘버 클릭에 대해, home > S(검색),   public > S(검색),  public > R(추천)

    @app.route('/home/detail', methods=['POST'])    # '{"img_no": 10210, "type" : "S"}'
    @login_required
    def get_image_detail():
        img_no = request.json['img_no']  # img_no, type (추천클릭인지, 검색클릭인지)
        type = request.json['type']
        user_no = g.user_no
        image_service.insert_click_data(user_no, img_no, type)
        like_or_unlike = image_service.like_or_unlike_by_user_img(img_no, user_no)
        original_image = image_service.get_image_detail(img_no, user_no)
        if original_image:
            return jsonify({
                'img_info': original_image,
                'user_no': user_no,
                'like_or_unlike': like_or_unlike
            })
        else:
            return '', 404



    @app.route('/like/<int:img_no>', methods=['GET'])
    @login_required
    def insert_or_delete_like(img_no):
        user_no = g.user_no
        like_or_unlike = image_service.like_or_unlike_by_user_img(img_no, user_no)
        if(like_or_unlike):
            image_service.delete_like(img_no, user_no)
            return '', 200
        else:
            image_service.insert_like(img_no, user_no)
            return '', 200


    @app.route('/home/upload', methods=['POST'])
    @login_required
    def upload_image():
        user_no = g.user_no
        print(request.files)

        if 'upload_image' not in request.files:
            return 'File is missing', 404

        upload_image = request.files['upload_image']

        if upload_image.filename == '':
            return 'File is missing', 404

        filename = secure_filename(upload_image.filename)
        upload_image_info = image_service.upload_image(upload_image, filename, user_no)
        # 비동기 처리하기
        image_service.insert_image(upload_image_info)
        return '', 200

    @app.route('/home/delete/<int:img_no>', methods=['GET'])
    @login_required
    def delete_image(img_no):
       deleted_filename = image_service.delete_image(img_no)
       print(deleted_filename)

       return '', 200


    @app.route('/public', methods=['POST'])
    def get_public_image_by_tags():
        tag_list = request.json['tags']   # tags,  tag_no 리스트
        if tag_list == list([]):
            user_no = g.user_no
            search_tag_list = tag_service.get_public_tag_list()  # 검색용태그 리스트
            recommended_image = image_service.get_recommend_image_list_by_user(user_no)  ##유저기준 이미지 파일 추천 받음
            if recommended_image:
                return jsonify({
                    'img_info': recommended_image,
                    'user_no': user_no,
                    'search_tag_list': search_tag_list,
                    'type': 'R'
                })
            else:
                return '', 404
        else:
            user_tags_images = image_service.get_image_list_by_tags(tag_list)
            if user_tags_images:
                return jsonify({
                    'img_info': user_tags_images,
                    'tag_list': tag_list,
                    'type': 'S'
                })
            else:
                return '', 404


    # like

    @app.route('/likeimage', methods=['GET'])
    @login_required
    def get_like_image_by_user():
        user_no = g.user_no
        like_images = image_service.get_like_image_by_user(user_no)
        if like_images:
            return jsonify({
                'img_info' : like_images,
                'user_no' : user_no,
            })
        else:
            return '', 404

    @app.route('/test', methods=['GET'])
    def recommendation_update():
        success = model_service.recommendation_update()
        if(success):
            return '', 200
        else:
            return '', 404

    #
    # @app.route('/profile-picture/<int:user_no>', methods=['GET'])
    # def get_profile_picture(user_no):
    #     profile_picture = user_service.get_profile_picture(user_no)
    #
        # if profile_picture:
        #     return jsonify({'img_info': user_images})
    #     else:
    #         return '', 404
    #
    #
    # @app.route('/profile-picture', methods=['POST'])
    # @login_required
    # def upload_profile_picture():
    #     user_no = g.user_no
    #
    #     if 'profile_pic' not in request.files:
    #         return 'File is missing', 404
    #
    #     profile_pic = request.files['profile_pic']
    #
    #     if profile_pic.filename == '':
    #         return 'File is missing', 404
    #
    #     filename = secure_filename(profile_pic.filename)
    #     user_service.save_profile_picture(profile_pic, filename, user_no)
    #
    #     return '', 200
    #
    #
    #
    #
    #
    #
    #
    # @app.route('/follow', methods=['POST'])
    # @login_required
    # def follow():
    #     payload = request.json
    #     user_no = g.user_no
    #     follow_id = payload['follow']
    #
    #     user_service.follow(user_no, follow_id)
    #
    #     return '', 200
    #
    # @app.route('/unfollow', methods=['POST'])
    # @login_required
    # def unfollow():
    #     payload = request.json
    #     user_no = g.user_no
    #     unfollow_id = payload['unfollow']
    #
    #     user_service.unfollow(user_no, unfollow_id)
    #
    #     return '', 200
    #
    # @app.route('/timeline/<int:user_no>', methods=['GET'])
    # def timeline(user_no):
    #     timeline = tweet_service.get_timeline(user_no)
    #
    #     return jsonify({
    #         'user_no': user_no,
    #         'timeline': timeline
    #     })
    #
    # @app.route('/timeline', methods=['GET'])
    # @login_required
    # def user_timeline():
    #     timeline = tweet_service.get_timeline(g.user_no)
    #
    #     return jsonify({
    #         'user_no': user_no,
    #         'timeline': timeline
    #     })

    # @app.route('/tweet', methods=['POST'])
    # @login_required
    # def tweet():
    #     user_tweet = request.json
    #     tweet = user_tweet['tweet']
    #     user_no = g.user_no
    #
    #     result = tweet_service.tweet(user_no, tweet)
    #     if result is None:
    #         return '300자를 초과했습니다', 400
    #
    #     return '', 200