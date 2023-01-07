function selectRegistrationForm(item) {
  var x = document.getElementById("role_selection");
  if (item.value != "admin") {
    var role = document.getElementById("employee_user_role");
    role.value = item.value
    role.text = item.text
    document.getElementById('register_employee_form').style.display = 'block'
    document.getElementById('text_message').style.display = 'none'
    document.getElementById('text_message_explanation').style.display = 'block'
    document.getElementById('register_admin_form').style.display = 'none'
  } else {
    document.getElementById('register_admin_form').style.display = 'block'
    document.getElementById('register_employee_form').style.display = 'none'
    document.getElementById('text_message_explanation').style.display = 'none'
    document.getElementById('text_message').style.display = 'block'
  }
}