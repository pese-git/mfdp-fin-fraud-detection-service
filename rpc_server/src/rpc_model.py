from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from typing import Any


class Model:
    """
    Класс для представления модели машинного обучения, использующей RandomForestClassifier
    из библиотеки scikit-learn. Этот класс автоматически создает и обучает
    модель с использованием датасета Iris при создании экземпляра.

    Методы
    -------
    _create_and_train_model() -> RandomForestClassifier
        Статический метод, который загружает датасет Iris, делит его на обучающую и
        тестовую выборки, обучает RandomForestClassifier на обучающей выборке
        и возвращает обученную модель.

    predict(input_data: Any) -> Any
        Метод предсказания, который принимает входные данные и возвращает предсказанные
        метки в виде списка.
    """

    def __init__(self) -> None:
        self.model = self._create_and_train_model()

    @staticmethod
    def _create_and_train_model() -> RandomForestClassifier:
        """
        Загружает датасет Iris, делит его на обучающую и тестовую выборки, обучает
        RandomForestClassifier на обучающей выборке и возвращает обученную модель.

        Возвращает
        -------
        RandomForestClassifier
            Обученная модель RandomForestClassifier.
        """
        data = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(
            data.data, data.target, test_size=0.2
        )
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        return model

    def predict(self, input_data: Any) -> Any:
        """
        Выполняет предсказания с использованием обученной модели RandomForestClassifier.

        Параметры
        ----------
        input_data : Any
            Входные данные, для которых нужно сделать предсказания.
            Это должно быть в формате, который ожидает модель, например,
            двумерный массив или DataFrame значений признаков.

        Возвращает
        -------
        Any
            Предсказанные метки для входных данных в виде списка.
        """
        return self.model.predict(input_data).tolist()
