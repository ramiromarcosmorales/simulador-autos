document.addEventListener('DOMContentLoaded', function () {

    // pestañas del formulario
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            tabButtons.forEach(function (b) { b.classList.remove('active'); });
            tabPanels.forEach(function (p) { p.classList.remove('active'); });

            btn.classList.add('active');
            var targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // selección de auto desde las cards
    const botonesAuto = document.querySelectorAll('.btn-seleccionar-auto');
    const selectModelo = document.getElementById('selectModelo');

    botonesAuto.forEach(function (boton) {
        boton.addEventListener('click', function () {
            document.querySelectorAll('.card-modelo').forEach(function (card) {
                card.classList.remove('card-seleccionada');
            });
            botonesAuto.forEach(function (btn) {
                btn.classList.remove('btn-seleccionado');
                btn.innerText = 'Seleccionar';
            });

            var cardPadre = this.closest('.card-modelo');
            cardPadre.classList.add('card-seleccionada');
            this.classList.add('btn-seleccionado');
            this.innerText = 'Seleccionado';

            // sincronizo la card con el select del formulario
            var nombreAuto = this.getAttribute('data-auto');
            if (selectModelo) {
                selectModelo.value = nombreAuto;
            }
        });
    });



    // envío del formulario por AJAX
    var form = document.getElementById('formSimulador');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        limpiarErrores();
        ocultarMensajeExito();

        var errores = validarFormulario();
        if (Object.keys(errores).length > 0) {
            mostrarErrores(errores);
            return;
        }

        var formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
        })
        .then(function (response) {
            return response.json().then(function (data) {
                return { status: response.status, body: data };
            });
        })
        .then(function (result) {
            var data = result.body;

            if (data.status === 'ok') {
                mostrarMensajeExito();
                actualizarInforme(data.informe);
            } else if (data.status === 'error') {
                mostrarErrores(data.errores);
            }
        })
        .catch(function (error) {
            console.error('Error en la petición:', error);
        });
    });

    function obtenerCuotaJS(planName) {
        var PRECIO_BASE = 8500000;
        var CUOTAS = 84;
        var TASA_ANUAL = 14.50;
        var porcentajeFinanciado = 0.70;
        if (planName === 'Plan 70/30') {
            porcentajeFinanciado = 0.70;
        } else if (planName === 'Plan 60/40') {
            porcentajeFinanciado = 0.60;
        } else if (planName === 'Plan 100%') {
            porcentajeFinanciado = 1.0;
        }
        
        var montoFinanciado = PRECIO_BASE * porcentajeFinanciado;
        var tasaMensual = (TASA_ANUAL / 100) / 12;
        var cuotaMensual = 0;
        if (tasaMensual > 0) {
            cuotaMensual = (montoFinanciado * tasaMensual) / (1 - Math.pow(1 + tasaMensual, -CUOTAS));
        } else {
            cuotaMensual = montoFinanciado / CUOTAS;
        }
        return cuotaMensual;
    }

    // valido todos los campos antes de enviar
    function validarFormulario() {
        var errores = {};

        var nombre = form.querySelector('[name="nombre"]').value.trim();
        var email = form.querySelector('[name="email"]').value.trim();
        var dni = form.querySelector('[name="dni"]').value.trim();
        var telefono = form.querySelector('[name="telefono"]').value.trim();
        var fechaNacimiento = form.querySelector('[name="fecha_nacimiento"]').value;
        var nombreGarante = form.querySelector('[name="nombre_garante"]').value.trim();
        var fechaNacimientoGarante = form.querySelector('[name="fecha_nacimiento_garante"]').value;
        var ingresosGarante = form.querySelector('[name="ingresos_garante"]').value.trim();
        var modelo = form.querySelector('[name="modelo"]').value;
        var plan = form.querySelector('[name="plan"]').value;

        if (!nombre) errores.nombre = 'Este campo es obligatorio.';

        if (!email) {
            errores.email = 'Este campo es obligatorio.';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            errores.email = 'Ingresá un email válido.';
        }

        if (!dni) {
            errores.dni = 'Este campo es obligatorio.';
        } else if (!/^\d+$/.test(dni)) {
            errores.dni = 'El DNI debe contener solo números.';
        }

        if (!telefono) errores.telefono = 'Este campo es obligatorio.';

        if (!fechaNacimiento) {
            errores.fecha_nacimiento = 'Este campo es obligatorio.';
        } else {
            var birthDate = new Date(fechaNacimiento);
            var today = new Date();
            var age = today.getFullYear() - birthDate.getFullYear();
            var m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            if (age < 18) {
                errores.fecha_nacimiento = 'El usuario debe ser mayor de 18 años.';
            }
        }

        if (!nombreGarante) errores.nombre_garante = 'Este campo es obligatorio.';

        if (!fechaNacimientoGarante) {
            errores.fecha_nacimiento_garante = 'Este campo es obligatorio.';
        } else {
            var birthDateG = new Date(fechaNacimientoGarante);
            var today = new Date();
            var ageG = today.getFullYear() - birthDateG.getFullYear();
            var mG = today.getMonth() - birthDateG.getMonth();
            if (mG < 0 || (mG === 0 && today.getDate() < birthDateG.getDate())) {
                ageG--;
            }
            if (ageG < 18) {
                errores.fecha_nacimiento_garante = 'El garante debe ser mayor de 18 años.';
            }
        }

        if (!ingresosGarante) {
            errores.ingresos_garante = 'Este campo es obligatorio.';
        } else if (plan) {
            var cuota = obtenerCuotaJS(plan);
            var ingresoMinimo = cuota * 4;
            if (Number(ingresosGarante) < ingresoMinimo) {
                errores.ingresos_garante = 'Ingreso insuficiente. Mínimo requerido: $' + ingresoMinimo.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '.';
            }
        }

        if (!modelo) errores.modelo = 'Seleccioná un vehículo.';
        if (!plan) errores.plan = 'Seleccioná un plan.';

        return errores;
    }

    function mostrarErrores(errores) {
        for (var campo in errores) {
            var errorDiv = document.getElementById('error-' + campo);
            if (errorDiv) {
                errorDiv.textContent = errores[campo];
                errorDiv.style.display = 'block';
            }
            var input = form.querySelector('[name="' + campo + '"]');
            if (input) input.classList.add('is-invalid');
        }

        // navego a la pestaña donde está el primer error
        var primerCampo = Object.keys(errores)[0];
        var inputError = form.querySelector('[name="' + primerCampo + '"]');
        if (inputError) {
            var panel = inputError.closest('.tab-panel');
            if (panel && !panel.classList.contains('active')) {
                var tabId = panel.id;
                tabButtons.forEach(function (b) { b.classList.remove('active'); });
                tabPanels.forEach(function (p) { p.classList.remove('active'); });
                panel.classList.add('active');
                var btnTab = document.querySelector('[data-tab="' + tabId + '"]');
                if (btnTab) btnTab.classList.add('active');
            }
        }
    }

    function limpiarErrores() {
        document.querySelectorAll('.error-msg').forEach(function (el) {
            el.textContent = '';
            el.style.display = 'none';
        });
        form.querySelectorAll('.is-invalid').forEach(function (el) {
            el.classList.remove('is-invalid');
        });
    }

    function mostrarMensajeExito() {
        var msg = document.getElementById('mensajeExito');
        if (msg) {
            msg.classList.remove('d-none');
            setTimeout(function () { msg.classList.add('d-none'); }, 5000);
        }
    }

    function ocultarMensajeExito() {
        var msg = document.getElementById('mensajeExito');
        if (msg) msg.classList.add('d-none');
    }

    // actualizo el panel de informe con los datos del JSON
    function actualizarInforme(informe) {
        document.getElementById('inf-modelo').textContent = informe.modelo;
        document.getElementById('inf-precio').textContent = '$ ' + informe.precio;
        document.getElementById('inf-plan').textContent = informe.plan;
        document.getElementById('inf-cuotas').textContent = informe.cuotas;
        document.getElementById('inf-adjudicacion').textContent = '$ ' + informe.adjudicacion;
        document.getElementById('inf-retiro').textContent = '$ ' + informe.retiro;
        document.getElementById('inf-tasa').textContent = informe.tasa + '% anual';
        document.getElementById('inf-cuota').textContent = '$ ' + informe.cuota_mensual;
        document.getElementById('inf-cuota').classList.remove('text-muted');

        var imgBase = form.getAttribute('data-img-base');
        var imgContainer = document.getElementById('informeImgContainer');
        var imgEl = document.getElementById('informeImg');
        if (imgContainer && imgEl) {
            imgEl.src = imgBase + informe.imagen;
            imgEl.alt = informe.modelo;
            imgContainer.style.display = 'block';
        }

        document.querySelectorAll('.sidebar-informe .fw-bold.text-muted').forEach(function (el) {
            el.classList.remove('text-muted');
        });
    }

    // cotización del dólar en el campo de ingresos del garante
    var campoIngresos = form.querySelector('[name="ingresos_garante"]');
    var dolarTimer = null;

    if (campoIngresos) {
        var dolarInfo = document.createElement('small');
        dolarInfo.className = 'dolar-equivalencia';
        dolarInfo.style.display = 'none';
        campoIngresos.parentNode.appendChild(dolarInfo);

        // debounce de 800ms al escribir
        campoIngresos.addEventListener('input', function () {
            clearTimeout(dolarTimer);
            var valor = campoIngresos.value.trim();
            if (!valor || isNaN(valor) || Number(valor) <= 0) {
                dolarInfo.style.display = 'none';
                return;
            }
            dolarTimer = setTimeout(function () {
                consultarDolar(Number(valor));
            }, 800);
        });

        // inmediato al salir del campo
        campoIngresos.addEventListener('blur', function () {
            clearTimeout(dolarTimer);
            var valor = campoIngresos.value.trim();
            if (!valor || isNaN(valor) || Number(valor) <= 0) {
                dolarInfo.style.display = 'none';
                return;
            }
            consultarDolar(Number(valor));
        });

        function consultarDolar(montoPesos) {
            fetch('/api/dolar/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(function (response) {
                if (!response.ok) throw new Error('API no disponible');
                return response.json();
            })
            .then(function (data) {
                if (data.venta && data.venta > 0) {
                    var equivalencia = (montoPesos / data.venta).toFixed(2);
                    var cotizacion = data.venta.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                    dolarInfo.textContent = 'Este importe equivale a ' + equivalencia + ' dólares bajo la cotización del dólar oficial del día ($' + cotizacion + ').';
                    dolarInfo.style.display = 'block';
                }
            })
            .catch(function () {
                dolarInfo.textContent = 'No se pudo obtener la cotización del dólar.';
                dolarInfo.style.display = 'block';
            });
        }
    }

});
