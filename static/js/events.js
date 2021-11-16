$("#submit-estimate-btn").click(function(){
    var data = {
    'date': $("#date").val(),
    'prototype-prefix': $("#prototype-prefix").val(),
    'region': $("#region").val(),
    'vendor': $("#vendor").val(),
    'wall-panel-sqft-int': $("#wall-panel-sqft-int").val(),
    'wall-panel-sqft-ext': $("#wall-panel-sqft-ext").val(),
    'sqft': $("#sqft").val(),
    'algorithm': $("#algorithm").val()
    };

    $.ajax({
      url: "/get-estimate",
      type: "get",
      data: data,
      success: function(response) {
        $("#estimate-output").html(response);
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
});