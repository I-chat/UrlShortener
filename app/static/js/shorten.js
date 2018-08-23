$(function () {
  $('button#shorten').on('click', function () {
    var formData = $('#short').serialize();
    $.ajax({
      type: "POST",
      beforeSend: function (request) {
        request.setRequestHeader('Ajax-Test', 'one');
      },
      url: '/shorten',
      data: formData,
      processData: false,
      success: function(data) {
        $('#result').attr("href", data);
        $('#result').attr("value", data);
        $('#result').text(data);
        $('#drop').slideDown("slow");
      },
    });
    return false;
  });
});
new Clipboard('.clip');
$(document).ready(function(){
  $('#drop').slideUp();
});
