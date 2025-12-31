package com.timeweaver.notification.listener;

import com.timeweaver.notification.config.RabbitConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class NotificationListener {
    private static final Logger log = LoggerFactory.getLogger(NotificationListener.class);

    @RabbitListener(queues = RabbitConfig.NOTIFICATIONS_QUEUE)
    public void onNotification(@Payload Map<String, Object> payload) {
        // Pour l'instant, on logge simplement; plus tard: email/websocket
        log.info("Notification reçue: {}", payload);
    }
}
