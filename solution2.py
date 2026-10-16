import os
import requests
from dotenv import load_dotenv
import folium
from folium import Map, Marker, Icon

# 1. Carrega as variáveis de ambiente a partir do arquivo .env
load_dotenv(".env")

# 2. Inicia a sessão HTTP e realiza a autenticação na API Olho Vivo da SPTrans
s = requests.Session()
token = os.getenv("SPTRANS_TOKEN")
auth_res = s.post(f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}")

if auth_res.text.lower() != "true":
    print("Falha na autenticação com a API da SPTrans. Verifique o token no arquivo .env.")
    exit()

# 3. Código da linha selecionado (utilizando a linha 33609 - diferente da 2506 dos slides)
CODIGO_LINHA = 33609

# 4. Busca as paradas da linha
res_paradas = s.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha?codigoLinha={CODIGO_LINHA}")
paradas = res_paradas.json()

# 5. Busca as posições dos ônibus em tempo real para a linha
res_posicao = s.get(f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha={CODIGO_LINHA}")
dados_posicao = res_posicao.json()
veiculos = dados_posicao.get("vs", [])

# 6. Inicialização do Mapa
# Se houver paradas, centraliza a visualização na primeira parada encontrada
if paradas:
    centro_lat = paradas[0]["py"]
    centro_lon = paradas[0]["px"]
else:
    # Coordenadas padrão de São Paulo caso a lista de paradas venha vazia
    centro_lat, centro_lon = -23.550520, -46.633308

mapa = Map(
    location=[centro_lat, centro_lon], 
    zoom_start=13, 
    tiles='Esri.WorldStreetMap'
)

# 7. Adiciona os pins das Paradas no mapa (Cor: Azul)
for parada in paradas:
    Marker(
        location=[parada["py"], parada["px"]],
        popup=parada.get("np", "Parada"),
        icon=Icon(color="blue", icon="info-sign")
    ).add_to(mapa)

# 8. Adiciona os pins dos Ônibus em tempo real no mapa (Cor: Vermelha)
for veiculo in veiculos:
    Marker(
        location=[veiculo["py"], veiculo["px"]],
        popup=f"Prefixo do Ônibus: {veiculo.get('p')}",
        icon=Icon(color="red", icon="bus", prefix="fa")
    ).add_to(mapa)

# 9. Salva o mapa em um arquivo HTML
mapa.save("mapa.html")
print("Mapa gerado com sucesso em 'mapa.html'!")