import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-login',
    imports: [
        FormsModule,
        CommonModule
    ],
    templateUrl: './login.component.html',
    styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
    emailValue = '';
    passwordValue = '';
    isLoading = false;
    returnUrl: string = '/dashboard';

    constructor(
        private authService: AuthService,
        private router: Router,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        // Get return url from route parameters or default to '/dashboard'
        this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';

        // Check if already authenticated
        if (this.authService.isAuthenticatedValue) {
            this.router.navigate([this.returnUrl]);
        }

        document.getElementById("login_form")?.addEventListener("submit", (e) => {
            this.submit();
            e.preventDefault();
        });
    }

    resetErr() {
        document.getElementById("err")!.innerHTML = "";
        document.getElementById("err")!.classList.remove("active");
    }

    err(msg: string, type = "info") {
        let icon = "fa-solid fa-exclamation";

        switch (type) {
            case "error":
                icon = "error fa-solid fa-circle-exclamation";
                break;
            case "warning":
                icon = "warning fa-solid fa-triangle-exclamation";
                break;
            default:
                icon = "info fa-solid fa-exclamation";
        }

        document.getElementById("err")!.innerHTML = '<i class="' + icon + '"></i> ' + msg;
        document.getElementById("err")!.classList.add("active");
    }

    showPass() {
        if (document.getElementById("pass")!.getAttribute("type") == "password") {
            document.getElementById("pass")!.setAttribute("type", "text");

            document.getElementById("pass_eye")!.classList.add("fa-eye-slash");
            document.getElementById("pass_eye")!.classList.remove("fa-eye");
        } else {
            document.getElementById("pass")!.setAttribute("type", "password");

            document.getElementById("pass_eye")!.classList.remove("fa-eye-slash");
            document.getElementById("pass_eye")!.classList.add("fa-eye");
        }
    }

    submit() {
        this.resetErr();

        // Validate inputs
        if (!this.emailValue || !this.passwordValue) {
            this.err('Veuillez remplir tous les champs', 'error');
            return;
        }

        this.isLoading = true;

        // Call auth service
        this.authService.login({
            email: this.emailValue,
            password: this.passwordValue
        }).subscribe({
            next: (response) => {
                this.isLoading = false;
                if (response.success) {
                    // Redirect to the return URL or dashboard
                    this.router.navigate([this.returnUrl]);
                } else {
                    this.err(response.message || 'Erreur de connexion', 'error');
                }
            },
            error: (error) => {
                this.isLoading = false;
                const errorMessage = error.error?.detail || error.error?.message || 'Erreur de connexion. Veuillez réessayer.';
                this.err(errorMessage, 'error');
                console.error('Login failed:', error);
            }
        });
    }
}
