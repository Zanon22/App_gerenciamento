from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from telas import *
from botoes import *
import requests
import os
from functools import partial
from firebase import Firebase
from datetime import date
from kivy.clock import Clock
import random

GUI = Builder.load_file("main.kv")


class MainApp(App):

    def build(self):

        self.firebase = Firebase()
        return GUI

    def on_start(self):
        # carrega as infos
        self.carregar_infos_usuarios()
        try:
            self.valores_fornecedor()
        except:
            pass
        try:
            self.valores_produtos()
        except:
            pass
        try:
            self.valores_receitas()
        except:
            pass
        try:
            self.estoque()
        except:
            pass

    def carregar_infos_usuarios(self):
        try:
            with open("refreshToken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.localid = local_id
            self.idtoken = id_token

            # pegar informações do usuario
            requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.idtoken}')
            requisicao_dic = requisicao.json()
        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def add_fornecedor(self):

        pagina_add_fornecedor =self.root.ids["addfornecedorpage"]
        fornecedor = pagina_add_fornecedor.ids["fornecedor"].text

        if not fornecedor:
            pagina_add_fornecedor.ids["fornecedor_label"].color = (1, 0, 0, 1)

        if fornecedor:

            info = f'{{"fornecedor": "{fornecedor}"}}'
            requests.post(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/fornecedores.json?auth={self.idtoken}",
                data=info)
            self.mudar_tela("compraspage")
            self.valores_fornecedor()

        fornecedor = None

    def add_produto(self):

        pagina_add_produto =self.root.ids["addprodutopage"]
        produto = pagina_add_produto.ids["produto"].text
        und_medida = pagina_add_produto.ids["und_medida"].text
        qnt_medida = pagina_add_produto.ids["qnt_medida"].text

        if not produto:
            pagina_add_produto.ids["produto_label"].color = (1, 0, 0, 1)

        if not und_medida:
            pagina_add_produto.ids["undm_label"].color = (1, 0, 0, 1)

        if not qnt_medida:
            pagina_add_produto.ids["qntm_label"].color = (1, 0, 0, 1)
        else:
            try:
                qnt_medida = float(qnt_medida)
            except:
                pagina_add_produto.ids["qntm_label"].color = (1, 0, 0, 1)

        if produto and und_medida and qnt_medida and (type(qnt_medida) == float):
            quantidade = 0
            info = f'{{"Quantidade": {quantidade}}}'
            requests.put(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/estoque/{produto}.json?auth={self.idtoken}",
                data=info)

        if produto and und_medida and qnt_medida and (type(qnt_medida) == float):
            info = f'{{"produto": "{produto}", "Unidade de Medida": "{und_medida}", "Quantidade de Medida": "{qnt_medida}"}}'
            requests.post(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/produtos.json?auth={self.idtoken}",
                data=info)
            self.mudar_tela("compraspage")
            self.valores_produtos()

        produto = None
        und_medida = None
        qnt_medida = None

    def valores_fornecedor(self):
        pagina_precompra = self.root.ids["precomprapage"]
        requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.idtoken}')
        requisicao_dic = requisicao.json()
        valores = requisicao_dic['fornecedores']
        self.valores = valores
        select_fornecedores = pagina_precompra.ids["fornecedor"]
        lista_fornecedores = []

        for fornecedores in valores:
            fornecedor = valores[fornecedores]
            texto = fornecedor['fornecedor']
            lista_fornecedores.extend(texto.split(','))

        select_fornecedores.values = lista_fornecedores

    def valores_produtos(self):
        pagina_add_produto = self.root.ids["addcomprapage"]
        pagina_add_receita = self.root.ids["addreceitaspage"]
        requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.idtoken}')
        requisicao_dic = requisicao.json()
        valores = requisicao_dic['produtos']
        self.valores = valores
        select_produtos = pagina_add_produto.ids["produto"]
        select_produtos2 = pagina_add_receita.ids["produto"]
        lista_produtos = []

        for produtos in valores:
            produto = valores[produtos]
            texto = produto['produto']
            lista_produtos.extend(texto.split(','))

        select_produtos.values = lista_produtos
        select_produtos2.values = lista_produtos

    def valores_receitas(self):
        pagina_produzir = self.root.ids["produzirpage"]
        requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.idtoken}')
        requisicao_dic = requisicao.json()
        valores = requisicao_dic['receita']
        self.valores = valores
        select_produtos = pagina_produzir.ids["receita"]
        lista_receitas = []

        for receitas in valores:
            receita = valores[receitas]
            texto = receita['receita']
            lista_receitas.extend(texto.split(','))

        select_produtos.values = lista_receitas

    def pre_compra(self):
        global id_formatado_global
        pagina_precompra = self.root.ids["precomprapage"]
        #data = pagina_precompra.ids["data"].text
        fornecedor = pagina_precompra.ids["fornecedor"].text
        frete_total = pagina_precompra.ids["frete"].text
        desconto_total = pagina_precompra.ids["desconto"].text
        preco_total = pagina_precompra.ids["preco"].text
        requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.idtoken}')
        requisicao_dic = requisicao.json()
        lista_ids = []

        try:
            valores = requisicao_dic['compras']
            self.valores = valores
            lista_ids = []
            for ids in valores:
                id = valores[ids]
                texto = id['id']
                lista_ids.extend(texto.split(','))
        except:
            pass

        while True:
            id_compra = random.randrange(100000)
            id_formatado = '{:05d}'.format(id_compra)

            if not lista_ids:
                break
            elif id_formatado in lista_ids:
                pass
            else:
                break

        if not fornecedor:
            pagina_precompra.ids["forecedor_label"].color = (1, 0, 0, 1)

        if not preco_total:
            pagina_precompra.ids["preco_label"].color = (1, 0, 0, 1)
        else:
            try:
                preco_total = float(preco_total)
            except:
                pagina_precompra.ids["preco_label"].color = (1, 0, 0, 1)

        if not desconto_total:
            pagina_precompra.ids["desconto_label"].color = (1, 0, 0, 1)
        else:
            try:
                desconto_total = float(desconto_total) or 0
            except:
                pagina_precompra.ids["desconto_label"].color = (1, 0, 0, 1)

        if not frete_total:
            pagina_precompra.ids["frete_label"].color = (1, 0, 0, 1)
        else:
            try:
                frete_total = float(frete_total) or 0
            except:
                pagina_precompra.ids["frete_label"].color = (1, 0, 0, 1)

        if fornecedor and frete_total and desconto_total and preco_total and (type(preco_total) == float) and (type(desconto_total) == float or 0) and (type(frete_total) == float or 0):
            info = f'{{"Fornecedor": "{fornecedor}", "Frete total": "{frete_total}", "Preco total": "{preco_total}", "Desconto total": "{desconto_total}"}}'
            requests.put(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/compras/{id_formatado}.json?auth={self.idtoken}",
                data=info)
            self.mudar_tela("addcomprapage")
            id_formatado_global = id_formatado

    def registrar_compra(self):
        global id_formatado_global

        pagina_add_produto = self.root.ids["addcomprapage"]
        pagina_precompra = self.root.ids["precomprapage"]

        produto = pagina_add_produto.ids["produto"].text
        quantidade = pagina_add_produto.ids["quantidade"].text
        preco = pagina_add_produto.ids["preco"].text
        frete_total = pagina_precompra.ids["frete"].text
        desconto_total = pagina_precompra.ids["desconto"].text
        preco_total = pagina_precompra.ids["preco"].text

        if not produto:
            pagina_add_produto.ids["produto_label"].color = (1, 0, 0, 1)

        if not preco:
            pagina_add_produto.ids["preco_label"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_add_produto.ids["preco_label"].color = (1, 0, 0, 1)

        if not quantidade:
            pagina_add_produto.ids["quantidade_label"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = int(quantidade)
            except:
                pagina_add_produto.ids["quantidade_label"].color = (1, 0, 0, 1)

        if produto and preco and quantidade and (type(preco) == float) and (type(quantidade) == int):
            req_poduto_quantidade = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/estoque/{produto}.json?auth={self.idtoken}')
            quantidade_add = req_poduto_quantidade.json()
            valores = quantidade_add
            self.valores = valores
            for quants in valores:
                quant = valores[quants]
                numero = quant
                quantidade_formatada = (numero)
            quantidade_final = int(quantidade_formatada) + quantidade
            info = f'{{"Quantidade": {quantidade_final}}}'
            requests.put(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/estoque/{produto}.json?auth={self.idtoken}",
                data=info)
            info = f'{{"produto": "{produto}", "quantidade": "{quantidade}", "preco": "{preco}"}}'
            requests.post(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/compras/{id_formatado_global}.json?auth={self.idtoken}",
                data=info)
            self.mudar_tela("addcomprapage")
            produto = None
            quantidade = None
            preco = None

    def estoque(self):
        requisicao = requests.get(f'https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/estoque.json?auth={self.idtoken}')
        requisicao_dic = requisicao.json()
        try:
            estoques = requisicao_dic
            self.vendas = estoques
            pagina_estoque = self.root.ids["gerenciarestoquepage"]
            lista_estoque = pagina_estoque.ids["lista_estoque"]
            for id_estoque in estoques:
                formatar = list(estoques.keys())
                produto = formatar[0]
                estoque = estoques[id_estoque]
                quantidade = estoque['Quantidade']
                banner = Label(text=f"[color=#900030]{produto}:[/color] [b]possui {quantidade} unidades[/b]", markup= True)
                lista_estoque.add_widget(banner)
        except:
            pass

    def criar_receita(self):
        pagina_addreceita = self.root.ids["addreceitaspage"]
        pagina_prereceita = self.root.ids["prereceitapage"]
        nome_receita = pagina_prereceita.ids["receita"].text
        produto = pagina_addreceita.ids["produto"].text
        quantidade = pagina_addreceita.ids["quantidade"].text

        if not nome_receita:
            pagina_prereceita.ids["nome_label"].color = (1, 0, 0, 1)
        if not produto:
            pagina_addreceita.ids["produto_label"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_addreceita.ids["quantidade_label"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_addreceita.ids["quantidade_label"].color = (1, 0, 0, 1)

        if produto and quantidade and (type(quantidade) == float):
            info = f'{{"quantidade": "{quantidade}"}}'
            requests.put(
                f"https://app-gerenciamento-f87d2-default-rtdb.firebaseio.com/{self.localid}/receitas/{nome_receita}/{produto}.json?auth={self.idtoken}",
                data=info)

    def produzir_receita(self):
        pagina_produzir = self.root.ids["produzirpage"]
        receita = pagina_produzir.ids["receita"].text
        quantidade = pagina_produzir.ids["quantidade"].text


MainApp().run()
