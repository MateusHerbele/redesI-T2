# RedesI-T2
Implementação de uma rede em anel que possibilite jogar F*da-se (o nome do jogo é esse mesmo)

# O JOGO: # Regras do Jogo de Cartas

## Setup Inicial

1. **Vidas dos Jogadores:**
   - Cada jogador começa com 7 vidas.

2. **Embaralhamento e Distribuição:**
   - O carteador embaralha as cartas no início de cada rodada.
   - As cartas são distribuídas começando pelo jogador à esquerda do carteador.
   - O número de cartas por jogador é igual ao número da rodada atual.

3. **Palpites Iniciais:**
   - O carteador faz o primeiro palpite após a distribuição das cartas.
   - O jogador seguinte ao carteador faz o primeiro palpite subsequente.

4. **Carta do Vira:**
   - Na primeira rodada, a carta do vira é mantida virada para baixo até que todos façam seus palpites.
   - Em rodadas subsequentes, a carta do vira é colocada virada para cima antes do primeiro palpite.

## Dinâmica do Jogo

5. **Manilhas:**
   - A carta seguinte na ordem de força ao "vira" determina as manilhas.
   - As manilhas são as cartas de maior força na rodada.

6. **Força das Cartas:**
   - A ordem crescente de força das cartas é: 4, 5, 6, 7, Q, J, K, A, 2, 3.
   - A ordem crescente de força dos naipes é: ♦, ♣️, ♥, ♠️.

7. **Sub-rodadas:**
   - Cada jogador pode fazer um palpite do número de sub-rodadas que acredita que vencerá, de 0 até o número da rodada atual.
   - O palpite do carteador não pode resultar na soma igual ao número da rodada com os palpites dos outros jogadores.

8. **Jogabilidade:**
   - Um jogador vence uma sub-rodada se tiver a carta não embuchada mais forte na mesa após todos jogarem.
   - Se dois jogadores jogarem cartas do mesmo valor (não manilhas), as cartas "embucham" e não têm mais valor.
   - Se dois jogadores jogarem manilhas do mesmo valor, a carta mais forte é determinada pelo naipe.

## Fim da Rodada

9. **Resultado dos Palpites:**
   - Os jogadores que acertam seus palpites não perdem vidas.
   - Os jogadores que erram perdem vidas de acordo com a diferença absoluta entre seu palpite e o número de sub-rodadas vencidas.

10. **Atualização e Continuidade:**
    - Após o fim de uma rodada, o carteador muda para o próximo jogador na ordem.
    - A rodada seguinte tem um número maior de cartas distribuídas, conforme o número de jogadores vivos.

11. **Eliminação e Fim do Jogo:**
    - Um jogador é eliminado se suas vidas forem menores que 1 após uma rodada.
    - O jogo continua até restar apenas um jogador com vidas positivas.
    - Se todos os jogadores forem eliminados, o jogador com o maior número de vidas, mesmo negativo, vence. Em caso de empate nesse critério, todos perdem.

12. **Limite de Cartas:**
    - O número máximo de cartas por jogador é determinado pelo número de jogadores vivos.

