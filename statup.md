# Esteira Agêntica de IA

Esteira de desenvolvimento mult agente automatizada

## Estado atual

Hoje tenho uma estrutura robusta de esteira de desenvolvimento de IA que simulam agentes de Produto, Analista de requisitos, Analista de UX, Arquiteto, Qualidade, Engenharia e etc.

Porém o acionamento dos agentes é a manual, tornando o usuário o tanto o gerenciador de tarefas quanto o orquestrador, sendo o humano um gargalo.

## Objetivos

Criar uma esteira agentica automatizada que:

1. Utilize um sistema de gestão de tarefas para organizar as features, bugs, milestones, story e ou qualquer nome de organização, sendo em Kanban, Scrum, lean, cascata ou qualquer metodologia que o usuário queira adotar;

2. Integre com git, seja github, gitlab, git local e qualquer repositório que o usuário queira configurar, inicialmente github

3. Usar IA CLI para execução das etapas em papeis bem definidos

4. Ser capaz de capturar metricas de tempo de execução, custo em tokens, retrabalho, delírios de IA e outros.

5. usaremos o kiro cli como agente de ia

6. O usuário precisa aprovar todas as estapas

7. o sistema precisa seguir se configurado um gitflow específico.

## Objetivos futuros

1. Integração via e-mail e chats para integração com o usuário (humano)

2. permitir outros agentes de ia

3. permitir a integração com ferramentas pagas

## Limites

1. Inicialmente as ferramentas escolhidas precisam ser gratuitas;

2. o sitema deve rodar em uma máquina qualquer e todo contato com o humano precisa ser remota via board, email, chats e etc, exceto na configuração inicial ou em esporádicas manutenções, o usuário nunca deve precisar interagir com os sistemas da esteira diretamente.