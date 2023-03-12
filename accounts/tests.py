import random

from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from mysite import settings
from tweets.models import Tweet

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        """
        クラスの中で定義される関数はメソッド
        サーバーから情報を取得できるかtest

        ほんとはClientのimportが必要っぽい。今回はtest.pyの中なので大丈夫
                                ↑TestCaseではインスタンスにclientが定義されている!
        status_codeは404みたいなやつ。200はリクエスト成功
        reverseでURL取得、client.getを実行。client,getはTestCaseで定義されてる
        assert*はunittest等も多い
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        # サーバーへ情報が登録できるかtest

        user = {
            "username": "test",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, user)
        self.assertTrue(User.objects.filter(username="test", email="test@example.com").exists())
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,  # はじめに返ってくるHTTPレスポンスコード
            target_status_code=200,  # 最終的に返ってくるHTTPのレスポンスコード
            msg_prefix="",  # テスト結果のメッセージのプレフィックス
            fetch_redirect_response=True,  # 最終ページをロードするか否か
        )

        self.assertIn(SESSION_KEY, self.client.session)  # sessionを使うならsetting.pyを書き換え,AinBの確認。

    def test_failure_post_with_empty_form(self):
        data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        expected_errs = {
            "username": "このフィールドは必須です。",
            "email": "このフィールドは必須です。",
            "password1": "このフィールドは必須です。",
            "password2": "このフィールドは必須です。",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        for key, value in expected_errs.items():
            self.assertIn(value, form.errors[key])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_username(self):
        data = {
            "username": "",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {
            "username": "このフィールドは必須です。",
        }
        self.assertIn(expected_errs["username"], form.errors["username"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_email(self):
        data = {
            "username": "test",
            "email": "",
            "password1": "pass0000",
            "password2": "pass0000",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {
            "email": "このフィールドは必須です。",
        }
        self.assertIn(expected_errs["email"], form.errors["email"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_password(self):
        data = {
            "username": "test",
            "email": "hoge@email.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {
            "password1": "このフィールドは必須です。",
            "password2": "このフィールドは必須です。",
        }
        for key, value in expected_errs.items():
            self.assertIn(value, form.errors[key])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_duplicated_user(self):
        User.objects.create_user(username="test", email="fuga@email.com", password="passcode0000")
        data2 = {
            "username": "test",
            "email": "fuga@email.com",
            "password1": "passcode0000",
            "password2": "passcode0000",
        }
        response = self.client.post(self.url, data2)
        form = response.context["form"]
        expected_errs = {"username": "同じユーザー名が既に登録済みです。"}
        self.assertIn(expected_errs["username"], form.errors["username"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_failure_post_with_invalid_email(self):
        data = {
            "username": "testpscd",
            "email": "fuga.email.com",
            "password1": "test0000",
            "password2": "test0000",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {"email": "有効なメールアドレスを入力してください。"}
        self.assertIn(expected_errs["email"], form.errors["email"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_too_short_password(self):
        data = {
            "username": "test",
            "email": "fuga@email.com",
            "password1": "passcd",
            "password2": "passcd",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {"password2": "このパスワードは短すぎます。最低 8 文字以上必要です。"}
        self.assertIn(expected_errs["password2"], form.errors["password2"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_password_similar_to_username(self):
        data = {
            "username": "testpscd",
            "email": "fuga@email.com",
            "password1": "testpscd",
            "password2": "testpscd",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {"password2": "このパスワードは ユーザー名 と似すぎています。"}
        self.assertIn(expected_errs["password2"], form.errors["password2"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_only_numbers_password(self):
        data = {
            "username": "testpscd",
            "email": "fuga@email.com",
            "password1": "20040326",
            "password2": "20040326",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {"password2": "このパスワードは数字しか使われていません。"}
        self.assertIn(expected_errs["password2"], form.errors["password2"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_mismatch_password(self):
        data = {
            "username": "testpscd",
            "email": "fuga@email.com",
            "password1": "testpasscd",
            "password2": "testpassdc",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        expected_errs = {"password2": "確認用パスワードが一致しません。"}
        self.assertIn(expected_errs["password2"], form.errors["password2"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)


class TestHomeView(TestCase):
    def test_success_get(self):
        pass


class TestLoginView(TestCase):
    def setUp(self):
        user = {
            "email": "hogefuga@fuga.com",
            "username": "hoge",
            "password1": "pass0000",
            "password2": "pass0000",
        }
        User.objects.create_user(user["username"], user["email"], user["password1"])
        self.login = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        loginPost = {
            "username": "hoge",
            "password": "pass0000",
        }
        response = self.client.post(self.login, loginPost)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL), 302, 200)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        loginPost = {
            "username": "fuga",
            "password": "pass1111",
        }
        response = self.client.post(self.login, loginPost)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            ["正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        loginPost = {
            "username": "hoge",
            "password": "",
        }
        response = self.client.post(self.login, loginPost)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["このフィールドは必須です。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        logoutPost = User.objects.create_user(username="hoge", password="pass0000", email="hoge@fuga.com")
        self.client.force_login(logoutPost)

    def test_success_get(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL), 302, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="hogehogeman",
            password="testpasscd",
            email="hoge@email.com",
        )
        self.client.force_login(self.user)
        # 10人以下のランダムな数新しいuserを追加する
        self.followees = []
        for i in range(random.randint(3, 10)):
            followee = User.objects.create_user(
                username=f"followee{i}",
                password=f"followeepass{i}",
                email=f"followee{i}@email.com",
            )
            self.followees.append(followee)
        # self.userが全部のアカウントをフォロー
        for followee in self.followees:
            self.user.following.add(followee)

        # self.userが10以下の数ツイート
        for i in range(random.randint(3, 10)):
            Tweet.objects.create(
                user=self.user,
                content=f"Test tweet {i} from {self.user}",
            )

    def test_success_get(self):
        response = self.client.get(reverse("accounts:user_profile", kwargs={"username": self.user.username}))
        # context内に含まれるフォロー数とフォロワー数がDBに保存されている該当のユーザーのフォロー数とフォロワー数に同一であることを確認する
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["followings_count"], len(self.followees))
        self.assertEqual(response.context["followers_count"], 0)
        # context内に含まれるツイート一覧が、DBに保存されている該当のユーザーのツイート一覧と同一である
        tweet_list = response.context["tweet_list"]
        self.assertEqual(len(list(tweet_list)), len(self.user.tweets.all()))


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="hoge@example.com",
            password="hogepass",
        )
        self.targetuser = User.objects.create_user(
            username="targetuser",
            email="fuga@example.com",
            password="fugapass",
        )
        self.client.force_login(self.user)

    #        self.client.force_login(self.user)
    #
    #    def test_success_post(self):
    #        response = self.client.post(
    #            reverse(
    #                "accounts:follow",
    #                kwargs={"username": self.targetuser.username},
    #            ),
    #        )
    #        self.assertRedirects(
    #            response,
    #            reverse("tweets:home"),
    #            status_code=302,
    #            target_status_code=200,
    #        )
    #        self.assertEqual(self.user.following.count(), 1)
    #        self.assertEqual(self.user.following.first(), self.targetuser)
    #
    #    def test_failure_post_with_not_exist_user(self):
    #        response = self.client.post(
    #            reverse(
    #                "accounts:follow",
    #                kwargs={"username": "heman"},
    #            ),
    #        )
    #        self.assertEqual(response.status_code, 404)
    #        self.assertEqual(self.user.following.count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(
            reverse(
                "accounts:follow",
                kwargs={"username": self.user.username},
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 400)
        form = response.content.decode("utf-8")
        expected_errs = "自分自身をフォローすることはできません。"
        self.assertEqual(expected_errs, form)
        self.assertEqual(self.user.following.count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="hoge@example.com",
            password="hogepass",
        )
        self.targetuser = User.objects.create_user(
            username="targetuser",
            email="fuga@example.com",
            password="fugapass",
        )
        self.user.following.add(self.targetuser)
        self.client.force_login(self.user)

    def test_success_post(self):
        res = self.client.post(
            reverse(
                "accounts:unfollow",
                kwargs={"username": self.targetuser.username},
            ),
        )
        self.assertRedirects(
            res,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(self.user.following.count(), 0)

    def test_failure_post_with_not_exist_user(self):
        res = self.client.post(
            reverse(
                "accounts:unfollow",
                kwargs={"username": "heman"},
            ),
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(self.user.following.count(), 1)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(
            reverse(
                "accounts:unfollow",
                kwargs={"username": self.user.username},
            ),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.following.count(), 1)
        form = response.content.decode("utf-8")
        expected_errs = "自分自身にリクエストできません。"
        self.assertEqual(expected_errs, form)


class TestFollowingListView(TestCase):
    def setUp(self):
        # 10人以下のランダムな数新しいuserを追加する
        self.user = User.objects.create_user(
            username="test",
            password="testpasscd",
            email="hoge@email.com",
        )
        self.client.force_login(self.user)
        self.followees = []
        for i in range(random.randint(3, 10)):
            followee = User.objects.create_user(
                username=f"followee{i}",
                password=f"followeepass{i}",
                email=f"followee{i}@email.com",
            )
            self.followees.append(followee)

        for followee in self.followees:
            self.user.following.add(followee)

    def test_success_get(self):
        res = self.client.get(
            reverse(
                "accounts:following_list",
                kwargs={"username": self.user.username},
            )
        )
        self.assertEqual(res.status_code, 200)
        user_list = res.context["user_list"]
        self.assertEqual(list(user_list), self.followees)


class TestFollowerListView(TestCase):
    def setUp(self):
        # 10人以下のランダムな数新しいuserを追加する
        self.user = User.objects.create_user(
            username="test",
            password="testpasscd",
            email="hoge@email.com",
        )
        self.client.force_login(self.user)
        self.followers = []
        for i in range(random.randint(3, 10)):
            follower = User.objects.create_user(
                username=f"follower{i}",
                password=f"followerpass{i}",
                email=f"follower{i}@email.com",
            )
            self.followers.append(follower)

        for follower in self.followers:
            follower.following.add(self.user)

    def test_success_get(self):
        res = self.client.get(
            reverse(
                "accounts:follower_list",
                kwargs={"username": self.user.username},
            )
        )
        self.assertEqual(res.status_code, 200)
        user_list = res.context["user_list"]
        self.assertEqual(list(user_list), self.followers)
