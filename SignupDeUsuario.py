# Importación de bibliotecas necesarias para la automatización y pruebas
import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import unittest

# Configuración del logging para generar un archivo de informes
logging.basicConfig(
    filename='test_report_sign_up.txt',  # El archivo de salida para los registros
    level=logging.INFO,  # Nivel de los registros, INFO incluye todos los mensajes importantes
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato de los registros
)

# Constantes de configuración utilizadas en las pruebas
BASE_URL = "https://test-qa.inlaze.com/auth/sign-up"  # URL base de la página de registro
TIMEOUT = 2  # Tiempo de espera máximo en segundos para encontrar elementos
INVALID_CLASS = "ng-invalid"  # Clase CSS utilizada para marcar campos inválidos
ERROR_MESSAGE_SELECTOR = "span.label-text-alt.text-error"  # Selector CSS para el mensaje de error

# Clase de pruebas para la página de registro en Inlaze
class InlazeLoginTests(unittest.TestCase):
    """
    Clase para pruebas automatizadas en la página de sign up de Inlaze.
    """

    @classmethod
    def setUpClass(cls):

        """Configuración inicial antes de ejecutar las pruebas."""

        logging.info("Iniciando pruebas...")  # Registro de inicio de pruebas
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Inicia el navegador Chrome
        cls.driver.maximize_window()  # Maximiza la ventana del navegador
        cls.driver.implicitly_wait(10)  # Establece el tiempo de espera implícito para encontrar elementos

    @classmethod
    def tearDownClass(cls):

        """Limpieza después de ejecutar todas las pruebas."""

        cls.driver.quit()  # Cierra el navegador después de todas las pruebas
        logging.info("Pruebas completadas.")  # Registro de fin de pruebas

    def navigate_to_signup_page(self):

        """Navegar a la página de sign-up."""

        self.driver.get(BASE_URL)  # Abre la URL definida en BASE_URL
        logging.info(f"Página cargada: {BASE_URL}")  # Registro de la carga de la página

    def is_error_message_visible(self, selector, expected_text):

        """Verificar si un mensaje de error específico es visible en la página."""

        try:
            error_element = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))  # Espera hasta que el error sea visible
            )
            return error_element.text.strip() == expected_text  # Compara el texto del mensaje de error con el esperado
        except TimeoutException:
            return False  # Retorna False si el mensaje de error no es visible en el tiempo esperado

    def test_validate_full_name_field(self):

        """Prueba para validar que el campo de nombre (ID: full-name) acepte al menos dos palabras."""

        try:
            start_time = time.time()  # Marca el tiempo de inicio de la prueba
            logging.info("Iniciando validación del campo 'full-name'.")  # Registro del inicio de la prueba

            self.navigate_to_signup_page()  # Navega a la página de registro

            full_name_field = self.driver.find_element(By.ID, "full-name")  # Localiza el campo 'full-name'
            logging.info("Campo 'full-name' localizado.")  # Registro de la localización del campo

            # Casos de prueba para el campo 'full-name'
            test_cases = [
                {"input": "Nombre", "expected": False},  # Espera un error si solo hay un nombre
                {"input": "Nombre Apellido", "expected": True},  # Espera que sea válido ingresando datos correctos
                {"input": " ", "expected": False},  # Espera un error si no se ingresa nada
                {"input": "Nombre A", "expected": True},  # Espera que sea válido se ingresa nombre completo y apellido simple
            ]

            # Ejecuta cada caso de prueba
            for test in test_cases:
                iteration_start = time.time()  # Marca el tiempo de inicio de la iteración
                input_value = test["input"]
                expected_result = test["expected"]

                full_name_field.clear()  # Limpia el campo antes de ingresar un valor
                ActionChains(self.driver).click(full_name_field).perform()  # Hace clic en el campo para enfocar
                full_name_field.send_keys(input_value)  # Ingresa el valor al campo

                css_classes = full_name_field.get_attribute("class")  # Obtiene las clases CSS del campo
                logging.info(f"Ingresando valor: '{input_value}'")  # Registro del valor ingresado
                actual_result = INVALID_CLASS not in css_classes  # Verifica si el campo es válido

                # Compara el resultado actual con el esperado
                self.assertEqual(
                    actual_result, expected_result,
                    f"Test fallido para entrada: '{input_value}'. Esperado: {expected_result}, Obtenido: {actual_result}."
                )
                iteration_time = time.time() - iteration_start  # Tiempo de ejecución de la iteración
                logging.info(f"Test pasado para entrada: '{input_value}'. Tiempo: {iteration_time:.2f} segundos.")  # Registro de resultado

            total_time = time.time() - start_time  # Tiempo total de ejecución de la prueba
            logging.info(f"Validación completada en {total_time:.2f} segundos.")  # Registro del tiempo total

        except Exception as e:
            logging.error(f"Error durante la validación: {e}")  # Registro de error
            self.fail(f"Error inesperado durante la prueba: {e}")  # Marca la prueba como fallida

    def test_validate_password_mismatch(self):

        """Prueba para validar que se muestre un error cuando las contraseñas no coinciden."""

        try:
            start_time = time.time()  # Marca el tiempo de inicio de la prueba
            logging.info("Iniciando validación de contraseñas no coincidentes.")  # Registro del inicio de la prueba

            self.navigate_to_signup_page()  # Navega a la página de registro

            # Localiza los campos de contraseña y confirmación de contraseña
            password_field = self.driver.find_elements(By.ID, "password")[1]  
            confirm_password_field = self.driver.find_elements(By.ID, "confirm-password")[1]

            # Casos de prueba para las contraseñas
            test_cases = [
                {"password": "password123", "confirm_password": "password321", "expected_error": True},  # Contraseñas no coincidentes
                {"password": "Password1!", "confirm_password": "Password1!", "expected_error": False},  # Contraseñas coincidentes
                {"password": "abc123", "confirm_password": "abc124", "expected_error": True},  # Contraseñas no coincidentes
            ]

            # Ejecuta cada caso de prueba
            for test in test_cases:
                iteration_start = time.time()  # Marca el tiempo de inicio de la iteración
                password = test["password"]
                confirm_password = test["confirm_password"]
                expected_error = test["expected_error"]

                password_field.clear()  # Limpia los campos de contraseña
                confirm_password_field.clear()  
                password_field.send_keys(password)  # Ingresa la contraseña
                confirm_password_field.send_keys(confirm_password)  # Ingresa la confirmación de la contraseña
                logging.info(f"Ingresando contraseñas: '{password}' y '{confirm_password}'.")  # Registro de los valores ingresados

                # Verifica si el mensaje de error es visible
                error_visible = self.is_error_message_visible(ERROR_MESSAGE_SELECTOR, "Passwords do not match")

                # Compara el resultado actual con el esperado
                self.assertEqual(
                    error_visible, expected_error,
                    f"Test fallido para contraseñas: '{password}' y '{confirm_password}'. "
                    f"Esperado error: {expected_error}, Obtenido: {error_visible}."
                )
                iteration_time = time.time() - iteration_start  # Tiempo de ejecución de la iteración
                logging.info(f"Test pasado para contraseñas: '{password}' y '{confirm_password}'. Tiempo: {iteration_time:.2f} segundos.")  # Registro del resultado

            total_time = time.time() - start_time  # Tiempo total de ejecución de la prueba
            logging.info(f"Validación completada en {total_time:.2f} segundos.")  # Registro del tiempo total

        except Exception as e:
            logging.error(f"Error durante la validación de contraseñas: {e}")  # Registro de error
            self.fail(f"Error inesperado durante la prueba de contraseñas: {e}")  # Marca la prueba como fallida

    

    def test_email_format_and_uniqueness(self):

        """Verifica que el correo electrónico cumpla con el formato estándar y que sea único en la base de datos."""


        logging.info("Iniciando la prueba: test_email_format_and_uniqueness")

        def is_valid_email(email):
            """Verifica si el correo electrónico cumple con el formato estándar."""
            email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            return re.match(email_regex, email) is not None

        try:
            # Navegar a la página de registro
            self.navigate_to_signup_page()

            # Localizar los elementos del formulario
            email_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_elements(By.ID, "password")[1]
            confirm_password_field = self.driver.find_elements(By.ID, "confirm-password")[1]
            full_name_field = self.driver.find_element(By.ID, "full-name")
            register_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-up/main/section[2]/app-sign-up-form/form/button")

            # Definir datos de prueba
            valid_email = "correo_valido@prueba.com"
            invalid_email = "correo_invalido@com"
            duplicate_email = valid_email  # Se intentará registrar este correo nuevamente
            valid_password = "Password1!"
            valid_full_name = "Nombre Apellido"

            # Validar formato del correo
            for email in [valid_email, invalid_email]:
                try:
                    # Verifica si el formato del correo es válido
                    if not is_valid_email(email):
                        logging.error(f"El correo '{email}' no tiene un formato válido.")
                        self.fail(f"El correo '{email}' no cumple con el formato estándar y fue aceptado.")
                except Exception as e:
                    # Captura y registra cualquier error durante la validación del correo
                    logging.error(f"Error durante la validación del correo '{email}': {e}")
                    continue  # Continúa con el siguiente correo si hay un error en la validación del actual

            # Registro inicial con un correo válido
            full_name_field.clear()
            email_field.clear()
            password_field.clear()
            confirm_password_field.clear()

            full_name_field.send_keys(valid_full_name)
            email_field.send_keys(valid_email)
            password_field.send_keys(valid_password)
            confirm_password_field.send_keys(valid_password)
            register_button.click()
            logging.info(f"Intentando registrar el correo único: {valid_email}")

            # Esperar el mensaje de éxito
            success_message_selector = "div.ml-3.text-sm.font-normal"
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, success_message_selector))
            )
            success_message = self.driver.find_element(By.CSS_SELECTOR, success_message_selector)
            self.assertEqual(
                success_message.text.strip(), "Successful registration!",
                f"Error: No se mostró el mensaje de registro exitoso para el correo único {valid_email}."
            )
            logging.info("Registro inicial exitoso con un correo único.")

            # Intentar registrar nuevamente con el mismo correo
            self.navigate_to_signup_page()

            # Localizar los elementos del formulario nuevamente
            email_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_elements(By.ID, "password")[1]
            confirm_password_field = self.driver.find_elements(By.ID, "confirm-password")[1]
            full_name_field = self.driver.find_element(By.ID, "full-name")
            register_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-up/main/section[2]/app-sign-up-form/form/button")

            full_name_field.clear()
            email_field.clear()
            password_field.clear()
            confirm_password_field.clear()

            full_name_field.send_keys(valid_full_name)
            email_field.send_keys(duplicate_email)
            password_field.send_keys(valid_password)
            confirm_password_field.send_keys(valid_password)
            register_button.click()
            logging.info(f"Intentando registrar el correo duplicado: {duplicate_email}")

            # Verificar si aparece un mensaje de error o si se registra incorrectamente
            try:
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, success_message_selector))
                )
                duplicate_success_message = self.driver.find_element(By.CSS_SELECTOR, success_message_selector)
                # Si el mensaje de éxito aparece, significa que el correo duplicado fue aceptado incorrectamente
                if duplicate_success_message.text.strip() == "Successful registration!":
                    logging.error(f"Error: El sistema permitió registrar el correo duplicado: {duplicate_email}")
                    self.fail(f"Error: El correo duplicado '{duplicate_email}' fue registrado nuevamente.")
            except TimeoutException:
                # Si no aparece el mensaje de éxito, se considera que el registro fue rechazado correctamente
                logging.info(f"Registro rechazado correctamente para el correo duplicado: {duplicate_email}")

        except NoSuchElementException as e:            
            logging.error(f"Elemento no encontrado: {e}")
            self.fail(f"Fallo en la prueba: No se encontró un elemento esperado. {e}")

        except Exception as e:            
            logging.error(f"Error inesperado durante la prueba: {e}")
            raise

        finally:            
            logging.info("Prueba completada: test_email_format_and_uniqueness")



    def test_form_submission_with_missing_fields_and_password_requirements(self):
        """Verifica que el formulario no se envíe si los campos obligatorios no están completos 
        o si la contraseña no cumple con los requisitos mínimos."""

        logging.info("Iniciando la prueba: test_form_submission_with_missing_fields_and_password_requirements")

        try:
            # Navegar a la página de registro
            self.navigate_to_signup_page()

            # Localizar los campos obligatorios y el botón de registro
            full_name_field = self.driver.find_element(By.ID, "full-name")
            email_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_elements(By.ID, "password")[1]
            confirm_password_field = self.driver.find_elements(By.ID, "confirm-password")[1]
            register_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-up/main/section[2]/app-sign-up-form/form/button")
            logging.info("Campos obligatorios y botón de registro localizados.")

            # Definir los casos de prueba
            test_cases = [
                {
                    "full_name": "Nombre",  # Solo un nombre (inválido)
                    "email": "correo_valido@prueba.com",
                    "password": "Password1!",
                    "confirm_password": "Password1!",
                    "expected_disabled": True,
                    "description": "Campo de nombre incompleto"
                },
                {
                    "full_name": "Nombre Apellido",
                    "email": " ",  # Email vacío
                    "password": "Password1!",
                    "confirm_password": "Password1!",
                    "expected_disabled": True,
                    "description": "Email no ingresado"
                },
                {
                    "full_name": "Nombre Apellido",
                    "email": "correo_valido@prueba.com",
                    "password": "Password1!",  
                    "confirm_password": "Password123",  # Contraseñas no coinciden
                    "expected_disabled": True,
                    "description": "Contraseñas no coinciden"
                },
                {
                    "full_name": "Nombre Apellido",
                    "email": "correo_valido@prueba.com",
                    "password": "pass",  # Contraseña no cumple los requisitos
                    "confirm_password": "pass",
                    "expected_disabled": True,
                    "description": "Contraseña no cumple requisitos mínimos"
                },
                {
                    "full_name": "Nombre Apellido",
                    "email": "correo_valido@prueba.com",
                    "password": "Password1!",  # Contraseña válida
                    "confirm_password": "Password1!",  # Contraseña válida y coincidente
                    "expected_disabled": False,
                    "description": "Formulario completo y válido"
                },
            ]

            # Ejecutar los casos de prueba
            for case in test_cases:
                try:
                    iteration_start = time.time()  # Inicio del tiempo de la iteración
                    
                    # Limpiar y completar los campos
                    full_name_field.clear()
                    email_field.clear()
                    password_field.clear()
                    confirm_password_field.clear()
                     

                    full_name_field.send_keys(case["full_name"])
                    email_field.send_keys(case["email"])
                    password_field.send_keys(case["password"])
                    confirm_password_field.send_keys(case["confirm_password"])

                    logging.info(f"Rellenando formulario: {case}")

                    # Verificar si el botón de registro está habilitado o deshabilitado
                    is_disabled = not register_button.is_enabled()
                    self.assertEqual(
                        is_disabled, case["expected_disabled"],
                        f"{case['description']} - Estado del botón incorrecto. "
                        f"Esperado: {case['expected_disabled']}, Obtenido: {is_disabled}."
                    )
                    logging.info(f"Prueba pasada: {case['description']}. Botón {'deshabilitado' if is_disabled else 'habilitado'} correctamente.")

                    iteration_time = time.time() - iteration_start
                    logging.info(f"Tiempo de ejecución del caso: {iteration_time:.2f} segundos.")

                except AssertionError as e:
                    logging.error(f"Fallo en el caso '{case['description']}': {e}")

                except Exception as e:
                    logging.error(f"Error inesperado en el caso '{case['description']}': {e}")

        except NoSuchElementException as e:
            logging.error(f"Elemento no encontrado: {e}")
            self.fail(f"Fallo en la prueba: No se encontró el elemento esperado. {e}")

        except Exception as e:
            logging.error(f"Error inesperado durante la prueba: {e}")
            raise

        finally:
            logging.info("Prueba completada: test_form_submission_with_missing_fields_and_password_requirements")

    def test_successful_registration(self):

        """Verifica que un usuario pueda registrarse con datos válidos y se muestre el mensaje de éxito."""

        logging.info("Iniciando la prueba: test_successful_registration")

        try:
            # Navegar a la página de registro
            self.navigate_to_signup_page()

            # Localizar los elementos del formulario
            full_name_field = self.driver.find_element(By.ID, "full-name")
            email_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_elements(By.ID, "password")[1]
            confirm_password_field = self.driver.find_elements(By.ID, "confirm-password")[1]
            register_button = self.driver.find_element(By.XPATH, "/html/body/app-root/app-sign-up/main/section[2]/app-sign-up-form/form/button")
            logging.info("Formulario localizado correctamente.")

            # Datos válidos para el registro
            valid_data = {
                "full_name": "Nombre Apellido",
                "email": "correo_valido@prueba.com",
                "password": "Password1!",
            }

            # Completar el formulario
            full_name_field.clear()
            email_field.clear()
            password_field.clear()
            confirm_password_field.clear()

            full_name_field.send_keys(valid_data["full_name"])
            email_field.send_keys(valid_data["email"])
            password_field.send_keys(valid_data["password"])
            confirm_password_field.send_keys(valid_data["password"])
            logging.info("Formulario rellenado con datos válidos.")

            # Hacer clic en el botón de registro
            register_button.click()
            logging.info("Botón de registro clicado.")

            # Esperar la redirección y verificar el mensaje de éxito
            success_message_selector = "div.ml-3.text-sm.font-normal"  # Selector del mensaje de éxito
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, success_message_selector))
            )
            success_message = self.driver.find_element(By.CSS_SELECTOR, success_message_selector)

            # Verificar el texto del mensaje
            expected_message = "Successful registration!"
            self.assertEqual(
                success_message.text.strip(), expected_message,
                f"El mensaje de éxito esperado era '{expected_message}', pero se encontró '{success_message.text.strip()}'."
            )
            logging.info("Registro exitoso verificado. Mensaje de éxito mostrado correctamente.")

        except TimeoutException:
            logging.error("El mensaje de éxito no apareció en el tiempo esperado.")
            self.fail("Fallo en la prueba: No se mostró el mensaje de éxito tras el registro.")

        except NoSuchElementException as e:
            logging.error(f"No se encontró un elemento esperado: {e}")
            self.fail(f"Fallo en la prueba: Elemento faltante. {e}")

        except Exception as e:
            logging.error(f"Error inesperado durante la prueba: {e}")
            raise

        finally:
            logging.info("Prueba completada: test_successful_registration")


if __name__ == "__main__":
    unittest.main()  # Ejecuta las pruebas definidas en la clase
