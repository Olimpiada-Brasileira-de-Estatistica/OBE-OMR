import cv2
import numpy as np

altura = 700
largura = 700

path = "./retavazia.jpg"
img = cv2.imread(path)

img = cv2.resize(img, (largura, altura))
imgContorno = img.copy()
imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgCinza, (5, 5), 10)
imgCanny = cv2.Canny(imgBlur, 10, 50)

contours, hierarchy = cv2.findContours(
    imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
)
cv2.drawContours(imgContorno, contours, -1, (0, 255, 0), 2)

cv2.imshow("Original", imgContorno)
while True:
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
