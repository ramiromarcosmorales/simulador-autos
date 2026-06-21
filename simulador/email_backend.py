import ssl
from django.core.mail.backends.smtp import EmailBackend


class SSLEmailBackend(EmailBackend):
    # backend personalizado para conectar con servidores SMTP que usan
    # certificados SSL no reconocidos por Python (ej: hosting compartido Ferozo)

    def open(self):
        if self.connection:
            return False

        import smtplib
        import socket

        connection_params = {'local_hostname': socket.getfqdn()}
        connection_params['timeout'] = self.timeout if self.timeout is not None else 5

        # contexto SSL sin verificación de certificado
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            if self.use_ssl:
                connection_params['context'] = ssl_context
                self.connection = smtplib.SMTP_SSL(
                    self.host, self.port, **connection_params
                )
            else:
                self.connection = smtplib.SMTP(
                    self.host, self.port, **connection_params
                )
                if self.use_tls:
                    self.connection.starttls(context=ssl_context)

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception:
            return False
