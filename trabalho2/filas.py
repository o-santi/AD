from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto
from numpy import random
import numpy as np
from matplotlib import pyplot as plt
from typing_extensions import Self
from pprint import pprint

class EventoTipo(IntEnum):
    Entrada = auto()
    Saida = auto()
    Atendido = auto()

@dataclass
class Evento:
    tipo : EventoTipo
    tempo: float
        
@dataclass
class Cliente:
    chegada: float
    atendido: Optional[float] = None
    saida: Optional[float] = None

# @dataclass
# class Estatisticas:

@dataclass   
class Infectado:
    geracao: int
    filhos: list[Self] = field(default_factory=list)

    def adicionar_filho(self, filho : Self):
        self.filhos.append(filho)
        

    
    
@dataclass
class Servidor:
    lamda: float
    mu: float
    tempo_maximo: float
    arvore : list[Infectado] = field(default_factory=list)
    processados: list[Cliente] = field(default_factory=list)
    
    def proximo_cliente(self, ultimo_cliente: Cliente) -> Cliente:
        chegada = ultimo_cliente.chegada + self.chegada_aleatoria()
        atendido = max(chegada, ultimo_cliente.saida)
        return Cliente(chegada=chegada, atendido=atendido,
                       saida=atendido+self.tempo_de_processamento())
        
    def run(self):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                   saida=self.tempo_de_processamento())
        while atual_cliente.saida < self.tempo_maximo:
            self.processados.append(atual_cliente)
            atual_cliente = self.proximo_cliente(atual_cliente)

    def run_until_empty(self, deterministic=False):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                saida=self.tempo_de_processamento())
        while atual_cliente.saida < self.tempo_maximo:
            self.processados.append(atual_cliente)
            if not (atual_cliente := self.proximo_cliente_ou_vazio(atual_cliente, deterministic=deterministic)):
                return True
        return False

    def run_with_max_clientes_until_empty(self, max_clientes):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                saida=self.tempo_de_processamento())
        clientes_na_fila = 0
        while True:
            self.processados.append(atual_cliente)
            if not (atual_cliente := self.proximo_cliente_ou_vazio(atual_cliente)):
                return True
            if atual_cliente.atendido > atual_cliente.chegada:
                clientes_na_fila += 1
            else:
                clientes_na_fila -= 1
            if clientes_na_fila > max_clientes:
                return False
            prox_cliente = atual_cliente
        

    def proximo_cliente_ou_vazio(self, ultimo_cliente, deterministic=False):
        delta = self.chegada_aleatoria() if deterministic else 1/self.mu
        chegada = ultimo_cliente.chegada + delta
        if chegada < ultimo_cliente.saida:
            atendido = ultimo_cliente.saida
            return Cliente(chegada=chegada, atendido=ultimo_cliente.saida,
                           saida=atendido+self.tempo_de_processamento())
    
    def chegada_aleatoria(self):
        return random.exponential(1/self.lamda)

    def tempo_de_processamento(self):
        return random.exponential(1/self.mu)

    def eventos(self):            
        eventos = []
        
        for cliente in self.processados:
            eventos.append(Evento(EventoTipo.Entrada, cliente.chegada))
            eventos.append(Evento(EventoTipo.Saida, cliente.saida))
            eventos.append(Evento(EventoTipo.Atendido, cliente.atendido))
        return sorted(eventos, key=lambda evento: evento.tempo)
    
    def info_clientes(self):
        na_fila = 0
        curr_time = 0
        waiting_time = 0
        pessoas_area = 0
        cdf_pessoas = []
        for evento in self.eventos():
            pessoas_area += na_fila * (evento.tempo - curr_time)
            cdf_pessoas.append((pessoas_area, evento.tempo))
            curr_time = evento.tempo
            match evento.tipo:
                case EventoTipo.Saida:
                    na_fila -= 1
                case EventoTipo.Entrada:
                    na_fila += 1
        waiting_time = sum(cliente.atendido - cliente.chegada for cliente in self.processados)
        mean_waiting_time = waiting_time / len(self.processados)
        mean_pessoas_area = pessoas_area / self.tempo_maximo
        return mean_pessoas_area, mean_waiting_time, cdf_pessoas
    
    def gera_arvore(self):
        atual_infectado = Infectado(geracao=0,
                                    filhos=[])
        atual_fila = [atual_infectado]
        self.arvore = [atual_infectado]
        eventos_str = ''
        for evento in self.eventos()[1:]:
            match evento.tipo:
                case EventoTipo.Entrada:
                    eventos_str += 'e'
                    novo_infectado = Infectado(geracao=atual_infectado.geracao+1,
                                               filhos=[])
                    self.arvore.append(novo_infectado)
                    atual_infectado.adicionar_filho(novo_infectado)
                    atual_fila.append(novo_infectado)
                case EventoTipo.Saida:
                    eventos_str += 's'
                    if len(atual_fila) == 1:
                        return evento.tempo
                    else:
                        atual_fila = atual_fila[1:]
                        atual_infectado = atual_fila[0]

                    
        

    def info_arvore(self,show=False):
        tamanhos_geracoes = []
        atual_geracao = 0
        tamanho_atual = 0
        max_filhos = 0
        filhos_raiz = len(self.arvore[0].filhos)
        soma_alturas = 0
        for infectado in self.arvore:
            soma_alturas += infectado.geracao
            max_filhos = max(len(infectado.filhos), max_filhos)
            if infectado.geracao == atual_geracao:
                tamanho_atual += 1
            else:
                tamanhos_geracoes.append(tamanho_atual)
                tamanho_atual = 1
        media_alturas = soma_alturas/len(self.arvore)
        if show:
            print(f"filhos da raiz: {filhos_raiz}")
            print(f"max_filhos: {max_filhos}")
            print(f"altura: {self.arvore[-1].geracao}")
            print(f"media_alturas: {media_alturas}")
            print(f"numero de infectados: {len(self.arvore)}")
        return filhos_raiz, max_filhos, self.arvore[-1].geracao, media_alturas, len(self.arvore)
    
    def print_arvore(self, no : Infectado):
        if no.geracao == 20:
            print(f"{no.geracao*' '} filhos: {len(no.filhos)} (filhos omitidos)")
        elif no.filhos == []:
            print(f"{no.geracao*' '} filhos: {len(no.filhos)}")
        else:
            print(f"{no.geracao*' '} filhos: {len(no.filhos)}")
            for filho in no.filhos:
                self.print_arvore(filho)

        


    

        
        
        
    # def plot(self):
    #     [x, y] = list(zip(*points))
    #     fig = plt.figure(figsize=(10, 5))
    #     fila = fig.subplots(1, 1)
    #     fig.suptitle(f'''Fila M/M/1 ($\lambda$={self.lamda}, $\mu$={self.mu})  ($T_{{max}}={self.tempo_maximo}s) (Mean = {mean_persons/self.tempo_maximo:.2f}$)''', fontsize=15)

    #     fila.set_xlabel('Tempo (s)')
    #     fila.set_ylabel('Número de clientes')
    #     fila.bar(x, y, align='edge')
    #     fila.grid(True, axis='y', linestyle='dashed')

    #     plt.show()

