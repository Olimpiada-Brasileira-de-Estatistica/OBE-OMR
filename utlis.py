import csv
import os
import shutil

import cv2
import numpy as np

QUESTOES = 10
COLUNAS_GABARITO = 2
QUESTOES_POR_COLUNA = int(QUESTOES / COLUNAS_GABARITO)
ALTERNATIVAS = 4
COLUNAS_ID = 5


def retContorno(contornos):
    """
    Encontra os retângulos com base num vetor de pontos e devolve um vetor com
    os retângulos em ordem crescente de área

    Argumentos:
    contornos = Vetor de vetores com pontos que compõem os perímetros (contornos)
    encontrados dos poligonos pela função cv2.findContours
    """
    contornoRet = []
    for i in contornos:
        area = cv2.contourArea(i)
        if area > 50:
            pontas = encontraPontas(i)
            if len(pontas) == 4:
                contornoRet.append(i)
        # print(contornoRet)

    # Cria lista dos retângulos em ordem decrescente de área
    contornoRet = sorted(contornoRet, key=cv2.contourArea, reverse=True)

    return contornoRet


def encontraPontas(poligono):
    """
    Dado uma sequencia de pontos representando o perímetro de um polígono, conta
    quantas pontas este tem e retorna esse valor.

    Argumetnos:
    poligono = Vetor de pontos do perímetro de uma região encontrada pela função
    cv2.findContours
    """
    peri = cv2.arcLength(poligono, True)
    pontas = cv2.approxPolyDP(poligono, 0.02 * peri, True)
    return pontas


def reordenar(pontos):
    """
    Dado um vetor de pontos, ordena-os para preparar ajuste de perspectiva.
    Devolve-os em ordem: [[0,0], [largura, 0], [0, altura], [largura, altura]]

    Argumentos:
    pontos = Vetor com quatro pontos de um retângulo encontrado por retContorno
    """
    pontos = pontos.reshape((4, 2))
    novosPontos = np.zeros((4, 1, 2), np.int32)
    add = pontos.sum(1)
    diff = np.diff(pontos, axis=1)
    novosPontos[0] = pontos[np.argmin(add)]  # 0, 0
    novosPontos[1] = pontos[np.argmin(diff)]  # l, 0
    novosPontos[2] = pontos[np.argmax(diff)]  # 0, a
    novosPontos[3] = pontos[np.argmax(add)]  # l, a
    return novosPontos


def separarGabarito(gabarito):
    """
    Separa a imagem do gabarito do aluno recebia em seções com as marcações
    ("alternativas") separadas para leitura e devolve um vetor de matrizes do
    numpy (imagens separadas).

    Argumentos:
    id = Imagem do OpenCV com a seção "gabarito" do aluno
    """
    linhas = np.vsplit(gabarito, int(QUESTOES_POR_COLUNA))
    marcacoes = []
    for i in linhas:
        marcacoes.append(
            np.hsplit(i, COLUNAS_GABARITO + COLUNAS_GABARITO * ALTERNATIVAS)
        )
        # marcacoes = np.hsplit(i, COLUNAS_GABARITO)

    # Isso vai precisar de melhorias! Dropa as colunas "inúteis" (espaços em
    # branco números de questões)
    i = 0
    while i <= (COLUNAS_GABARITO - 1) * ALTERNATIVAS:
        marcacoes = np.delete(marcacoes, i, 1)  # Deleta a coluna inútil
        i += ALTERNATIVAS
    return marcacoes


def separarId(id):
    """
    Separa a imagem do id do aluno recebida em seções com as marcações
    ("alternativas") separadas para leitura e devolve um vetor de matrizes do
    numpy (imagens separadas).

    Argumentos:
    id = Imagem do OpenCV com a seção "id" do aluno (escrita manual inclusa)
    """
    linhas = np.vsplit(id, 10)  # Caixa dos alunos + marcações
    # linhas = np.delete(linhas, 0, 0)  # Deleta linha do id escrito
    marcacoes = []
    for i in linhas:
        marcacoes.append(np.hsplit(i, COLUNAS_ID))

    return marcacoes


def erro(tipo, arquivo):
    """
    Função para jogar erros. Altera o nome do arquivo da prova e coloca em uma
    pasta do erro específico. Retorna o erro conforme a lista abaixo:
        1. Erro na leitura da prova (não encontrou gabarito)
        2. Erro na leitura da prova (não encontrou id)
        3. Erro na leitura de id ou id inválido
        4. Erro no processamento da prova
    """
    nomeArqv = os.path.basename(arquivo)
    match tipo:
        case 1:
            shutil.move(arquivo, f"./ErroGabarito/{nomeArqv}")
            return 1
        case 2:
            shutil.move(arquivo, f"./ErroId/{nomeArqv}")
            return 2
        case 3:
            shutil.move(arquivo, f"./ErroId/{nomeArqv}")
            return 3
        case 4:
            shutil.move(arquivo, f"./ErroProc/{nomeArqv}")
            return 4


# Deve ter um jeito melhor de fazer isso
def escreveSaida(id, resposta):
    """
    Escreve em um arquivo .csv a saída da leitura da prova

    Argumentos:
    id = array do numpy com inteiros representando os algarismos lidos do id
    resposta = array do numpy com inteiros representando as respostas do aluno:
        0. Resposta em branco ou anulada
        1. Aternativa "a"
        2. Aternativa "b"
        3. Aternativa "c"
        4. Aternativa "d"
    """
    id = "".join(map(str, id))
    respostas = dict(enumerate(resposta, 1))
    dados = {"id": id}
    dados.update(respostas)
    print(dados)
    with open("./SaidaProvas/resultados.csv", "a") as saidacsv:
        writer = csv.writer(saidacsv)
        writer.writerow(dados.values())
        print(f"Escrevendo dados {dados}")


def preparaCSV():
    """
    Prepara o CSV para receber dados
    """
    with open("./SaidaProvas/resultados.csv", "w") as saidacsv:
        campos = ["id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"]
        writer = csv.DictWriter(saidacsv, fieldnames=campos)
        writer.writeheader()
