$(document).ready(function () {
  $('#date').val(new Date().toISOString().slice(0, 10));


  $("#submit-estimate-btn").click(function () {
    var data = {
      'sales_order_date': $("#date").val(),
      'prototype_prefix': $("#prototype-prefix").val(),
      'region': $("#region").val(),
      'panel_vendor': $("#vendor").val(),
      'sqft_wall_panels_int': $("#wall-panel-sqft-int").val(),
      'sqft_wall_panels_ext': $("#wall-panel-sqft-ext").val(),
      'sqft': $("#sqft").val(),
      'algorithm': $("#algorithm").val()
    };

    $.ajax({
      url: "/get-estimate",
      type: "get",
      data: data,
      success: function (response) {
        $("#estimate-output").html(response);
      },
      error: function (xhr) {
        $("#estimate-output").html("ERROR");
        $("#utility-output").html(xhr.response);
      }
    });
  });

  $("#sync-btn").click(function () {
    $.ajax({
      url: "/sync",
      type: "post",
      success: function (response) {
        $("#utility-output").html(response);
      },
      error: function (xhr) {
        $("#utility-output").html(xhr.response)
      }
    });
  });

  $("#delete-projects-btn").click(function () {
    $.ajax({
      url: "/deleteProjects",
      type: "get",
      success: function (response) {
        $("#utility-output").html(response);
      },
      error: function (xhr) {
        $("#utility-output").html(xhr.response)
      }
    });
  });

  $("#delete-lumber-btn").click(function () {
    $.ajax({
      url: "/deleteLumber",
      type: "get",
      success: function (response) {
        $("#utility-output").html(response);
      },
      error: function (xhr) {
        $("#utility-output").html(xhr.response)
      }
    });
  });

  $("#train-btn").click(function () {
    $.ajax({
      url: "/train",
      type: "post",
      success: function (response) {
        $("#utility-output").html(response);
      },
      error: function (xhr) {
        $("#utility-output").html(xhr.response)
      }
    });
  });

});