
# WeatherEmailScraper

Uma aplicação automatizada desenvolvida em Python que utiliza Selenium para buscar a previsão do tempo no site AccuWeather e enviar
essas informações diretamente para o seu e-mail. Ideal para quem deseja receber atualizações diárias sobre as condições
meteorológicas de uma cidade específica de forma conveniente e sem esforço manual.

## Funcionalidades

- Obtenção de Dados: Utiliza Selenium para acessar o site do AccuWeather, inserir a cidade e extrair temperatura atual, condição do tempo e previsão para os próximos 3 dias.
- Envio por E-mail: Formata os dados obtidos em um e-mail HTML e envia para um destinatário configurado.
- Agendamento: Utiliza a biblioteca schedule para agendar a execução diária do script.

## Requisitos

- Python 3.x

## Configuração

1. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o script para testar o envio de e-mails:
   ```bash
   python app.py
   ```

## Notas

Certifique-se de que o Chrome WebDriver está instalado e configurado corretamente.
