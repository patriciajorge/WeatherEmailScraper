from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import schedule
from datetime import datetime

load_dotenv()

def iniciar_driver():
    chrome_options = Options()
    arguments = ['--lang=pt-BR', '--window-size=1300,1000', '--incognito']
    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1,
    })
    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=1,
        ignored_exceptions=[NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException]
    )
    return driver, wait

def obter_previsao(driver, wait, cidade):
    # Entrar no site do AccuWeather
    print('Entrando no site AccuWeather')
    driver.get('https://www.accuweather.com/')
    sleep(3)

    # Procurar pelo campo de cidade
    print('Digitando a cidade de preferência')
    campo_cidade = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='search-input']")))
    campo_cidade.send_keys(cidade)
    sleep(3)
    campo_cidade.send_keys(Keys.ENTER)
    sleep(3)

    # Rolar a página para baixo
    driver.execute_script("window.scrollTo(0, 300);")
    sleep(3)

    # Extrair a temperatura e condição do tempo
    try:
        print('Pegando as informações sobre a previsão do tempo')
        temperatura_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='temp-container']//div[@class='temp']")))
        condicaotempo_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='phrase']")))
        temperatura_atual = temperatura_element.text
        condicaotempo = condicaotempo_element.text

        driver.execute_script("window.scrollTo(0, 1600);")
        sleep(3)

        # Extrair a previsão do tempo dos próximos 3 dias
        previsoes_proximo_3_dias = []
        for i in range(2, 5):
            dia_xpath = f"//a[@class='daily-list-item '][{i}]/div/p"
            temp_max_xpath = f"//a[@class='daily-list-item '][{i}]//span[@class='temp-hi']"
            temp_min_xpath = f"//a[@class='daily-list-item '][{i}]//span[@class='temp-lo']"

            dia_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, dia_xpath)))
            dia_texts = [dia.text for dia in dia_elements]
            
            temp_max_element = wait.until(EC.presence_of_element_located((By.XPATH, temp_max_xpath)))
            temp_min_element = wait.until(EC.presence_of_element_located((By.XPATH, temp_min_xpath)))
            
            temp_max = temp_max_element.text
            temp_lo = temp_min_element.text
            
            temperatura_proximos_dias = f"Temperatura Máxima: {temp_max}, Temperatura Mínima: {temp_lo}"
            dia_texts.append(temperatura_proximos_dias)
            previsoes_proximo_3_dias.append(dia_texts)

        return temperatura_atual, condicaotempo, previsoes_proximo_3_dias

    except NoSuchElementException:
        print("Elemento não encontrado")
        return None
    finally:
        sleep(3)
        driver.quit()

# previsões para os próximos 3 dias
def format_previsoes(previsoes):
    formatted_previsoes = ''
    for idx, previsao in enumerate(previsoes):
        formatted_previsoes += '''
        <div class="day">
            <h3>Dia {idx}:</h3>
            <p>{texto}</p>
        </div>
        '''.format(idx=idx+1, texto='<br>'.join(previsao))
    return formatted_previsoes

def enviar_email(destinatario, cidade, temperatura, condicaotempo, previsoes):
    print('Criando o email com essas informações')
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("Variáveis de ambiente EMAIL_ADDRESS e EMAIL_PASSWORD não foram definidas")

    mail = EmailMessage()
    mail['Subject'] = 'Previsão do tempo'

    # Montando a mensagem HTML com formatação
    mensagem = f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Previsão do Tempo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
                max-width: 600px;
                margin: auto;
                position: relative;
                min-height: 100vh;
            }}
            h1 {{
                color: #1a73e8;
            }}
            .forecast {{
                margin-top: 20px;
            }}
            .day {{
                margin-bottom: 15px;
            }}
            .footer {{
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                text-align: center;
                width: 100%;
            }}
            .footer .content-block {{
                font-size: 12px;
                color: #999;
            }}
            .footer .content-block a {{
                color: #999;
                text-decoration: none;
            }}
            .footer .powered-by {{
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Previsão do Tempo para {cidade}</h1>
            <p>Temperatura: {temperatura}</p>
            <p>Condição: {condicaotempo}</p>
            <div class="forecast">
                <h2>Previsão para os próximos 3 dias:</h2>
                {format_previsoes(previsoes)}
            </div>
        </div>
        <!-- START FOOTER -->
        <div class="footer">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center">
                <tr>
                    <td class="content-block">
                        <span class="apple-link">Vamos automatizar tudo!</span>
                    </td>
                </tr>
                <tr>
                    <td class="content-block powered-by">
                        Desenvolvido por <a href="https://github.com/patriciajorge">Patrícia Jorge</a>.
                    </td>
                </tr>
            </table>
        </div>
        <!-- END FOOTER -->
    </body>
    </html>
    '''

    mail['From'] = EMAIL_ADDRESS
    mail['To'] = destinatario
    mail.add_header('Content-Type', 'text/html')
    mail.set_payload(mensagem.encode('utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(mail)
        print('Email enviado com sucesso!')

def iniciar_automacao():
    driver, wait = iniciar_driver()
    cidade = 'Campinas, São Paulo'
    temperatura, condicaotempo, previsoes = obter_previsao(driver, wait, cidade)

    if temperatura and condicaotempo and previsoes:
        destinatario = 'patriciajorge011@gmail.com'
        enviar_email(destinatario, cidade, temperatura, condicaotempo, previsoes)
    else:
        print("Não foi possível obter a previsão do tempo.")

def agendar_email():
    # Schedule para executar todos os dias às 08:00
    schedule.every().day.at('12:54').do(iniciar_automacao)
    

if __name__ == "__main__":
    print('Iniciando automação...')
    load_dotenv()    

    # Agendar o envio diário
    agendar_email()

    while True:
        schedule.run_pending()
        sleep(1)