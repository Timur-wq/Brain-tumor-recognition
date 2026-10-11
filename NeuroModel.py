import os
from contextlib import contextmanager

import requests

from roboflow import Roboflow


@contextmanager
def _roboflow_request_timeout(timeout):
   original_request = requests.sessions.Session.request

   def request_with_timeout(session, *args, **kwargs):
      if kwargs.get("timeout") is None:
         kwargs["timeout"] = timeout
      return original_request(session, *args, **kwargs)

   requests.sessions.Session.request = request_with_timeout
   try:
      yield
   finally:
      requests.sessions.Session.request = original_request


class NeuroModel:
   def __init__(self):
      self.model = None

   def getModel(self):
      api_key = os.getenv("ROBOFLOW_API_KEY")
      if not api_key:
         raise RuntimeError("Укажите ROBOFLOW_API_KEY в файле .env")

      try:
         with _roboflow_request_timeout((8, 20)):
            rf_mod = Roboflow(api_key=api_key)
            project = rf_mod.workspace("tim-xqpez").project("brain_tumor_mri")
            self.model = project.version(1).model
      except requests.Timeout as error:
         raise RuntimeError(
            "Roboflow не ответил за отведенное время. Проверьте интернет и доступ к workspace/project."
         ) from error
      except requests.ConnectionError as error:
         raise RuntimeError(
            "Не удалось подключиться к Roboflow. Проверьте интернет, firewall и доступ к workspace/project."
         ) from error
      except requests.HTTPError as error:
         raise RuntimeError(self._http_error_message(error)) from None

   def analyse(self, img):
      if self.model is None:
         raise RuntimeError("Модель еще не загружена")

      try:
         with _roboflow_request_timeout((8, 60)):
            predictions = self.model.predict(img, confidence=40, overlap=30).json()["predictions"]
      except requests.Timeout as error:
         raise RuntimeError(
            "Roboflow не завершил анализ за 60 секунд. Проверьте соединение и попробуйте еще раз."
         ) from error
      except requests.ConnectionError as error:
         raise RuntimeError("Не удалось подключиться к Roboflow для анализа снимка.") from error
      except requests.HTTPError as error:
         raise RuntimeError(self._http_error_message(error)) from None

      tumor_predictions = [
         prediction
         for prediction in predictions
         if prediction.get("class", "").casefold() == "braintumor"
      ]
      confidence = max(
         (prediction.get("confidence", 0) for prediction in tumor_predictions),
         default=None,
      )
      return {
         "has_tumor": bool(tumor_predictions),
         "confidence": confidence,
      }

   @staticmethod
   def _http_error_message(error):
      response = getattr(error, "response", None)
      status_code = getattr(response, "status_code", None)
      if status_code in {401, 403}:
         return (
            f"Roboflow отклонил запрос (HTTP {status_code}). Проверьте API-ключ и права на inference. "
            "Если ключ уже показывался в сообщении об ошибке, отзовите его и создайте новый."
         )
      if status_code == 404:
         return "Roboflow не нашел endpoint модели. Проверьте workspace, project и опубликованную версию."
      if status_code == 429:
         return "Roboflow временно ограничил число запросов. Попробуйте позже."
      if status_code:
         return f"Roboflow ответил ошибкой HTTP {status_code}."
      return "Roboflow не смог обработать запрос. Проверьте настройки модели и попробуйте снова."

   