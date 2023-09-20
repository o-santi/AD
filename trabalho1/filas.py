from dataclasses import dataclass
from typing import Optional

@dataclass
class Cliente:
    chegada: float
    saida: Optional[float]
    
@dataclass
class Servidor:
    fila_de_clientes: list[Cliente] = []
    clientes_processados: list[Cliente] = []
    lamda: float
    mu: float

    tempo_maximo: float
    
    def run(self):
        tempo_atual = 0
        ultima_chegada = 0
        while tempo_atual < self.tempo_maximo:
            while ultima_chegada <= tempo_atual:
                self.fila_de_clientes.push(Cliente(chegada=ultima_chegada))
                ultima_chegada += self.chegada_aleatoria()
            while (cliente := self.fila_de_clientes.pop(0)):
                tempo_atual += self.tempo_de_processamento()
                cliente.saida = tempo_atual
                self.clientes_processados.push(cliente)

                
    def chegada_aleatoria(self):
        return 1.0 # TODO: this

    def tempo_de_processamento(self):
        return 1.0 # TODO: this
                    
if __name__ == "__main__":
    fila1 = Servidor(lamda=2, mu=4, tempo_maximo=10000)
    fila2 = Servidor(lamda=2, mu=4, tempo_maximo=10000)
    
            
