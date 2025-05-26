$(document).ready(function() {
    $('form').on('submit', function(e) {
        const fileInput = $('input[type="file"]');
        if (fileInput[0].files[0].type !== 'text/xml') {
            alert('Apenas arquivos XML são permitidos!');
            e.preventDefault();
        }
    });
});