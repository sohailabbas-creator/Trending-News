// Newsletter button
document.getElementById('subBtn').addEventListener('click', function () {
  var email = document.getElementById('emailInput').value;
  if (email && email.includes('@')) {
    document.getElementById('subOk').style.display = 'block';
    this.style.display = 'none';
    document.getElementById('emailInput').style.display = 'none';
  } else {
    document.getElementById('emailInput').style.borderColor = 'red';
  }
});
