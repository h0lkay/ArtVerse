// Функция для переключения видимости контента
document.addEventListener("DOMContentLoaded", function () {
    const headers = document.querySelectorAll("h2");

    headers.forEach(header => {
        header.addEventListener("click", function () {
            // Находим следующий элемент после заголовка (контент)
            const content = this.nextElementSibling;

            // Переключаем класс 'open' для контента
            content.classList.toggle("open");
        });
    });
});