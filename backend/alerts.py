"""
alerts.py - Sistema de Alertas Multinivel
Gestiona alertas con diferentes niveles de severidad y canales de notificación
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Niveles de severidad de alertas"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class AlertChannel(str, Enum):
    """Canales de notificación disponibles"""
    IN_APP = "in_app"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class AlertCondition(str, Enum):
    """Condiciones que disparan alertas"""
    DEVICE_OFFLINE = "device_offline"
    DEVICE_ONLINE = "device_online"
    HIGH_LATENCY = "high_latency"
    HIGH_PACKET_LOSS = "high_packet_loss"
    NEW_DEVICE = "new_device"
    PORT_CLOSED = "port_closed"
    PORT_OPENED = "port_opened"
    UNAUTHORIZED_DEVICE = "unauthorized_device"


class Alert:
    """Representa una alerta individual"""
    
    def __init__(
        self,
        level: AlertLevel,
        condition: AlertCondition,
        message: str,
        device_id: Optional[int] = None,
        device_name: Optional[str] = None,
        device_ip: Optional[str] = None,
        alert_metadata: Optional[Dict] = None
    ):
        self.id = None  # Se asigna al guardar en BD
        self.level = level
        self.condition = condition
        self.message = message
        self.device_id = device_id
        self.device_name = device_name
        self.device_ip = device_ip
        self.alert_metadata = alert_metadata or {}
        self.timestamp = datetime.utcnow()
        self.acknowledged = False
        self.acknowledged_at = None
        self.acknowledged_by = None

    def to_dict(self):
        """Convierte la alerta a diccionario"""
        return {
            'id': self.id,
            'level': self.level.value,
            'condition': self.condition.value,
            'message': self.message,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_ip': self.device_ip,
            'metadata': self.alert_metadata,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by
        }


class AlertRule:
    """Regla de alerta configurable"""
    
    def __init__(
        self,
        name: str,
        condition: AlertCondition,
        level: AlertLevel,
        channels: List[AlertChannel],
        enabled: bool = True,
        device_id: Optional[int] = None,
        threshold: Optional[float] = None,
        throttle_minutes: int = 5,
        escalate_after_minutes: Optional[int] = None
    ):
        self.id = None
        self.name = name
        self.condition = condition
        self.level = level
        self.channels = channels
        self.enabled = enabled
        self.device_id = device_id  # None = aplica a todos
        self.threshold = threshold  # Para condiciones numéricas
        self.throttle_minutes = throttle_minutes
        self.escalate_after_minutes = escalate_after_minutes
        self.last_triggered = None

    def can_trigger(self) -> bool:
        """Verifica si la regla puede dispararse (throttling)"""
        if not self.enabled:
            return False
        
        if self.last_triggered is None:
            return True
        
        elapsed = datetime.utcnow() - self.last_triggered
        return elapsed.total_seconds() >= (self.throttle_minutes * 60)

    def to_dict(self):
        """Convierte la regla a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'condition': self.condition.value,
            'level': self.level.value,
            'channels': [ch.value for ch in self.channels],
            'enabled': self.enabled,
            'device_id': self.device_id,
            'threshold': self.threshold,
            'throttle_minutes': self.throttle_minutes,
            'escalate_after_minutes': self.escalate_after_minutes,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }


