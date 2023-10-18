import requests
from kivy.app import App


class Firebase():
    API_KEY = "AIzaSyC_cZQ7KvhTN6CUkk3mFk3UU9xDQuu5P3M"

    def criar_conta(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            idToken = requisicao_dic["idToken"]
            refreshToken = requisicao_dic["refreshToken"]
            localId = requisicao_dic["localId"]

            meu_app = App.get_running_app()
            meu_app.localid = localId
            meu_app.idtoken = idToken

            with open("refreshToken.txt", "w") as arquivo:
                arquivo.write(refreshToken)

            req_id = requests.get(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={idToken}")
            id_vendedor = req_id.json()

            link = f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{localId}.json?auth={idToken}"
            info_usuario = f'{{"id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            #atualizar o proximo_id_vendedor
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/.json?auth={idToken}",
                           data=info_id_vendedor)

            meu_app.carregar_infos_usuarios()
            meu_app.mudar_tela("homepage")

        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_app = App.get_running_app()
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["msglogin"].text = mensagem_erro
            pagina_login.ids["msglogin"].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            idToken = requisicao_dic["idToken"]
            refreshToken = requisicao_dic["refreshToken"]
            localId = requisicao_dic["localId"]

            meu_app = App.get_running_app()
            meu_app.localid = localId
            meu_app.idtoken = idToken

            with open("refreshToken.txt", "w") as arquivo:
                arquivo.write(refreshToken)

            meu_app.carregar_infos_usuarios()
            meu_app.mudar_tela("homepage")

        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_app = App.get_running_app()
            pagina_login = meu_app.root.ids["loginpage"]
            pagina_login.ids["msglogin"].text = mensagem_erro
            pagina_login.ids["msglogin"].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]
        return local_id, id_token

    def retornar_fornecedor(self):
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        requisicao = requests.post(link)
        requisicao_dic = requisicao.json()
        idToken = requisicao_dic["idToken"]
        req_f = requests.get(
            f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/fornecedores.json?auth={idToken}")
        id_fornecedor = req_f.json()
        return id_fornecedor
