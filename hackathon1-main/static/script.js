window.onload = function() {
    var forms = document.getElementsByTagName('form');
    for (var i = 0; i < forms.length; i++) {
        forms[i].addEventListener('submit', function(event) {
            event.preventDefault();
            // Здесь вы можете добавить код для обработки формы
            var comment = document.getElementById('comment').value;
            localStorage.setItem('comment', comment);

            // Получите файл из формы
            var file = document.getElementById('audio').files[0];
            // Добавьте файл в div
            var uploadedFiles = document.getElementById('uploadedFiles');
            uploadedFiles.innerHTML += '<p>' + file.name + '</p>';
        });
    }
    // Загрузите сохраненные данные из LocalStorage
    var savedComment = localStorage.getItem('comment');
    if (savedComment) {
        document.getElementById('comment').value = savedComment;
    }
};
