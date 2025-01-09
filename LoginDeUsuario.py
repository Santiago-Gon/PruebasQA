import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import unittest

# Configuración del logging para generar un archivo de informes
logging.basicConfig(filename='test_report.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

class InlazeLoginTests(unittest.TestCase):
    """Clase para pruebas automatizadas en la página de inicio de sesión de Inlaze."""

    @classmethod
    def setUpClass(cls):
        """Configuración inicial del entorno de pruebas."""
        logging.info("Iniciando pruebas...")
        # Configuración del driver con ChromeDriverManager
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """Cierre del driver después de todas las pruebas."""
        cls.driver.quit()
        logging.info("Pruebas completadas.")

    def login(self, username, password):
        """Método auxiliar para realizar el login y registrar el tiempo de ejecución."""
        start_time = time.time()  # Tiempo de inicio
        logging.info("Iniciando sesión con el usuario: %s", username)

        self.driver.find_element(By.ID, "email").send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, "input.input.input-bordered.join-item.w-full").send_keys(password)
        self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-in/main/section[1]/app-sign-in-form/form/button").click()

        elapsed_time = time.time() - start_time  # Tiempo de ejecución
        logging.info("Tiempo de ejecución del login: %.2f segundos", elapsed_time)

    def test_incomplete_login_form(self):
        """Valida que el formulario no se envíe si los campos no están completos."""
        logging.info("Iniciando la prueba: test_incomplete_login_form")
        url = "https://test-qa.inlaze.com/auth/sign-in"
        self.driver.get(url)
        logging.info(f"Accediendo a la URL: {url}")

        try:
            # Solo enviar email y presionar el botón
            username_field = self.driver.find_element(By.ID, "email")
            username_field.send_keys("CorreoPrueba@prueba.com")
            logging.info("Solo excribir email, realizado correctamente.")

            login_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-in/main/section[1]/app-sign-in-form/form/button")
            logging.info("Botón de inicio de sesión localizado exitosamente.")
            

            login_button.click()
            logging.info("Se intentó hacer clic en el botón de inicio de sesión con campos incompletos.")
            
            time.sleep(2)  # Esperar un momento para confirmar
            
            # Verificar que la URL no haya cambiado
            self.assertEqual(self.driver.current_url, url, "El formulario se envió aunque los campos no estaban completos.")
            logging.info("El formulario no se envió. La prueba fue exitosa.")        
              
        except WebDriverException as e:
            if "is not clickable at point" in str(e):
                logging.warning("El botón de inicio de sesión no es clickeable. Prueba exitosa.")
                self.assertTrue(True, "El botón de inicio de sesión no es clickeable, prueba exitosa.")
            else:
                logging.error(f"Excepción inesperada: {str(e)}")
                raise

        logging.info("Prueba completada: test_incomplete_login_form")

    def test_login_form_elements(self):
        """Verifica que los elementos del formulario de inicio de sesión estén presentes."""
        start_time = time.time()
        url = "https://test-qa.inlaze.com/auth/sign-in"
        self.driver.get(url)
        logging.info("Verificando los elementos del formulario de inicio de sesión...")

        try:
            username_field = self.driver.find_element(By.ID, "email")
            self.assertTrue(username_field.is_displayed(), "El campo de correo electrónico no está visible en la página.")
            logging.info("Campo de correo electrónico visible.")
        except NoSuchElementException:
            self.fail("El campo de correo electrónico no se encontró en la página.")

        try:
            password_field = self.driver.find_element(By.ID, "password")
            self.assertTrue(password_field.is_displayed(), "El campo de contraseña no está visible en la página.")
            logging.info("Campo de contraseña visible.")
        except NoSuchElementException:
            self.fail("El campo de contraseña no se encontró en la página.")

        try:
            login_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-in/main/section[1]/app-sign-in-form/form/button")
            self.assertTrue(login_button.is_displayed(), "El botón de inicio de sesión no está visible en la página.")
            logging.info("Botón de inicio de sesión visible.")
        except NoSuchElementException:
            self.fail("El botón de inicio de sesión no se encontró en la página.")
        
        elapsed_time = time.time() - start_time
        logging.info("Tiempo de ejecución de test_login_form_elements: %.2f segundos", elapsed_time)

    def test_successful_login(self):
        """Verifica que el usuario pueda iniciar sesión con email y contraseña correctos."""
        start_time = time.time()
        url = "https://test-qa.inlaze.com/auth/sign-in"
        self.driver.get(url)

        # Ingresar credenciales correctas
        self.login("eversantiago07@hotmail.com", "Santiagogon#2")

        # Esperar a que el dashboard se cargue
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-panel-root/app-navbar/div/div[2]/div/div/h2"))
        )
        # Validar redirección al dashboard
        self.assertIn("panel", self.driver.current_url, "El usuario no fue redirigido al dashboard tras iniciar sesión.")
        
        elapsed_time = time.time() - start_time
        logging.info("Tiempo de ejecución de test_successful_login: %.2f segundos", elapsed_time)

    def test_display_user_name(self):
        """Verifica que el nombre del usuario se muestre correctamente tras iniciar sesión."""
        start_time = time.time()
        url = "https://test-qa.inlaze.com/auth/sign-in"
        self.driver.get(url)

        # Ingresar credenciales correctas
        self.login("eversantiago07@hotmail.com", "Santiagogon#2")

        # Esperar a que el nombre del usuario aparezca en la página
        try:
            # Esperar que el elemento con la clase "font-bold" esté visible
            user_name_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/app-panel-root/app-navbar/div/div[2]/div/div/h2"))
            )
            # Verificar que el texto del elemento contiene el nombre del usuario
            self.assertTrue(user_name_element.text.strip() != "", "El nombre del usuario no se muestra correctamente.")
            logging.info("Nombre del usuario visible.")
        except TimeoutException:
            self.fail("El nombre del usuario no se mostró después de iniciar sesión.")
        
        elapsed_time = time.time() - start_time
        logging.info("Tiempo de ejecución de test_display_user_name: %.2f segundos", elapsed_time)

    def test_logout(self):
        """Verifica que el usuario pueda cerrar sesión correctamente."""
        start_time = time.time()
        url = "https://test-qa.inlaze.com/auth/sign-in"
        self.driver.get(url)

        # Ingresar credenciales correctas
        self.login("eversantiago07@hotmail.com", "Santiagogon#2")

        # Esperar a que el nombre de usuario esté visible para confirmar el inicio de sesión
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/app-panel-root/app-navbar/div/div[2]/div/div/h2"))
        )

        # Realizar clic en el botón de perfil (primero en el menú)
        profile_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-panel-root/app-navbar/div/div[2]/div/div/label")
        profile_button.click()

        # Esperar un momento para que se despliegue el menú
        time.sleep(2)

        # Realizar clic en el enlace de cerrar sesión
        logout_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-panel-root/app-navbar/div/div[2]/div/ul/li[3]/a")
        logout_button.click()

        # Esperar a que se redirija a la página de inicio de sesión
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be("https://test-qa.inlaze.com/auth/sign-in")
        )

        # Verificar que la URL sea la de inicio de sesión, lo que indica que se cerró la sesión
        self.assertEqual(self.driver.current_url, "https://test-qa.inlaze.com/auth/sign-in", "No se cerró la sesión correctamente.")
        
        elapsed_time = time.time() - start_time
        logging.info("Tiempo de ejecución de test_logout: %.2f segundos", elapsed_time)

if __name__ == "__main__":
    unittest.main()
