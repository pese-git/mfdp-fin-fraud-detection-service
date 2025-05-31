import json
from typing import Any, Optional
from sqlmodel import Session, select

from src.models.model import Model
from src.models.prediction import Prediction
from src.models.task import Task
#from src.models.transaction import Transaction, TransactionType
#from src.models.wallet import Wallet


def predict_processing(
    user_id: int,
    model_name: str,
    input_data: dict[str, Any],
    session: Session,
    callback: Any,
) -> Prediction:
    """
    Обработка запроса на предсказание путем выполнения нескольких операций в рамках транзакции базы данных.

    Параметры:
    - user_id (int): ID пользователя, делающего запрос.
    - model (str): Название модели машинного обучения, используемой для предсказания.
    - input_data (str): Входные данные, на которых должно быть выполнено предсказание.
    - session (Session): Сессия SQLModel, используемая для операций с базой данных.

    Эта функция выполняет следующие шаги:
    1. Получает модель машинного обучения на основе указанного названия модели.
       Выбрасывает исключение, если модель не найдена.
    2. Получает кошелек пользователя по user_id.
       Выбрасывает исключение, если кошелек не найден или если баланс кошелька недостаточен.
    3. Вычитает стоимость предсказания из баланса кошелька пользователя.
    4. Записывает транзакцию в базе данных, представляющую вычитание средств.
    5. Выполняет предсказание (здесь представлено как заглушка, возвращающая "42").
    6. Сохраняет результат предсказания в базе данных.
    7. Создает новую задачу, связанную с предсказанием и моделью, и сохраняет в базе данных.

    Если при выполнении одной из операций возникает ошибка, транзакция базы данных откатывается,
    и выбрасывается исключение с описанием ошибки. Если транзакция завершается успешно без исключений,
    она автоматически фиксируется.
    Возвращает:
    - Prediction: Объект предсказания, содержащий результат и связанную метаданные.

    Выбрасывает:
    - Exception: В случае возникновения ошибки во время обработки, с указанием типа ошибки базы данных.
    """
    try:
        # with session.begin():  # Начинаем транзакцию

        # Получаем ML модель
        model: Optional[Model] = (
            session.query(Model).filter(Model.name == model_name).first()
        )
        if not model:
            raise RuntimeError("Model not found")
        # Получаем кошелек пользователя
        #wallet: Optional[Wallet] = (
        #    session.query(Wallet).filter(Wallet.user_id == user_id).first()
        #)
        #if not wallet:
        #    raise RuntimeError("Wallet not found")
        #if wallet.balance < 10:  # Стоимость предсказания
        #    raise RuntimeError("Insufficient funds")

        #print(f"Wallet: {wallet.balance}")

        # Списываем средства
        #wallet.balance -= 10
        # Создаем запись о транзакции
        #new_transaction = Transaction(
        #    user_id=user_id, amount=-10, transaction_type=TransactionType.EXPENSE
        #)
        #session.add(new_transaction)
        #session.flush()
        #session.refresh(new_transaction)
        # Делаем предсказание (заглушка)
        # result = "42"
        # number = 15
        # print(f" [x] Запрос на вычисление fib({number})")
        # result = rpc.call(number)
        # print(f" [.] Получен ответ: {result}")
        # Вызываем callback с результатом
        result = callback(input_data)
        print(f"RESULT = {result}")
        # Сохраняем предсказание в БД
        prediction = Prediction(
            user_id=user_id,
            input_data=json.dumps(input_data),
            result=json.dumps(result),
        )
        session.add(prediction)
        session.flush()  # Применяем изменения в БД, но не фиксируем
        session.refresh(prediction)  # Обновляем объект из БД
        task = Task(
            prediction=prediction,
            model=model,
            #transaction=new_transaction,
        )
        session.add(task)
        session.flush()  # Применяем изменения в БД, но не фиксируем
        session.refresh(task)  # Обновляем объект из БД
        session.commit()

        # Если код дошел сюда без ошибок, транзакция будет автоматически зафиксирована
        return prediction

    except Exception as e:
        session.rollback()  # Откатываем транзакцию при ошибке
        raise RuntimeError(f"Exception: {e}")
