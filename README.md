# Como usar o programa

Coloque todas as provas (jpg, png ou outro arquivo de *imagem*, PDFs ainda não
tem suporte!) em um diretório (pasta) chamado "Provas", no mesmo local do
arquivo `main.py` e `utlis.py`. Rode o programa com `python main.py`.

Arquivos mal lidos serão movidos para outras pastas para avaliação manual. O
resultado da leitura será salvo em `./SaidaProvas/resultados.csv`.

# Recomendações

Para melhor funcionalidade, recomendamos uso de imagens escaneadas ou fotos com
boa resolução e com bordas e marcações bem visíveis. Caso sejam marcados pontos
nas bordas (perímetro dos retângulos) dos gabaritos e dos IDs, o programa pode
funcionar mal.

Priorizamos acurácia dos dados sobre estabilidade de runtime, isto é, o programa pode
falhar algumas vezes, mas provavelmente não guardará dados incorretos.

# Dependências

São necessários os pacotes `OpenCV` e `numpy`. Caso use Nix, disponibilizamos um
flake para ser acessado com `nix develop`. Caso contrário, recomendamos o uso do
`pip`: atualize o pip `pip install --upgrade pip` e para a maioria dos sistemas
`pip install opencv-python`. Para sistemas Headless, como servidores ou docker,
`pip install opencv-python-headless`. O numpy é instalado da mesma maneira: `pip
install numpy`.