class AlertManager:
    """Gestor principal de alertas"""
    
    def __init__(self, db_session, config: Dict):
        self.db = db_session
        self.config = config
        self.rules: List[AlertRule] = []
        self.active_alerts: List[Alert] = []
        
    def load_rules(self):
        """Carga reglas desde la base de datos"""
        # TODO: Implementar carga desde BD
        # Por ahora, reglas por defecto
        default_rules = [
            AlertRule(
                name="Dispositivo Crítico Offline",
                condition=AlertCondition.DEVICE_OFFLINE,
                level=AlertLevel.CRITICAL,
                channels=[AlertChannel.IN_APP, AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                throttle_minutes=10
            ),
            AlertRule(
                name="Latencia Alta",
                condition=AlertCondition.HIGH_LATENCY,
                level=AlertLevel.WARNING,
                channels=[AlertChannel.IN_APP],
                threshold=100.0,  # ms
                throttle_minutes=15
            ),
            AlertRule(
                name="Nuevo Dispositivo",
                condition=AlertCondition.NEW_DEVICE,
                level=AlertLevel.INFO,
                channels=[AlertChannel.IN_APP, AlertChannel.TELEGRAM],
                throttle_minutes=0
            ),
            AlertRule(
                name="Dispositivo No Autorizado",
                condition=AlertCondition.UNAUTHORIZED_DEVICE,
                level=AlertLevel.CRITICAL,
                channels=[AlertChannel.IN_APP, AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                throttle_minutes=5
            )
        ]
        self.rules = default_rules

    def check_condition(self, condition: AlertCondition, device: Dict, value: Optional[float] = None) -> bool:
        """Verifica si se cumple una condición"""
        if condition == AlertCondition.DEVICE_OFFLINE:
            return device.get('status') == 'Offline'
        
        elif condition == AlertCondition.DEVICE_ONLINE:
            return device.get('status') == 'Online'
        
        elif condition == AlertCondition.HIGH_LATENCY:
            return value is not None and value > 100.0
        
        elif condition == AlertCondition.HIGH_PACKET_LOSS:
            return value is not None and value > 5.0
        
        elif condition == AlertCondition.NEW_DEVICE:
            # Se dispara manualmente al detectar nuevo dispositivo
            return True
        
        elif condition == AlertCondition.UNAUTHORIZED_DEVICE:
            return not device.get('is_authorized', True)
        
        return False

    def create_alert(
        self,
        rule: AlertRule,
        device: Dict,
        custom_message: Optional[str] = None
    ) -> Alert:
        """Crea una nueva alerta"""
        
        # Generar mensaje
        if custom_message:
            message = custom_message
        else:
            message = self._generate_message(rule, device)
        
        alert = Alert(
            level=rule.level,
            condition=rule.condition,
            message=message,
            device_id=device.get('id'),
            device_name=device.get('alias') or device.get('hostname'),
            device_ip=device.get('ip'),
            alert_metadata={
                'rule_id': rule.id,
                'rule_name': rule.name
            }
        )
        
        return alert

    def _generate_message(self, rule: AlertRule, device: Dict) -> str:
        """Genera mensaje de alerta automático"""
        device_name = device.get('alias') or device.get('hostname') or device.get('ip')
        
        messages = {
            AlertCondition.DEVICE_OFFLINE: f"🔴 Dispositivo '{device_name}' está OFFLINE",
            AlertCondition.DEVICE_ONLINE: f"🟢 Dispositivo '{device_name}' está ONLINE",
            AlertCondition.HIGH_LATENCY: f"⚠️ Latencia alta en '{device_name}'",
            AlertCondition.HIGH_PACKET_LOSS: f"⚠️ Pérdida de paquetes alta en '{device_name}'",
            AlertCondition.NEW_DEVICE: f"ℹ️ Nuevo dispositivo detectado: '{device_name}'",
            AlertCondition.UNAUTHORIZED_DEVICE: f"🚨 Dispositivo NO autorizado: '{device_name}'"
        }
        
        return messages.get(rule.condition, f"Alerta: {rule.name}")

    def send_notification(self, alert: Alert, channels: List[AlertChannel]):
        """Envía notificación por los canales especificados"""
        for channel in channels:
            try:
                if channel == AlertChannel.IN_APP:
                    self._send_in_app(alert)
                elif channel == AlertChannel.EMAIL:
                    self._send_email(alert)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook(alert)
            except Exception as e:
                logger.error(f"Error sending alert via {channel}: {e}")

    def _send_in_app(self, alert: Alert):
        """Guarda alerta para mostrar en la app"""
        self.active_alerts.append(alert)
        logger.info(f"In-app alert created: {alert.message}")

    def _send_email(self, alert: Alert):
        """Envía alerta por email"""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled'):
            logger.warning("Email notifications disabled")
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.message}"
            msg['From'] = email_config.get('from_email')
            msg['To'] = email_config.get('to_email')
            
            # Cuerpo del email
            html = f"""
            <html>
                <body>
                    <h2 style="color: {'#dc2626' if alert.level == AlertLevel.CRITICAL else '#f59e0b' if alert.level == AlertLevel.WARNING else '#3b82f6'}">
                        {alert.message}
                    </h2>
                    <p><strong>Nivel:</strong> {alert.level.value.upper()}</p>
                    <p><strong>Condición:</strong> {alert.condition.value}</p>
                    <p><strong>Dispositivo:</strong> {alert.device_name or 'N/A'}</p>
                    <p><strong>IP:</strong> {alert.device_ip or 'N/A'}</p>
                    <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Enviar
            with smtplib.SMTP(email_config.get('smtp_server'), email_config.get('smtp_port', 587)) as server:
                server.starttls()
                server.login(email_config.get('smtp_user'), email_config.get('smtp_password'))
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def _send_telegram(self, alert: Alert, force: bool = False):
        """Envía alerta por Telegram"""
        telegram_config = self.config.get('telegram', {})
        
        if not force and not telegram_config.get('enabled'):
            logger.warning("Telegram notifications disabled")
            return
        
        try:
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            # Emoji según nivel
            emoji = {
                AlertLevel.CRITICAL: "🔴",
                AlertLevel.WARNING: "🟠",
                AlertLevel.INFO: "🔵",
                AlertLevel.DEBUG: "⚪"
            }
            
            message = f"{emoji.get(alert.level, '⚪')} *{alert.level.value.upper()}*\n\n"
            message += f"{alert.message}\n\n"
            message += f"📱 Dispositivo: {alert.device_name or 'N/A'}\n"
            message += f"🌐 IP: {alert.device_ip or 'N/A'}\n"
            message += f"🕐 {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent: {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    def _send_webhook(self, alert: Alert):
        """Envía alerta por webhook"""
        webhook_config = self.config.get('webhook', {})
        
        if not webhook_config.get('enabled'):
            logger.warning("Webhook notifications disabled")
            return
        
        try:
            url = webhook_config.get('url')
            headers = webhook_config.get('headers', {})
            
            payload = {
                'alert': alert.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent: {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")

    def process_device_event(self, event_type: str, device: Dict, value: Optional[float] = None):
        """Procesa un evento de dispositivo y genera alertas si corresponde"""
        
        # Mapear evento a condición
        condition_map = {
            'offline': AlertCondition.DEVICE_OFFLINE,
            'online': AlertCondition.DEVICE_ONLINE,
            'new': AlertCondition.NEW_DEVICE,
            'high_latency': AlertCondition.HIGH_LATENCY,
            'high_packet_loss': AlertCondition.HIGH_PACKET_LOSS,
            'unauthorized': AlertCondition.UNAUTHORIZED_DEVICE
        }
        
        condition = condition_map.get(event_type)
        if not condition:
            return
        
        # Buscar reglas aplicables
        for rule in self.rules:
            if rule.condition != condition:
                continue
            
            # Verificar si aplica al dispositivo
            if rule.device_id and rule.device_id != device.get('id'):
                continue
            
            # Verificar throttling
            if not rule.can_trigger():
                continue
            
            # Verificar condición
            if not self.check_condition(condition, device, value):
                continue
            
            # Crear y enviar alerta
            alert = self.create_alert(rule, device)
            self.send_notification(alert, rule.channels)
            
            # Actualizar última vez disparada
            rule.last_triggered = datetime.utcnow()
            
            logger.info(f"Alert triggered: {rule.name} for device {device.get('ip')}")

    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Dict]:
        """Obtiene alertas activas (no reconocidas)"""
        alerts = [a for a in self.active_alerts if not a.acknowledged]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return [a.to_dict() for a in alerts]

    def acknowledge_alert(self, alert_id: int, user: str = "system"):
        """Marca una alerta como reconocida"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = user
                logger.info(f"Alert {alert_id} acknowledged by {user}")
                return True
        return False

    def clear_old_alerts(self, days: int = 7):
        """Limpia alertas antiguas reconocidas"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.active_alerts = [
            a for a in self.active_alerts
            if not a.acknowledged or a.acknowledged_at > cutoff
        ]
