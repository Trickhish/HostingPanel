import { Component } from '@angular/core';

@Component({
  selector: 'app-login',
  imports: [],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
    resetErr() {
      document.getElementById("err")!.innerHTML = "";
      document.getElementById("err")!.classList.remove("active");
  }

  err(msg:String, type="info") {
      var icon="fa-solid fa-exclamation";

      switch (type) {
          case "error":
              icon="error fa-solid fa-circle-exclamation";
              break;
          case "warning":
              icon="warning fa-solid fa-triangle-exclamation";
              break;
          default:
              icon="info fa-solid fa-exclamation"
      }

      document.getElementById("err")!.innerHTML = '<i class="'+icon+'"></i> '+msg;
      document.getElementById("err")!.classList.add("active");
  }

  showPass() {
      if (document.getElementById("pass")!.getAttribute("type")=="password") {
          document.getElementById("pass")!.setAttribute("type", "text");

          document.getElementById("pass_eye")!.classList.add("fa-eye-slash");
          document.getElementById("pass_eye")!.classList.remove("fa-eye");
      } else {
          document.getElementById("pass")!.setAttribute("type", "password");

          document.getElementById("pass_eye")!.classList.remove("fa-eye-slash");
          document.getElementById("pass_eye")!.classList.add("fa-eye");
      }
  }
}
