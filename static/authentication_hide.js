function hidePassword() {
  var x = document.getElementById("password");
  $('#show_password').html('<span class="material-icons">visibility</span >')
  x.type = "password";
}