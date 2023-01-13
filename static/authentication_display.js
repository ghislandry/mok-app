function showPassword() {
  var x = document.getElementById("password");
  if (x.type === "password") {
    $('#show_password').html('<span class="material-icons">visibility_off</span >')
    x.type = "text";
  } else {
    $('#show_password').html('<span class="material-icons">visibility</span >')
    x.type = "password";
  }
}