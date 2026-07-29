	// Script para el registro del usuario
			const userIcon = document.querySelector('.container-user ion-icon[name="people-outline"]');
			const popup = document.getElementById("loginPopup");
			const closeBtn = document.querySelector(".close-btn");

			if (userIcon && popup) {
    			userIcon.onclick = () => popup.style.display = "flex";
			}

			if (closeBtn && popup) {
    			closeBtn.onclick = () => popup.style.display = "none";
			}

			window.onclick = (e) => {
				if (e.target === popup) popup.style.display = "none";
			};

			const loginPopup = document.getElementById("loginPopup");
			const registerPopup = document.getElementById("registerPopup");

			const userIcon2 = document.querySelector('.container-user ion-icon[name="people-outline"]');
			const closeLogin = document.querySelector(".close-btn");
			const closeRegister = document.querySelector(".close-register");

			const goRegister = document.querySelector(".signup-text a");
			const goLogin = document.getElementById("goLogin");

			// Abrir login
			if (userIcon2 && loginPopup) {
    			userIcon2.onclick = () => loginPopup.style.display = "flex";
			}

			// Cerrar login
			if (closeLogin && loginPopup) {
    			closeLogin.onclick = () => loginPopup.style.display = "none";
			}

			// Cerrar registro
			if (closeRegister && registerPopup) {
    			closeRegister.onclick = () => registerPopup.style.display = "none";
			}

			// Ir de login → registro
			if (goRegister) {
    			goRegister.onclick = (e) => {
        			e.preventDefault();
        			loginPopup.style.display = "none";
        			registerPopup.style.display = "flex";
    			};
			}

			if (goLogin) {
    			goLogin.onclick = (e) => {
       				 e.preventDefault();
        			registerPopup.style.display = "none";
        			loginPopup.style.display = "flex";
    			};
			}

			// Cerrar si hacen clic afuera
			window.onclick = (e) => {
				if (e.target === loginPopup) loginPopup.style.display = "none";
				if (e.target === registerPopup) registerPopup.style.display = "none";
			};
			const btnMenu = document.getElementById("btn-menu");
			const navMenu = document.getElementById("navMenu");

				if (btnMenu && navMenu) {
    				btnMenu.onclick = () => {
        				navMenu.classList.toggle("active");
    				};
				}


 