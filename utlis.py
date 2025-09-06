import cv2
import numpy as np

QUESTOES = 10
COLUNAS_GABARITO = 2
QUESTOES_POR_COLUNA = int(QUESTOES / COLUNAS_GABARITO)
ALTERNATIVAS = 4
COLUNAS_ID = 5
LIMITE = 1900


def retContorno(contornos):

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


def encontraPontas(retangulo):
    peri = cv2.arcLength(retangulo, True)
    pontas = cv2.approxPolyDP(retangulo, 0.02 * peri, True)
    return pontas


def reordenar(pontos):
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
    linhas = np.vsplit(gabarito, int(QUESTOES_POR_COLUNA))
    marcacoes = []
    for i in linhas:
        marcacoes.append(
            np.hsplit(i, COLUNAS_GABARITO + COLUNAS_GABARITO * ALTERNATIVAS)
        )
        # marcacoes = np.hsplit(i, COLUNAS_GABARITO)
    return marcacoes


def separarId():

    return