def gera_cdfs(lamda, mu, tempo_maximo=100):
    serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
    serv.run()
    _, _, cdf = serv.info_clientes()
    [tempo, pessoas] = list(zip(*cdf))
    fig = plt.figure(figsize=(10, 5))
    
    fig.suptitle(f"M/M/1 ($\\lambda$ = {lamda}, $\\mu$ = {mu})")
    [clientes, espera] = fig.subplots(2, 1)
    clientes.set_title("Cdf do número de clientes")
    clientes.plot(tempo, pessoas)

    x = range(len(serv.processados))
    y = []
    soma = 0
    for cliente in serv.processados:
        soma += cliente.saida - cliente.chegada
        y.append(soma)
    espera.set_title("Cdf do tempo de espera")
    espera.plot(x, y)

    fig.tight_layout()
    plt.savefig(f"m_m_1_queue_lambda_{lamda}_mu_{mu}.png")
    
    
def simula_servidores(lamda, mu, tempo_maximo=100):
    medias = []
    rho = lamda/mu
    for n in range(100):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        serv.run()
        numero_medio_clientes, tempo_medio_espera, _ = serv.info_clientes()
        medias.append((numero_medio_clientes, tempo_medio_espera))
    def media_desvio_padrao(l):
        media = np.mean(l)
        desvio = np.std(l)
        confianca = 1.984 * (desvio / np.sqrt(len(l)))
        return media, desvio, confianca 
    [[c_media, c_desvio_padrao, c_confianca], [e_media, e_desvio_padrao, e_confianca]] = list(map(media_desvio_padrao, zip(*medias)))
    
    print(f"Média de clientes {c_media:.2f} (±{c_confianca:.2f} @ 95%) (teorico: {rho/(1-rho):.2f}), desvio padrão {c_desvio_padrao:.2f}")
    print(f"Tempo médio de espera: {e_media:.2f} (±{e_confianca:.2f} @ 95%) (teorico: {rho / (mu - lamda):.2f}) desvio padrão {e_desvio_padrao:.2f}")

