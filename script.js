async function sendRequest() {
    const submitButton = document.querySelector("#submit-button");
    if (!submitButton) {
        console.error("Элемент #submit-button не найден.");
        return;
    }
    const originalButtonText = submitButton.textContent;

    // Отключаем кнопку отправки и меняем её текст
    submitButton.disabled = true;
    submitButton.textContent = "Отправка...";

    // Собираем данные из формы
    const formData = new FormData();
    formData.append("staff", document.querySelector("#staff").value);
    formData.append("shisha-quality", document.querySelector("input[name='shisha-quality']:checked").value);
    formData.append("staff-quality", document.querySelector("input[name='staff-quality']:checked").value);
    formData.append("venue-quality", document.querySelector("input[name='venue-quality']:checked").value);
    formData.append("feedback", document.querySelector("#feedback").value);
    formData.append("visit-date", document.querySelector("#visit-date").value);

    // Логируем данные, которые отправляются на сервер
    console.log("Отправляемые данные:", formData);

    try {
        const response = await fetch("http://playbox-kazan.online", {
            method: "POST",
            body: formData,
        });

        // Проверка ответа сервера
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Разбираем JSON-ответ
        const data = await response.json();
        if (data.message) {
            alert(data.message);  // Выводим сообщение от сервера
        } else {
            alert("Неизвестная ошибка.");
        }
    } catch (error) {
        // Логируем ошибку, если она произошла
        console.error("Ошибка отправки запроса:", error.message);
        alert("Произошла ошибка. Пожалуйста, попробуйте позже.");
    } finally {
        // Разблокируем кнопку отправки и восстанавливаем исходный текст
        console.log("Разблокировка кнопки...");
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
}
