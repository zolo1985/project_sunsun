$(window).ready(function () {
  $(".loader-wrapper").fadeOut("slow");
});

$(document).ready(function () {
  if (window.history && window.history.pushState) {
    $(window).on("popstate", function () {
      $(".loader-wrapper").fadeOut("slow");
    });
  }
});

$(function () {
  // this will get the full URL at the address bar
  var url = window.location.href;
  // passes on every "a" tag
  $(".navbar-nav a").each(function () {
    // checks if its the same on the address bar
    if (url == this.href) {
      $(this).closest("li").addClass("active");
      //for making parent of submenu active
      $(this).closest("li").parent().parent().addClass("active");
    }
  });
});

function togglePassword1() {
  var type = document.getElementById("password").type;
  if (type == "password") {
    document.getElementById("password").type = "text";
  } else {
    document.getElementById("password").type = "password";
  }
}

function togglePassword() {
  var type = document.getElementById("password").type;
  if (type == "password") {
    document.getElementById("password").type = "text";
    document.getElementById("confirm_password").type = "text";
  } else {
    document.getElementById("password").type = "password";
    document.getElementById("confirm_password").type = "password";
  }
}

// $('img').load(function(){
//     $(this).css('background','none');
//  });

$("document").ready(function () {
  $("#image").change(function () {
    if (this.files && this.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $("#renderImage").attr("src", e.target.result);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });
});

function mustSignInAlert() {
  alert("Хэрэглэгч нэвтрэх шаардлагатай!");
}
