# PASSCOM: Venda Compartilhada de Passagens

## Introdução

Este projeto discute a criação de um sistema de comercialização de bilhetes aéreos que se conecta entre diversas empresas aéreas. Cada empresa tem um servidor dedicado para consultas e reservas de rotas aéreas, permitindo a partilha de rotas com empresas parceiras. O principal desafio foi estabelecer uma solução que possibilitasse ao cliente, de qualquer servidor, reservar bilhetes em outras empresas, mantendo a sequência e preferência dos trechos escolhidos. Além disso, era necessário assegurar uma estrutura descentralizada, onde a falha de um servidor não prejudicasse o funcionamento dos demais.

O aplicativo foi criado com o uso do FastAPI para a criação de APIs REST. Foi aplicada uma solução de bloqueio local para administrar a concorrência e a ordem das solicitações entre diversos servidores.


## Metodologia Utilizada
Na implementação do sistema de vendas de passagens, o FastAPI foi escolhido como framework principal para criar APIs REST baseadas em HTTP, dada sua simplicidade e alto desempenho. Esse framework é ideal para lidar com múltiplas requisições simultâneas, o que é essencial em um sistema de reservas com alta concorrência.

Utilizando o HTTP como protocolo de comunicação, os clientes interagem com os servidores por meio de requisições REST, possibilitando que cada operação — como consulta, reserva ou cancelamento — seja facilmente identificada e gerenciada no servidor através dos métodos HTTP:

GET: para verificar a disponibilidade dos trechos de voos e acessar informações de uma rota específica.
POST: para realizar a reserva de um trecho de voo. As APIs dos servidores se comunicam seguindo a arquitetura REST, permitindo que consultas e reservas sejam processadas de forma descentralizada, isolando operações entre servidores conveniados. Cada trecho de voo é registrado em um arquivo JSON, que é atualizado conforme novas reservas são efetuadas, mantendo assim a persistência de dados.

### Bloqueio Local para Concorrência

Para garantir a concorrência entre os servidores e evitar a venda simultânea do mesmo trecho de voo, foi implementado um bloqueio local utilizando a biblioteca asyncio do Python. Quando um servidor recebe uma requisição de compra de passagem, ele adquire um lock local para o trecho específico. Isso impede que outros servidores ou processos concorrentes realizem a mesma venda enquanto o lock está ativo.

A utilização do bloqueio local proporciona uma abordagem eficiente de controle de concorrência, onde o lock é isolado a cada servidor, garantindo que a venda de um trecho seja exclusiva durante o processo de reserva. Após a conclusão da transação, o lock é liberado, permitindo que outro cliente ou servidor realize a venda do trecho posteriormente.

### Implementação dos Testes
Os testes foram realizados de forma básica, utilizando o Swagger UI para validação das principais funcionalidades e endpoints. Não foram implementados testes consistentes para simular condições de alta concorrência ou falhas de servidores, limitando a verificação da aplicação quanto à confiabilidade e robustez sob esses cenários. Contudo, a solução de bloqueio local foi validada em testes unitários, demonstrando a eficiência do mecanismo de concorrência entre servidores.

## Discussão e Resultados
Durante a execução, o sistema atendeu parcialmente aos requisitos de descentralização e concorrência. O sistema implementa o compartilhamento de trechos entre companhias, garantindo que, em caso de queda de um servidor, as demais companhias não são diretamente impactadas, mantendo a operabilidade para os clientes conectados nos servidores ativos. Entretanto, isso gera uma limitação em relação ao acesso aos dados do servidor que caiu, o que compromete a experiência do usuário em casos de falhas.

### Consistência e Confiabilidade:
O sistema possui uma solução mais robusta para garantir a concorrência e a integridade das transações, utilizando bloqueios locais para controlar o acesso simultâneo aos trechos de voo. Com isso, conseguimos evitar a venda simultânea de trechos em servidores diferentes. Entretanto, o sistema ainda não atende totalmente os requisitos de confiabilidade. Atualmente, uma compra em andamento não é recuperada se o servidor onde o cliente iniciou a requisição cair e reiniciar. Não há um mecanismo que armazene o estado da transação de forma persistente para recuperação posterior. Isso representa uma limitação relevante em termos de experiência do cliente e continuidade das transações.

### Concorrência e Preferência:
A preferência dos trechos é garantida entre os servidores conectados, e a concorrência é controlada pelo bloqueio local, onde a função asyncio.Lock() assegura que apenas um cliente possa realizar a venda de um trecho. Esse controle impede que diferentes servidores vendam a mesma passagem para clientes distintos. Contudo, em cenários de queda de servidores, o sistema pode apresentar dificuldades para finalizar a venda, pois os locks podem não ser liberados corretamente se o servidor cair antes de completar a transação.

## Conclusão
O projeto de venda de passagens entre diferentes servidores de companhias aéreas foi bem-sucedido em criar uma base descentralizada e uma experiência de reserva com concorrência controlada por meio de bloqueios locais. A solução de bloqueio local melhorou a confiabilidade e a integridade das transações, evitando a venda simultânea de passagens. No entanto, o sistema ainda apresenta limitações de confiabilidade, especialmente em relação à persistência do estado das transações em caso de falhas de servidor.

O uso do bloqueio local para controlar o acesso aos trechos de voo durante o processo de venda foi uma escolha eficiente, mas a solução de recuperação de transações em caso de falhas ainda precisa ser implementada para garantir uma experiência de usuário mais confiável e contínua. Além disso, o sistema de compartilhamento de dados entre servidores foi bem-sucedido, mas sua dependência de servidores ativos pode prejudicar a experiência do cliente em cenários de falha.
