import typer
import inquirer
from yaspin import yaspin
import time
import pydobot
from serial.tools import list_ports

# cria uma instância da aplicação
app = typer.Typer()

# cria uma instância do spinner
spinner = yaspin(text="Processando...", color="yellow")

# lista as portas dispoíveis
available_ports = list_ports.comports()

# pede para o usuário escolher uma das portas disponíveis
porta_escolhida = inquirer.prompt([
    inquirer.List("porta", message="Escolha a porta serial", choices=[x.device for x in available_ports])
])["porta"]

# cria uma instância do robô
robo = pydobot.Dobot(port=porta_escolhida, verbose=False)

# cria um comando CLI
@app.command()
def movimento():
    # realiza lista de perguntas para o usuário
    perguntas = [
        inquirer.List("operacao", message="Qual movimento deseja realizar?", choices=["home", "ligar ferramenta","desligar ferramenta","mover x100", "atual"])
    ]
    # realiza a leitura das respostas
    respostas = inquirer.prompt(perguntas)
    # realiza a operação
    saida = processar(respostas)
    # exibe o resultado
    print(saida)
    # comandos caso continue
    continuar = typer.confirm("Deseja continuar?")
    if continuar == True:
        movimento()
    elif continuar == False:
         robo.close()

# função que retorna uma pergunta par ao usuário dependendo da escolha
def verificar(dados):
    operacao = dados["operacao"]
    if operacao == "mover x100":
        return inquirer.Text("a", message="Digite x ou y ou z para especificar a direção desejada")
    else:
        return inquirer.Text("a", message="Digite c para confirmar")

        
# função que processa a operação e encaminha para as funções das opções
def processar(dados):
    time.sleep(1)
    operacao = dados["operacao"]
    dados = inquirer.prompt([verificar(dados)])
    a = dados["a"]
    if operacao == "home":
        if a== "c":
            home()
            return ("feito")
    elif operacao == "ligar ferramenta":
        if a== "c":
            ligar_atuador()
            return("feito")
    elif operacao == "desligar ferramenta":
        if a== "c":  
            desligar_atuador()
            return("feito")
    elif operacao == "mover x100":
        movimentacao_x100(a)
        return("feito")
    elif operacao == "atual":
        atual()
        return ("feito")

# função que faz voltar para um conjunto pré definido de pontos
def home():
    spinner.start()
    robo.move_to(230, 1, 159, 0, wait=True)
    spinner.stop()

# função que faz o robô se movimentar uma distância de 100 (em x, y ou z)
def movimentacao_x100(a):
    x_atual, y_atual, z_atual, r_atual, inclinacao1, inclinacao2, inclinacao3, inclinacao4 = robo.pose()
    distancia = 100
    if a == "x":
        x_novo = x_atual + distancia
        robo.move_to(x=x_novo, y=y_atual, z=z_atual, r=r_atual)
    elif a == "y":
        y_novo = y_atual + distancia
        robo.move_to(x=x_atual, y=y_novo, z=z_atual, r=r_atual)
    elif a =="z":
        z_novo = z_atual - distancia
        robo.move_to(x=x_atual, y=y_atual, z=z_novo, r=r_atual)

# função que liga o atuador
def ligar_atuador():
    spinner.start()
    robo.suck(True)
    robo.wait(200)
    spinner.stop()

# função que desliga o atuador
def desligar_atuador():
    spinner.start()
    robo.suck(False)
    robo.wait(200)
    spinner.stop()

# função que retorna a posição atual
def atual():
    posicao_atual = robo.pose()
    print(f"Posição atual: {posicao_atual}")
    
# Executa a aplicação
if __name__ == "__main__":
    app()