def estima_terminacoes(lamda, mu, tempo_maximo=100):
    terminations = 0
    tries = 10000
    for n in range(tries):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        terminated = serv.run_until_empty()
        if terminated:
            terminations += 1
    print(f"O sistema (lambda={lamda}, mu={mu}) termina {100 * terminations / tries}% das vezes")

def estima_terminacoes_com_max_clientes(lamda, mu, max_clientes, tempo_maximo=100):
    terminations = 0
    tries = 10000
    for n in range(tries):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        terminated = serv.run_with_max_clientes_until_empty(max_clientes)
        if terminated:
            terminations += 1
    print(f"O sistema (lambda={lamda}, mu={mu}, fila_max={max_clientes}) termina {100 * terminations / tries}% das vezes")

def simula_epidemias(lamda, mu, tempo_maximo=100, deterministic=False):
    medias = []
    quantas_parou = 0
    n = 10000
    for _ in range(n):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        parou = serv.run_until_empty(deterministic=deterministic)
        # numero_medio_clientes, tempo_medio_espera, _ = serv.info_clientes()
        ultima_saida = serv.gera_arvore()
        info_arvore = serv.info_arvore()
        #serv.print_arvore(serv.arvore[0])
        medias.append((*info_arvore, ultima_saida))
        if parou:
            quantas_parou += 1
    def media_desvio_padrao(l):
        media = np.mean(l)
        desvio = np.std(l)
        confianca = 1.984 * (desvio / np.sqrt(len(l)))
        return media, desvio, confianca 
    lista_resultados = list(map(media_desvio_padrao, zip(*medias)))
    # filhos_raiz, max_filhos, self.arvore[-1].geracao, media_alturas, len(self.arvore)
    descricoes = ["Grau de saída da raiz: ",
                  "Grau de saída máximo: ",
                  "Altura da árvore: ",
                  "Alturas dos nós da árvore: ",
                  "Número de infectados: ",
                  "Duração do periodo ocupado: "]

    print("------\nResultados (média, desvio, intervalo de confiança):\n------")
    for descricao, resultado in zip(descricoes, lista_resultados):
        prefix = "\item "
        resultado_str = f"média ${round(resultado[0], 3)}$, desvio ${round(resultado[1], 3)}$, intervalo de confiança $\pm {round(resultado[2], 3)}$"
        print(prefix, descricao, resultado_str)

    print("\item Fração de filas finitas: $" + str(round(quantas_parou/n, 3) * 100) + "\%$")

    
    
    
if __name__ == "__main__":
    print("\nCaso 1:")
    simula_epidemias(lamda=1, mu=2, tempo_maximo=1000)
    print("\nCaso 1 (determinístico):")
    simula_epidemias(lamda=1, mu=2, tempo_maximo=1000, deterministic=True)
    print("\nCaso 2:")
    simula_epidemias(lamda=2, mu=4, tempo_maximo=1000)
    print("\nCaso 2 (determinístico):")
    simula_epidemias(lamda=2, mu=4, tempo_maximo=1000, deterministic=True)
    print("\nCaso 3:")
    simula_epidemias(lamda=1.05, mu=1, tempo_maximo=1000)
    print("\nCaso 3 (determinístico):")
    simula_epidemias(lamda=1.05, mu=1, tempo_maximo=1000, deterministic=True)
    print("\nCaso 4:")
    simula_epidemias(lamda=1.1, mu=1, tempo_maximo=1000)
    print("\nCaso 4 (determinístico):")
    simula_epidemias(lamda=1.1, mu=1, tempo_maximo=1000, deterministic=True)


    '''
    gera_cdfs(lamda=1, mu=2)
    gera_cdfs(lamda=2, mu=4)
    estima_terminacoes(lamda=2,    mu=4)
    estima_terminacoes(lamda=1,    mu=2)
    estima_terminacoes(lamda=1.05, mu=1, tempo_maximo=10000)
    estima_terminacoes(lamda=1.10, mu=1, tempo_maximo=10000)
    estima_terminacoes_com_max_clientes(lamda=1.05, mu=1, max_clientes=1000)
    estima_terminacoes_com_max_clientes(lamda=1.1, mu=1, max_clientes=1000)
    estima_terminacoes_com_max_clientes(lamda=1, mu=2, max_clientes=1000)
    estima_terminacoes_com_max_clientes(lamda=2, mu=4, max_clientes=1000)
    '''
