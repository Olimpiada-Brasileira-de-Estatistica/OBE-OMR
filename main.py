import os

import cv2
import numpy as np

import utlis

ALTURA = 700
LARGURA = 700
LIMITE_GABARITO = 1900
LIMITE_ID = 3100


def main():
    utlis.preparaCSV()
    with os.scandir("./Provas/") as es:
        for e in es:
            print(f"Analisando prova {e.path}")
            analisaProva(str(e.path))
    return None


def processaProvas(img):
    img = cv2.resize(img, (LARGURA, ALTURA))
    imgContorno = img.copy()
    imgInteresses = img.copy()
    imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgCinza, (5, 5), 10)
    imgCanny = cv2.Canny(imgBlur, 10, 50)

    # Desenhando contornos
    contornos, hierarchy = cv2.findContours(
        imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    cv2.drawContours(imgContorno, contornos, -1, (0, 255, 0), 2)

    # cv2.imshow("Contornos", imgContorno)
    # while True:
    #     if cv2.waitKey(25) & 0xFF == ord("q"):
    #         break

    # Encontrando retângulos de interesse
    retangulos = utlis.retContorno(contornos)
    pontasRetanguloGabarito = utlis.reordenar(utlis.encontraPontas(retangulos[0]))
    pontasRetanguloId = utlis.reordenar(utlis.encontraPontas(retangulos[1]))

    # Arrumando perspectiva
    pt1Gabarito = np.float32(pontasRetanguloGabarito)
    pt2Gabarito = np.float32([[0, 0], [LARGURA, 0], [0, ALTURA], [LARGURA, ALTURA]])
    transformacaoGabarito = cv2.getPerspectiveTransform(pt1Gabarito, pt2Gabarito)
    imgGabaritoArrumada = cv2.warpPerspective(
        img, transformacaoGabarito, (LARGURA, ALTURA)
    )

    pt1Id = np.float32(pontasRetanguloId)
    pt2Id = np.float32([[0, 0], [770, 0], [0, 770], [770, 770]])
    transformacaoId = cv2.getPerspectiveTransform(pt1Id, pt2Id)
    imgIdArrumada = cv2.warpPerspective(img, transformacaoId, (770, 770))
    imgIdArrumada = imgIdArrumada[80:740, 10:760]

    # Exibir retângulos detectados (TEST)
    if pontasRetanguloGabarito.size != 0 and pontasRetanguloId.size != 0:
        cv2.drawContours(imgInteresses, pontasRetanguloGabarito, -1, (255, 0, 0), 5)
        cv2.drawContours(imgInteresses, pontasRetanguloId, -1, (0, 0, 255), 5)

    # Limiar marcados
    imgIdCinza = cv2.cvtColor(imgIdArrumada, cv2.COLOR_BGR2GRAY)
    imgIdLimiar = cv2.threshold(imgIdCinza, 170, 255, cv2.THRESH_BINARY_INV)[1]
    imgGabaritoCinza = cv2.cvtColor(imgGabaritoArrumada, cv2.COLOR_BGR2GRAY)
    imgGabaritoLimiar = cv2.threshold(
        imgGabaritoCinza, 170, 255, cv2.THRESH_BINARY_INV
    )[1]

    # # Exibir (TEST)
    # cv2.imshow("Contornos detectados", imgContorno)
    # cv2.imshow("Interesses", imgInteresses)
    # cv2.imshow("Gabarito Aguia", imgGabaritoArrumada)
    # cv2.imshow("Id Aguia", imgIdArrumada)
    # cv2.imshow("Gabarito Cinza Limiar", imgGabaritoLimiar)
    # # cv2.imshow("marc", marcs[0][0])
    # while True:
    #     if cv2.waitKey(25) & 0xFF == ord("q"):
    #         break
    # cv2.destroyAllWindows()

    return imgIdLimiar, imgGabaritoLimiar


def analisaProva(caminho):
    # Processando imagem
    img = cv2.imread(caminho)
    # try:
    imgIdLimiar, imgGabaritoLimiar = processaProvas(img)
    # except Exception as e:
    #     utlis.erro(4, caminho)
    #     print(f"Erro no processamento da Prova! Erro: {e}")
    #     return 4

    # cv2.imshow("id", imgIdLimiar)
    # cv2.imshow("gab", imgGabaritoLimiar)
    # while True:
    #     if cv2.waitKey(25) & 0xFF == ord("q"):
    #         break

    # Ler Gabarito
    try:
        marcsGab = utlis.separarGabarito(imgGabaritoLimiar)
    except Exception as e:
        utlis.erro(1, caminho)
        print(f"Erro na leitura do Gabarito! Erro: {e}")
        return 1

    respostas = np.zeros(utlis.QUESTOES)
    k = 0
    while k < utlis.COLUNAS_GABARITO:  # Itera colunas
        j = 0
        while j < utlis.QUESTOES_POR_COLUNA:  # Itera linhas na coluna
            i = 0
            resposta = 0
            while i < utlis.ALTERNATIVAS:  # Itera alternativas da questão
                pixeis = cv2.countNonZero(marcsGab[j][i + (k * utlis.ALTERNATIVAS)])

                # DEBUG
                # cv2.imshow("atual", marcs[j][i + (k * utlis.ALTERNATIVAS)])
                # print(pixeis)
                # print("i = ", i, " j = ", j, " k = ", k)
                # while True:
                #     if cv2.waitKey(25) & 0xFF == ord("q"):
                #         break

                if pixeis >= LIMITE_GABARITO:
                    if resposta != 0:  # Marcou o gabarito errado = anula
                        # print("Resposta inválida!")
                        resposta = 0
                        break
                    resposta = i + 1
                i += 1
            respostas[k * utlis.QUESTOES_POR_COLUNA + j] = resposta
            # print("Anotando resposta", resposta, " em ", k * utlis.QUESTOES_POR_COLUNA + j)
            j += 1
        k += 1

    try:
        marcsId = utlis.separarId(imgIdLimiar)
    except Exception as e:
        utlis.erro(2, caminho)
        print(f"Erro na leitura do Id! Erro: {e}")
        return 2

    idAluno = np.ones(utlis.COLUNAS_ID) * -1
    k = 0
    while k < 10:  # Linhas da identificação
        i = 0
        while i < utlis.COLUNAS_ID:  # Marcações na linha
            pixeis = cv2.countNonZero(marcsId[k][i])

            # DEBUG
            # cv2.imshow("atual", marcsId[k][i])
            # print(pixeis)
            # print("i = ", i, " k = ", k)
            # while True:
            #     if cv2.waitKey(25) & 0xFF == ord("q"):
            #         break

            if pixeis >= LIMITE_ID:
                if idAluno[i] != -1:
                    utlis.erro(2, caminho)
                    print(f"Erro na leitura do Id ou Id Inválido!")
                    return 2
                if k == 9:
                    # print(f"Escrevendo 0 na pos {i} do id")
                    idAluno[i] = 0
                else:
                    # print(f"Escrevendo {k + 1} na pos {i} do id")
                    idAluno[i] = k + 1
            i += 1
        k += 1
    if -1 in idAluno:
        utlis.erro(2, caminho)
        print(f"Erro na leitura do Id ou Id Inválido após leitura completa!")
        return 2

    utlis.escreveSaida(idAluno, respostas)

    return 0


main()
